"""
LLM客户端封装（支持阿里千问，线程安全）
"""
import json
import time
import threading
import os
from typing import Optional, Callable, Dict, Any, Iterator
import httpx
from inv_graph.config import (
    LLM_PROVIDER,
    QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL,
    FASTGPT_API_KEY, FASTGPT_BASE_URL, FASTGPT_MODEL,
    DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
)

# 调试模式：通过环境变量 DEBUG_FASTGPT_STREAM 控制
DEBUG_FASTGPT_STREAM = os.getenv("DEBUG_FASTGPT_STREAM", "false").lower() == "true"


# ==================== 辅助函数 ====================

def _extract_content_from_choices(choice: Dict[str, Any]) -> str:
    """从 choice 对象中提取内容，支持多种格式"""
    content = ''
    
    # 优先从 delta.content 提取（流式格式）
    if 'delta' in choice:
        delta = choice.get('delta', {})
        content = delta.get('content', '')
    
    # 如果没有 delta，尝试从 message.content 提取
    if not content and 'message' in choice:
        message = choice.get('message', {})
        content = message.get('content', '')
    
    # 如果还没有，尝试直接从 choice 中提取
    if not content:
        content = choice.get('content', '')
    
    return content


def _extract_content_from_response(result: Dict[str, Any]) -> str:
    """从非流式响应中提取内容，支持多种格式"""
    content: str = ""
    
    # 1. OpenAI 兼容格式
    if isinstance(result, dict) and "choices" in result and result["choices"]:
        content = (
            result["choices"][0]
            .get("message", {})
            .get("content", "")
        ) or result["choices"][0].get("text", "")
    
    # 2. FastGPT 常见格式：data.answer 或 data.content
    if not content and isinstance(result, dict) and "data" in result:
        data = result["data"]
        if isinstance(data, dict):
            content = (
                data.get("answer")
                or data.get("content")
                or ""
            )
    
    # 3. 顶层 answer/content
    if not content and isinstance(result, dict):
        content = result.get("answer") or result.get("content") or ""
    
    return content


def _parse_sse_data_line(line: str) -> Optional[str]:
    """解析 SSE 格式的 data 行，返回数据字符串（去掉前缀）"""
    if line.startswith("data: "):
        return line[6:]  # 去掉 "data: " 前缀
    elif line.startswith("data:"):
        return line[5:]  # 去掉 "data:" 前缀（无空格情况）
    return None


def _check_stream_response_status(response: httpx.Response, api_name: str = "API") -> None:
    """检查流式响应的状态码，如果非 200 则抛出异常"""
    if response.status_code != 200:
        raise httpx.HTTPStatusError(
            f"{api_name}调用失败: {response.status_code}",
            request=response.request,
            response=response
        )


def _handle_http_error(e: httpx.HTTPStatusError, api_name: str = "API") -> Exception:
    """处理 HTTP 错误，返回友好的异常信息"""
    error_detail = ""
    try:
        error_detail = e.response.json()
    except Exception:
        error_detail = e.response.text

    if e.response.status_code == 429:
        return Exception(f"{api_name} 限流，请稍后重试。详情: {error_detail}")
    elif e.response.status_code == 401:
        return Exception(f"{api_name} Key 无效。详情: {error_detail}")
    else:
        return Exception(f"{api_name}调用失败: HTTP {e.response.status_code}, 详情: {error_detail}")


def _handle_stream_http_error(e: httpx.HTTPStatusError, api_name: str = "API") -> Exception:
    """处理流式响应的 HTTP 错误"""
    error_detail = ""
    try:
        # 尝试读取错误响应体
        if hasattr(e.response, 'read'):
            try:
                error_text = e.response.read().decode('utf-8')
                try:
                    error_detail = json.loads(error_text)
                except:
                    error_detail = error_text
            except:
                error_detail = f"无法读取错误响应体"
        else:
            error_detail = str(e.response)
    except Exception as ex:
        error_detail = f"解析错误信息失败: {str(ex)}"

    if e.response.status_code == 429:
        return Exception(f"{api_name} 限流，请稍后重试。详情: {error_detail}")
    elif e.response.status_code == 401:
        return Exception(f"{api_name} Key 无效。详情: {error_detail}")
    else:
        return Exception(f"{api_name}调用失败: HTTP {e.response.status_code}, 详情: {error_detail}")


def _process_stream_data(
    data: Dict[str, Any],
    debug_prefix: str = "FastGPT Stream"
) -> tuple[Optional[str], Optional[str], bool]:
    """
    处理流式响应的 JSON 数据，提取内容和 finish_reason
    
    返回: (content, finish_reason, should_break)
    """
    if 'choices' not in data or len(data['choices']) == 0:
        if DEBUG_FASTGPT_STREAM:
            print(f"[DEBUG {debug_prefix}] No 'choices' in data or choices is empty. Full data: {json.dumps(data, ensure_ascii=False)[:200]}", flush=True)
        return None, None, False
    
    choice = data['choices'][0]
    content = _extract_content_from_choices(choice)
    
    if DEBUG_FASTGPT_STREAM:
        print(f"[DEBUG {debug_prefix}] Content extracted: '{content[:50]}...' (length: {len(content)})", flush=True)
        if not content:
            print(f"[DEBUG {debug_prefix}] Full choice data: {json.dumps(choice, ensure_ascii=False)[:200]}", flush=True)
    
    finish_reason = choice.get('finish_reason')
    should_break = finish_reason is not None
    
    if should_break and DEBUG_FASTGPT_STREAM:
        print(f"[DEBUG {debug_prefix}] Finish reason: {finish_reason}, breaking", flush=True)
    
    return content, finish_reason, should_break


def _update_usage_stats(
    stats: Dict[str, Any],
    lock: threading.Lock,
    usage_data: Optional[Dict[str, Any]] = None,
    increment_requests: bool = True
) -> None:
    """线程安全地更新使用统计"""
    if usage_data:
        with lock:
            stats['total_tokens'] += usage_data.get('total_tokens', 0)
            stats['prompt_tokens'] += usage_data.get('prompt_tokens', 0)
            stats['completion_tokens'] += usage_data.get('completion_tokens', 0)
    
    if increment_requests:
        with lock:
            stats['total_requests'] += 1


# ==================== LLMClient 类 ====================

class LLMClient:
    """大模型客户端统一接口"""
    
    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        :param provider: 提供商 ('qwen' 或 'fastgpt')，默认从 LLM_PROVIDER 环境变量读取
        :param api_key: API密钥
        :param model: 模型名称
        """
        self.provider = (provider or LLM_PROVIDER or "qwen").lower()
        
        if self.provider == "qwen":
          self.api_key = api_key or QWEN_API_KEY
          self.model = model or QWEN_MODEL
          self.base_url = QWEN_BASE_URL
        elif self.provider == "fastgpt":
          self.api_key = api_key or FASTGPT_API_KEY
          self.model = model or FASTGPT_MODEL
          self.base_url = FASTGPT_BASE_URL
        else:
          raise ValueError(f"不支持的provider: {self.provider}")
        
        if not self.api_key:
            raise ValueError("API密钥未设置，请检查对应的环境变量（如 QWEN_API_KEY 或 FASTGPT_API_KEY）")
        self.usage_stats = {
            'total_tokens': 0,
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_requests': 0
        }
        self._stats_lock = threading.Lock()  # 保护usage_stats的线程锁
    
    def generate(self, prompt: str, temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = DEFAULT_MAX_TOKENS, **kwargs) -> str:
        """
        生成文本
        :param prompt: 输入的Prompt
        :param temperature: 温度参数
        :param max_tokens: 最大token数
        :param kwargs: 其他参数
        :return: 模型返回的文本
        """
        if self.provider == "qwen":
            return self._generate_qwen(prompt, temperature, max_tokens, **kwargs)
        if self.provider == "fastgpt":
            return self._generate_fastgpt(prompt, temperature, max_tokens, **kwargs)
        raise ValueError(f"不支持的provider: {self.provider}")
    
    def _generate_qwen(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> str:
        """调用阿里千问API（兼容OpenAI格式）"""
        url = f"{self.base_url}/chat/completions"
        return self._generate_openai_compatible(url, prompt, temperature, max_tokens, **kwargs)

    def _build_fastgpt_payload(
        self,
        prompt: str,
        stream: bool,
        kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构建 FastGPT 请求 payload"""
        # 提取 FastGPT 特定参数
        chat_id = kwargs.pop("chat_id", None)
        response_chat_item_id = kwargs.pop("response_chat_item_id", None)
        variables = kwargs.pop("variables", None)
        detail = kwargs.pop("detail", False)
        custom_uid = kwargs.pop("custom_uid", None)

        payload: Dict[str, Any] = {
            "stream": stream,
            "detail": detail,
            "messages": [
                {
                    "content": prompt,
                    "role": "user"
                }
            ]
        }
        
        if chat_id is not None:
            payload["chatId"] = chat_id
        
        if response_chat_item_id:
            payload["responseChatItemId"] = response_chat_item_id
        
        if variables:
            payload["variables"] = variables
        
        if custom_uid:
            payload["customUid"] = custom_uid
        
        return payload

    def _generate_fastgpt(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> str:
        """调用 FastGPT OpenAPI /v1/chat/completions 接口，参考官方文档。
        
        文档: https://doc.fastgpt.io/docs/introduction/development/openapi/chat
        
        支持的 kwargs 参数：
        - chat_id: 对话ID，用于上下文管理（可选）
        - response_chat_item_id: 响应消息ID（可选）
        - variables: 模块变量，用于替换模块中输入框内容里的 [key]（可选）
        - detail: 是否返回中间值（默认 False）
        - custom_uid: 自定义用户ID（可选，文档未提及，保留兼容性）
        """
        base = self.base_url.rstrip("/")
        url = f"{base}/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = self._build_fastgpt_payload(prompt, stream=False, kwargs=kwargs.copy())

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                result = response.json()
                content = _extract_content_from_response(result)

                if content:
                    _update_usage_stats(self.usage_stats, self._stats_lock, increment_requests=True)
                    return content

                raise ValueError(f"FastGPT API返回格式无法解析: {result}")

        except httpx.HTTPStatusError as e:
            raise _handle_http_error(e, "FastGPT API") from e
        except httpx.RequestError as e:
            raise Exception(f"FastGPT 网络请求失败: {str(e)}") from e

    def _process_fastgpt_stream_line(
        self,
        line: str,
        line_num: int,
        chunks_yielded: int,
        usage_data: Optional[Dict[str, Any]],
        stream_callback: Optional[Callable[[str], None]]
    ) -> tuple[Optional[str], Optional[Dict[str, Any]], int, bool]:
        """
        处理 FastGPT 流式响应的一行数据
        
        返回: (content, usage_data, new_chunks_yielded, should_break)
        """
        if not line.strip():
            return None, usage_data, chunks_yielded, False
        
        if DEBUG_FASTGPT_STREAM:
            print(f"[DEBUG FastGPT Stream] Line {line_num}: {line[:100]}...", flush=True)
        
        data_str = _parse_sse_data_line(line)
        
        if data_str is not None:
            data_str = data_str.strip()
            if data_str == "[DONE]":
                if DEBUG_FASTGPT_STREAM:
                    print(f"[DEBUG FastGPT Stream] Received [DONE] marker", flush=True)
                return None, usage_data, chunks_yielded, True
            
            if not data_str:
                return None, usage_data, chunks_yielded, False
            
            try:
                data = json.loads(data_str)
                
                if DEBUG_FASTGPT_STREAM:
                    print(f"[DEBUG FastGPT Stream] Parsed JSON keys: {list(data.keys())}", flush=True)
                
                content, finish_reason, should_break = _process_stream_data(data, "FastGPT Stream")
                
                if content:
                    chunks_yielded += 1
                    if stream_callback:
                        stream_callback(content)
                    if DEBUG_FASTGPT_STREAM:
                        print(f"[DEBUG FastGPT Stream] Yielding chunk #{chunks_yielded}: '{content[:50]}...' (length: {len(content)})", flush=True)
                elif DEBUG_FASTGPT_STREAM:
                    print(f"[DEBUG FastGPT Stream] Empty content, skipping yield", flush=True)
                
                # 提取 usage 信息
                if 'usage' in data:
                    usage_data = data['usage']
                
                return content, usage_data, chunks_yielded, should_break
                
            except json.JSONDecodeError as e:
                if DEBUG_FASTGPT_STREAM:
                    print(f"[DEBUG FastGPT Stream] JSON decode error: {e}, data_str: {data_str[:100]}", flush=True)
                return None, usage_data, chunks_yielded, False
        
        elif line.startswith("event: "):
            if DEBUG_FASTGPT_STREAM:
                print(f"[DEBUG FastGPT Stream] Event line: {line}", flush=True)
            return None, usage_data, chunks_yielded, False
        elif DEBUG_FASTGPT_STREAM:
            print(f"[DEBUG FastGPT Stream] Unknown line format: {line[:100]}", flush=True)
        
        return None, usage_data, chunks_yielded, False

    def _generate_fastgpt_stream(
        self, 
        prompt: str, 
        temperature: float, 
        max_tokens: int,
        stream_callback: Optional[Callable[[str], None]],
        **kwargs
    ) -> Iterator[str]:
        """流式调用 FastGPT OpenAPI /v1/chat/completions 接口
        
        文档: https://doc.fastgpt.io/docs/introduction/development/openapi/chat
        流式响应格式: data: {"id":"","object":"","created":0,"choices":[{"delta":{"content":"..."},"index":0,"finish_reason":null}]}
        
        支持的 kwargs 参数：
        - chat_id: 对话ID，用于上下文管理（可选）
        - response_chat_item_id: 响应消息ID（可选）
        - variables: 模块变量，用于替换模块中输入框内容里的 [key]（可选）
        - detail: 是否返回中间值（默认 False）
        - custom_uid: 自定义用户ID（可选，文档未提及，保留兼容性）
        """
        base = self.base_url.rstrip("/")
        url = f"{base}/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = self._build_fastgpt_payload(prompt, stream=True, kwargs=kwargs.copy())

        try:
            with httpx.Client(timeout=120.0) as client:
                with client.stream("POST", url, headers=headers, json=payload) as response:
                    _check_stream_response_status(response, "FastGPT API")
                    
                    if DEBUG_FASTGPT_STREAM:
                        print(f"[DEBUG FastGPT Stream] Starting to read stream response. Status: {response.status_code}", flush=True)
                    
                    full_content = ""
                    usage_data = None
                    lines_processed = 0
                    chunks_yielded = 0
                    
                    try:
                        for line in response.iter_lines():
                            lines_processed += 1
                            
                            content, usage_data, chunks_yielded, should_break = self._process_fastgpt_stream_line(
                                line, lines_processed, chunks_yielded, usage_data, stream_callback
                            )
                            
                            if content:
                                full_content += content
                                if DEBUG_FASTGPT_STREAM:
                                    print(f"[DEBUG FastGPT Stream] About to yield content: '{content[:50]}...'", flush=True)
                                yield content
                            
                            if should_break:
                                if DEBUG_FASTGPT_STREAM:
                                    print(f"[DEBUG FastGPT Stream] Breaking due to finish_reason", flush=True)
                                break
                    
                    except Exception as stream_error:
                        if DEBUG_FASTGPT_STREAM:
                            import traceback
                            print(f"[DEBUG FastGPT Stream] Error during stream reading: {stream_error}", flush=True)
                            print(f"[DEBUG FastGPT Stream] Traceback: {traceback.format_exc()}", flush=True)
                        raise
                    
                    if DEBUG_FASTGPT_STREAM:
                        print(f"[DEBUG FastGPT Stream] Stream ended. Total lines: {lines_processed}, chunks yielded: {chunks_yielded}, full_content length: {len(full_content)}", flush=True)
                    
                    if lines_processed > 0 and chunks_yielded == 0:
                        print(f"[WARNING] FastGPT Stream: Processed {lines_processed} lines but yielded 0 chunks. This indicates a parsing issue.", flush=True)
                        if DEBUG_FASTGPT_STREAM:
                            print(f"[DEBUG FastGPT Stream] Final full_content (first 500 chars): {full_content[:500]}", flush=True)
                    
                    _update_usage_stats(self.usage_stats, self._stats_lock, usage_data, increment_requests=True)
                    
        except httpx.HTTPStatusError as e:
            raise _handle_stream_http_error(e, "FastGPT API") from e
        except httpx.RequestError as e:
            raise Exception(f"FastGPT 网络请求失败: {str(e)}") from e
        except Exception as e:
            error_msg = f"FastGPT 流式调用发生未预期的错误: {type(e).__name__}: {str(e)}"
            if DEBUG_FASTGPT_STREAM:
                import traceback
                error_msg += f"\n{traceback.format_exc()}"
            raise Exception(error_msg) from e

    def _generate_openai_compatible(self, url: str, prompt: str, temperature: float, max_tokens: int, **kwargs) -> str:
        """调用 OpenAI 兼容格式的 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                _update_usage_stats(self.usage_stats, self._stats_lock, result.get('usage'), increment_requests=True)
                
                # 提取回复内容
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0].get('message', {}).get('content', '')
                    if not content:
                        content = result['choices'][0].get('text', '')
                    return content
                else:
                    raise ValueError("API返回格式异常，未找到choices字段")
                    
        except httpx.HTTPStatusError as e:
            raise _handle_http_error(e, "API") from e
        except httpx.RequestError as e:
            raise Exception(f"网络请求失败: {str(e)}") from e
    
    def generate_stream(
        self, 
        prompt: str, 
        temperature: float = DEFAULT_TEMPERATURE, 
        max_tokens: int = DEFAULT_MAX_TOKENS, 
        stream_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        流式生成文本
        :param prompt: 输入的Prompt
        :param temperature: 温度参数
        :param max_tokens: 最大token数
        :param stream_callback: 流式输出回调函数，每次收到新内容时调用
        :param kwargs: 其他参数
        :return: 生成器，每次yield一个文本片段
        """
        if self.provider == "qwen":
            yield from self._generate_qwen_stream(prompt, temperature, max_tokens, stream_callback, **kwargs)
            return
        if self.provider == "fastgpt":
            yield from self._generate_fastgpt_stream(prompt, temperature, max_tokens, stream_callback, **kwargs)
            return
        raise ValueError(f"不支持的provider: {self.provider}")
    
    def _process_qwen_stream_line(
        self,
        line: str,
        full_content: str,
        usage_data: Optional[Dict[str, Any]],
        stream_callback: Optional[Callable[[str], None]]
    ) -> tuple[Optional[str], Optional[Dict[str, Any]], bool]:
        """
        处理 Qwen 流式响应的一行数据
        
        返回: (content, usage_data, should_break)
        """
        if not line.strip():
            return None, usage_data, False
        
        data_str = _parse_sse_data_line(line)
        if data_str is None:
            return None, usage_data, False
        
        data_str = data_str.strip()
        if data_str == "[DONE]":
            return None, usage_data, True
        
        try:
            data = json.loads(data_str)
            
            # 提取内容
            if 'choices' in data and len(data['choices']) > 0:
                delta = data['choices'][0].get('delta', {})
                content = delta.get('content', '')
                
                if content:
                    if stream_callback:
                        stream_callback(content)
                    return content, usage_data, False
            
            # 提取usage信息（通常在最后）
            if 'usage' in data:
                usage_data = data['usage']
            
            return None, usage_data, False
            
        except json.JSONDecodeError:
            return None, usage_data, False

    def _generate_qwen_stream(
        self, 
        prompt: str, 
        temperature: float, 
        max_tokens: int,
        stream_callback: Optional[Callable[[str], None]],
        **kwargs
    ) -> Iterator[str]:
        """流式调用阿里千问API（兼容OpenAI格式）"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,  # 启用流式输出
            **kwargs
        }
        
        try:
            with httpx.Client(timeout=120.0) as client:
                with client.stream("POST", url, headers=headers, json=payload) as response:
                    _check_stream_response_status(response, "API")
                    
                    full_content = ""
                    usage_data = None
                    
                    for line in response.iter_lines():
                        content, usage_data, should_break = self._process_qwen_stream_line(
                            line, full_content, usage_data, stream_callback
                        )
                        
                        if content:
                            full_content += content
                            yield content
                        
                        if should_break:
                            break
                    
                    _update_usage_stats(self.usage_stats, self._stats_lock, usage_data, increment_requests=True)
                    
        except httpx.HTTPStatusError as e:
            raise _handle_http_error(e, "API") from e
        except httpx.RequestError as e:
            raise Exception(f"网络请求失败: {str(e)}") from e
    
    def get_usage(self) -> Dict[str, Any]:
        """获取本次调用的Token使用情况"""
        return self.usage_stats.copy()


class RetryableLLMClient:
    """支持重试和断点续传的LLM客户端"""
    
    def __init__(
        self, 
        llm_client: LLMClient,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0
    ):
        self.llm_client = llm_client
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
    
    def generate_with_retry(
        self, 
        prompt: str,
        checkpoint_callback: Optional[Callable] = None,
        **kwargs
    ) -> str:
        """
        带重试的生成方法
        
        checkpoint_callback: 每次重试前调用，用于保存状态
        """
        last_exception = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # 调用LLM生成
                response = self.llm_client.generate(prompt, **kwargs)
                return response
            
            except Exception as e:
                last_exception = e
                error_type = type(e).__name__
                
                # 判断是否可重试
                if not self._is_retryable_error(e):
                    raise  # 不可重试的错误直接抛出
                
                # 如果是最后一次尝试，不再等待
                if attempt == self.max_retries:
                    break
                
                # 保存检查点（如果提供回调）
                if checkpoint_callback:
                    checkpoint_callback(attempt, error_type)
                
                # 计算等待时间（指数退避）
                wait_time = self.retry_delay * (self.backoff_factor ** (attempt - 1))
                print(f"第{attempt}次尝试失败: {error_type}, {wait_time:.1f}秒后重试...")
                time.sleep(wait_time)
        
        # 所有重试都失败，抛出异常
        raise Exception(f"经过{self.max_retries}次重试后仍然失败") from last_exception
    
    def generate_stream_with_retry(
        self,
        prompt: str,
        stream_callback: Optional[Callable[[str], None]] = None,
        checkpoint_callback: Optional[Callable] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        带重试的流式生成方法
        
        stream_callback: 每次收到新内容时调用
        checkpoint_callback: 每次重试前调用，用于保存状态
        """
        last_exception = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # 调用流式LLM生成
                full_content = ""
                chunks_received = 0
                
                if DEBUG_FASTGPT_STREAM:
                    print(f"[DEBUG RetryableLLMClient] Starting stream attempt {attempt}", flush=True)
                
                # 调用流式LLM生成，确保传递所有参数
                generator = self.llm_client.generate_stream(
                    prompt, 
                    stream_callback=stream_callback,
                    **kwargs
                )
                
                if DEBUG_FASTGPT_STREAM:
                    print(f"[DEBUG RetryableLLMClient] Generator created, starting iteration...", flush=True)
                
                for chunk in generator:
                    chunks_received += 1
                    full_content += chunk
                    if DEBUG_FASTGPT_STREAM:
                        print(f"[DEBUG RetryableLLMClient] Received chunk #{chunks_received}: '{chunk[:50]}...' (length: {len(chunk)})", flush=True)
                    yield chunk
                
                if DEBUG_FASTGPT_STREAM:
                    print(f"[DEBUG RetryableLLMClient] Generator iteration completed", flush=True)
                
                if DEBUG_FASTGPT_STREAM:
                    print(f"[DEBUG RetryableLLMClient] Stream completed. Total chunks: {chunks_received}, total length: {len(full_content)}", flush=True)
                
                # 如果没有任何内容被 yield，记录警告
                if chunks_received == 0:
                    print(f"[WARNING] generate_stream_with_retry: No chunks received from generate_stream. This may indicate a parsing issue.", flush=True)
                
                # 成功生成，返回
                return
            
            except Exception as e:
                last_exception = e
                error_type = type(e).__name__
                
                # 判断是否可重试
                if not self._is_retryable_error(e):
                    raise  # 不可重试的错误直接抛出
                
                # 如果是最后一次尝试，不再等待
                if attempt == self.max_retries:
                    break
                
                # 保存检查点（如果提供回调）
                if checkpoint_callback:
                    checkpoint_callback(attempt, error_type)
                
                # 计算等待时间（指数退避）
                wait_time = self.retry_delay * (self.backoff_factor ** (attempt - 1))
                print(f"第{attempt}次尝试失败: {error_type}, {wait_time:.1f}秒后重试...")
                time.sleep(wait_time)
        
        # 所有重试都失败，抛出异常
        raise Exception(f"经过{self.max_retries}次重试后仍然失败") from last_exception
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """判断错误是否可重试"""
        error_str = str(error).lower()
        retryable_keywords = [
            '限流', 'rate limit', '429',
            '网络', 'network', 'connection',
            '超时', 'timeout',
            'api调用失败'
        ]
        return any(keyword in error_str for keyword in retryable_keywords)

