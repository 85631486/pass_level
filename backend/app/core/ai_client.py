"""
AI 客户端封装（支持阿里云千问和 FastGPT）

本模块是**对外部大模型服务的最薄封装层**，职责：

- 负责读取 `config/ai_config.yaml` 配置
- 封装 HTTP 请求（包括普通模式与流式输出模式）
- 支持多 provider（qwen/fastgpt）
- 为教学平台的业务场景提供若干高层 API：
  - 思维导图 / 关卡树生成
  - 任务 / 卡片 / 环节 / 题目生成
  - 学习助手问答

注意：这里**不涉及数据库与业务日志**，只关注「构造 Prompt → 调用接口 → 解析 JSON」。
"""
import logging
import json
import yaml
import os
from pathlib import Path
from typing import Optional, Dict, Any, Callable, Iterator
import httpx

logger = logging.getLogger(__name__)

# 调试模式：通过环境变量 DEBUG_AI_STREAM 控制
DEBUG_AI_STREAM = os.getenv("DEBUG_AI_STREAM", "false").lower() == "true"


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


# ==================== AIClient 类 ====================

class AIClient:
    """AI 客户端（支持阿里云千问和 FastGPT）

    用于向兼容 OpenAI Chat Completions 协议的服务发送请求。

    推荐只在 service 层中组合使用，不直接暴露给视图 / 路由层。
    """
    
    def __init__(self):
        self.config = self._load_config()
        ai_config = self.config.get("ai", {})
        
        # 获取 provider（默认 qwen）
        self.provider = (ai_config.get("provider", "qwen") or "qwen").lower()
        
        # 根据 provider 加载配置
        if self.provider == "qwen":
            qwen_config = ai_config.get("qwen", {})
            self.api_key = qwen_config.get("api_key", "")
            self.base_url = qwen_config.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            self.model = qwen_config.get("model", "qwen-turbo")
        elif self.provider == "fastgpt":
            fastgpt_config = ai_config.get("fastgpt", {})
            self.api_key = fastgpt_config.get("api_key", "")
            self.base_url = fastgpt_config.get("base_url", "https://fastgpt.run/api")
            self.model = fastgpt_config.get("model", "")
        else:
            raise ValueError(f"不支持的 provider: {self.provider}，支持的值: qwen, fastgpt")
        
        if not self.api_key:
            logger.warning(f"AI API Key not configured for provider: {self.provider}")
        
        # 通用配置
        self.temperature = ai_config.get("temperature", 0.7)
        self.max_tokens = ai_config.get("max_tokens", 8000)
        self.timeout = ai_config.get("timeout", 120)
    
    def _load_config(self) -> dict:
        """加载 AI 配置文件

        配置文件路径：`backend/config/ai_config.yaml`

        Returns
        -------
        dict
            YAML 解析后的配置字典，读取失败时返回空字典。
        """
        config_path = Path(__file__).resolve().parents[2] / "config" / "ai_config.yaml"
        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            else:
                logger.warning(f"AI config file not found: {config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading AI config: {e}", exc_info=True)
            return {}
    
    def _call_api(self, messages: list, **kwargs) -> Optional[str]:
        """调用 Chat Completions 接口（一次性返回）

        Parameters
        ----------
        messages : list
            OpenAI 风格的对话消息列表，例如：
            [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        **kwargs :
            可选参数，如 model / temperature / max_tokens 等。

        Returns
        -------
        Optional[str]
            成功时返回模型回复的 content 字符串；失败或未配置 API Key 时返回 None。
        """
        if not self.api_key:
            logger.warning("AI API Key not configured")
            return None
        
        if self.provider == "qwen":
            return self._call_qwen_api(messages, **kwargs)
        elif self.provider == "fastgpt":
            return self._call_fastgpt_api(messages, **kwargs)
        else:
            logger.error(f"Unsupported provider: {self.provider}")
            return None
    
    def _call_qwen_api(self, messages: list, **kwargs) -> Optional[str]:
        """调用阿里云千问 API（兼容 OpenAI 格式）"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            **{k: v for k, v in kwargs.items() if k not in ["model", "temperature", "max_tokens"]}
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                content = _extract_content_from_response(result)
                
                if content:
                    return content
                else:
                    logger.error(f"Unexpected API response: {result}")
                    return None
                    
        except httpx.HTTPStatusError as e:
            error = _handle_http_error(e, "阿里云千问 API")
            logger.error(f"Error calling AI API: {error}", exc_info=True)
            return None
        except httpx.RequestError as e:
            logger.error(f"Network error calling AI API: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error in AI API call: {e}", exc_info=True)
            return None
    
    def _build_fastgpt_payload(
        self,
        messages: list,
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
            "messages": messages
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
    
    def _call_fastgpt_api(self, messages: list, **kwargs) -> Optional[str]:
        """调用 FastGPT OpenAPI /v1/chat/completions 接口
        
        文档: https://doc.fastgpt.io/docs/introduction/development/openapi/chat
        """
        base = self.base_url.rstrip("/")
        url = f"{base}/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = self._build_fastgpt_payload(messages, stream=False, kwargs=kwargs.copy())

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                result = response.json()
                content = _extract_content_from_response(result)

                if content:
                    return content

                raise ValueError(f"FastGPT API返回格式无法解析: {result}")

        except httpx.HTTPStatusError as e:
            error = _handle_http_error(e, "FastGPT API")
            logger.error(f"Error calling FastGPT API: {error}", exc_info=True)
            return None
        except httpx.RequestError as e:
            logger.error(f"FastGPT 网络请求失败: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling FastGPT API: {e}", exc_info=True)
            return None
    
    def _call_api_stream(self, messages: list, callback=None, **kwargs):
        """调用 Chat Completions 接口（流式输出）

        服务端会以 Server-Sent Events / 分片 JSON 的形式逐步返回内容。

        Parameters
        ----------
        messages : list
            OpenAI 风格的对话消息列表。
        callback : Callable[[str], None] | None
            每次收到增量 content 时回调，用于透传到前端或拼装中间态。
        **kwargs :
            其它可选参数，例如 model、temperature、max_tokens 等。

        Returns
        -------
        Optional[str]
            聚合后的完整 content 字符串，失败时返回 None。
        """
        if not self.api_key:
            logger.warning("AI API Key not configured")
            return None
        
        if self.provider == "qwen":
            return self._call_qwen_api_stream(messages, callback, **kwargs)
        elif self.provider == "fastgpt":
            return self._call_fastgpt_api_stream(messages, callback, **kwargs)
        else:
            logger.error(f"Unsupported provider: {self.provider}")
            return None
    
    def _call_qwen_api_stream(self, messages: list, callback=None, **kwargs) -> Optional[str]:
        """流式调用阿里云千问 API（兼容 OpenAI 格式）"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "stream": True,  # 启用流式输出
            **{k: v for k, v in kwargs.items() if k not in ["model", "temperature", "max_tokens", "stream"]}
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                with client.stream("POST", url, headers=headers, json=payload) as response:
                    _check_stream_response_status(response, "阿里云千问 API")
                    
                    full_content = ""
                    for line in response.iter_lines():
                        if not line.strip():
                            continue
                        
                        data_str = _parse_sse_data_line(line)
                        if data_str is None:
                            continue
                        
                        data_str = data_str.strip()
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            
                            # 提取内容
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                
                                if content:
                                    full_content += content
                                    if callback:
                                        callback(content)
                        except json.JSONDecodeError:
                            continue
                    
                    return full_content
                    
        except httpx.HTTPStatusError as e:
            error = _handle_stream_http_error(e, "阿里云千问 API")
            logger.error(f"Error calling AI API stream: {error}", exc_info=True)
            return None
        except httpx.RequestError as e:
            logger.error(f"Network error calling AI API stream: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error in AI API stream call: {e}", exc_info=True)
            return None
    
    def _process_fastgpt_stream_line(
        self,
        line: str,
        line_num: int,
        chunks_yielded: int,
        stream_callback: Optional[Callable[[str], None]]
    ) -> tuple[Optional[str], int, bool]:
        """
        处理 FastGPT 流式响应的一行数据
        
        返回: (content, new_chunks_yielded, should_break)
        """
        if not line.strip():
            return None, chunks_yielded, False
        
        if DEBUG_AI_STREAM:
            logger.debug(f"[DEBUG FastGPT Stream] Line {line_num}: {line[:100]}...")
        
        data_str = _parse_sse_data_line(line)
        
        if data_str is not None:
            data_str = data_str.strip()
            if data_str == "[DONE]":
                if DEBUG_AI_STREAM:
                    logger.debug(f"[DEBUG FastGPT Stream] Received [DONE] marker")
                return None, chunks_yielded, True
            
            if not data_str:
                return None, chunks_yielded, False
            
            try:
                data = json.loads(data_str)
                
                if DEBUG_AI_STREAM:
                    logger.debug(f"[DEBUG FastGPT Stream] Parsed JSON keys: {list(data.keys())}")
                
                if 'choices' not in data or len(data['choices']) == 0:
                    if DEBUG_AI_STREAM:
                        logger.debug(f"[DEBUG FastGPT Stream] No 'choices' in data. Full data: {json.dumps(data, ensure_ascii=False)[:200]}")
                    return None, chunks_yielded, False
                
                choice = data['choices'][0]
                content = _extract_content_from_choices(choice)
                
                finish_reason = choice.get('finish_reason')
                should_break = finish_reason is not None
                
                if content:
                    chunks_yielded += 1
                    if stream_callback:
                        stream_callback(content)
                    if DEBUG_AI_STREAM:
                        logger.debug(f"[DEBUG FastGPT Stream] Yielding chunk #{chunks_yielded}: '{content[:50]}...' (length: {len(content)})")
                
                return content, chunks_yielded, should_break
                
            except json.JSONDecodeError as e:
                if DEBUG_AI_STREAM:
                    logger.debug(f"[DEBUG FastGPT Stream] JSON decode error: {e}, data_str: {data_str[:100]}")
                return None, chunks_yielded, False
        
        elif line.startswith("event: "):
            if DEBUG_AI_STREAM:
                logger.debug(f"[DEBUG FastGPT Stream] Event line: {line}")
            return None, chunks_yielded, False
        elif DEBUG_AI_STREAM:
            logger.debug(f"[DEBUG FastGPT Stream] Unknown line format: {line[:100]}")
        
        return None, chunks_yielded, False
    
    def _call_fastgpt_api_stream(self, messages: list, callback=None, **kwargs) -> Optional[str]:
        """流式调用 FastGPT OpenAPI /v1/chat/completions 接口
        
        文档: https://doc.fastgpt.io/docs/introduction/development/openapi/chat
        """
        base = self.base_url.rstrip("/")
        url = f"{base}/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = self._build_fastgpt_payload(messages, stream=True, kwargs=kwargs.copy())

        try:
            with httpx.Client(timeout=self.timeout) as client:
                with client.stream("POST", url, headers=headers, json=payload) as response:
                    _check_stream_response_status(response, "FastGPT API")
                    
                    if DEBUG_AI_STREAM:
                        logger.debug(f"[DEBUG FastGPT Stream] Starting to read stream response. Status: {response.status_code}")
                    
                    full_content = ""
                    lines_processed = 0
                    chunks_yielded = 0
                    
                    try:
                        for line in response.iter_lines():
                            lines_processed += 1
                            
                            content, chunks_yielded, should_break = self._process_fastgpt_stream_line(
                                line, lines_processed, chunks_yielded, callback
                            )
                            
                            if content:
                                full_content += content
                            
                            if should_break:
                                if DEBUG_AI_STREAM:
                                    logger.debug(f"[DEBUG FastGPT Stream] Breaking due to finish_reason")
                                break
                    
                    except Exception as stream_error:
                        if DEBUG_AI_STREAM:
                            import traceback
                            logger.debug(f"[DEBUG FastGPT Stream] Error during stream reading: {stream_error}")
                            logger.debug(f"[DEBUG FastGPT Stream] Traceback: {traceback.format_exc()}")
                        raise
                    
                    if DEBUG_AI_STREAM:
                        logger.debug(f"[DEBUG FastGPT Stream] Stream ended. Total lines: {lines_processed}, chunks yielded: {chunks_yielded}, full_content length: {len(full_content)}")
                    
                    if lines_processed > 0 and chunks_yielded == 0:
                        logger.warning(f"FastGPT Stream: Processed {lines_processed} lines but yielded 0 chunks. This indicates a parsing issue.")
                    
                    return full_content
                    
        except httpx.HTTPStatusError as e:
            error = _handle_stream_http_error(e, "FastGPT API")
            logger.error(f"Error calling FastGPT API stream: {error}", exc_info=True)
            return None
        except httpx.RequestError as e:
            logger.error(f"FastGPT 网络请求失败: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            error_msg = f"FastGPT 流式调用发生未预期的错误: {type(e).__name__}: {str(e)}"
            if DEBUG_AI_STREAM:
                import traceback
                error_msg += f"\n{traceback.format_exc()}"
            logger.error(error_msg, exc_info=True)
            return None
    
    # ==================== 业务方法（保持不变）====================
    
    def generate_mindmap(self, chapter_name: str, description: Optional[str] = None, knowledge_points: Optional[list] = None) -> Optional[Dict[str, Any]]:
        """AI 生成思维导图（关卡树结构，非流式）

        典型用途：根据「篇章名称 + 描述 + 知识点列表」生成一棵树状关卡结构，
        供地图编辑器鱼骨布局算法 `layoutFishbone` 消化。
        """
        prompt = f"""请为教学篇章"{chapter_name}"生成一个思维导图结构的关卡树（学习路径）。

篇章描述：{description or "无"}

知识点：{', '.join(knowledge_points) if knowledge_points else "无"}

请生成一个JSON格式的思维导图结构，包含：
1. 关卡节点（level nodes）
2. 关卡之间的层级关系和顺序
3. 每个关卡的基本信息（名称、描述）

返回格式示例：
{{
  "root": {{
    "id": "root",
    "topic": "{chapter_name}",
    "children": [
      {{
        "id": "level_1",
        "topic": "关卡1名称",
        "description": "关卡1描述",
        "children": [...]
      }}
    ]
  }}
}}

请直接返回JSON，不要包含其他文字说明。"""
        
        messages = [
            {"role": "system", "content": "你是一个教学设计师，擅长设计游戏化学习路径。"},
            {"role": "user", "content": prompt}
        ]
        
        result = self._call_api(messages)
        if result:
            try:
                # 尝试解析JSON
                return json.loads(result)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {result}")
                return None
        return None
    
    def generate_mindmap_from_syllabus_stream(
        self,
        syllabus: str,
        chapter_name: Optional[str] = None,
        description: Optional[str] = None,
        stream_callback=None,
        extra_instructions: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """从教学大纲生成思维导图（流式输出）

        这是平台中**复杂度最高**的 AI 能力之一：
        - 输入完整教学大纲（syllabus）
        - 按章节和知识点先后关系生成多层级关卡树
        - 使用流式输出，将增量结果通过回调函数推送到前端
        """
        prompt = f"""请分析以下教学大纲，提取知识点并分析它们之间的先后关联关系，生成一个层次化的思维导图结构（关卡树）。

教学大纲内容：
{syllabus}

{'篇章名称：' + chapter_name if chapter_name else ''}
{'篇章描述：' + description if description else ''}

如果教师给出了额外的生成规则或自然语言命令，请严格遵守：
{extra_instructions or '（无特别说明时，请按章节结构和知识点依赖关系自动规划）'}

请按照以下要求生成思维导图：
1. 分析教学大纲中的知识点和章节结构
2. 识别知识点之间的先后顺序和依赖关系
3. 生成层次化的关卡树结构，每个关卡对应一个知识点或章节
4. 确保关卡之间的顺序符合学习路径的逻辑
5. 如果有"按章节分类 / 按能力维度分组 / 难度分层"等说明，请在节点层级与命名中体现出来

返回JSON格式（必须是有效的JSON，不要包含markdown代码块）：
{{
  "root": {{
    "id": "root",
    "topic": "{chapter_name or '根节点'}",
    "description": "{description or ''}",
    "children": [
      {{
        "id": "level_1",
        "topic": "第一层关卡名称",
        "description": "关卡描述",
        "order": 1,
        "children": [
          {{
            "id": "level_1_1",
            "topic": "第二层关卡名称",
            "description": "关卡描述",
            "order": 1,
            "children": []
          }}
        ]
      }}
    ]
  }}
}}

重要：请直接返回JSON格式，不要包含任何markdown代码块标记（如```json）或其他文字说明。"""
        
        messages = [
            {"role": "system", "content": "你是一个教学设计师和知识图谱专家，擅长分析教学大纲并生成层次化的学习路径。你总是返回有效的JSON格式数据。"},
            {"role": "user", "content": prompt}
        ]
        
        result = self._call_api_stream(messages, callback=stream_callback, max_tokens=8000)
        if result:
            try:
                # 清理可能的 markdown 代码块标记，保证是纯 JSON 字符串
                cleaned_result = result.strip()
                if cleaned_result.startswith("```json"):
                    cleaned_result = cleaned_result[7:]
                if cleaned_result.startswith("```"):
                    cleaned_result = cleaned_result[3:]
                if cleaned_result.endswith("```"):
                    cleaned_result = cleaned_result[:-3]
                cleaned_result = cleaned_result.strip()
                
                return json.loads(cleaned_result)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse AI response as JSON: {result[:200]}... Error: {e}")
                # 尝试提取JSON部分
                try:
                    import re
                    json_match = re.search(r'\{.*\}', result, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass
                return None
        return None
    
    def generate_mindmap_from_syllabus(
        self,
        syllabus: str,
        chapter_name: Optional[str] = None,
        description: Optional[str] = None,
        extra_instructions: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """从教学大纲生成思维导图（层次化结构，非流式）

        与 `generate_mindmap_from_syllabus_stream` 相比：
        - 调用方式为一次性返回
        - 方便在不需要前端流式交互时直接使用
        """
        prompt = f"""请分析以下教学大纲，提取知识点并分析它们之间的先后关联关系，生成一个层次化的思维导图结构（关卡树）。

教学大纲内容：
{syllabus}

{'篇章名称：' + chapter_name if chapter_name else ''}
{'篇章描述：' + description if description else ''}

如果教师给出了额外的生成规则或自然语言命令，请严格遵守：
{extra_instructions or '（无特别说明时，请按章节结构和知识点依赖关系自动规划）'}

请按照以下要求生成思维导图：
1. 分析教学大纲中的知识点和章节结构
2. 识别知识点之间的先后顺序和依赖关系
3. 生成层次化的关卡树结构，每个关卡对应一个知识点或章节
4. 确保关卡之间的顺序符合学习路径的逻辑
5. 如果有"按章节分类 / 按能力维度分组 / 难度分层"等说明，请在节点层级与命名中体现出来

返回JSON格式（必须是有效的JSON，不要包含markdown代码块）：
{{
  "root": {{
    "id": "root",
    "topic": "{chapter_name or '根节点'}",
    "description": "{description or ''}",
    "children": [
      {{
        "id": "level_1",
        "topic": "第一层关卡名称",
        "description": "关卡描述",
        "order": 1,
        "children": [
          {{
            "id": "level_1_1",
            "topic": "第二层关卡名称",
            "description": "关卡描述",
            "order": 1,
            "children": []
          }}
        ]
      }}
    ]
  }}
}}

重要：请直接返回JSON格式，不要包含任何markdown代码块标记（如```json）或其他文字说明。"""
        
        messages = [
            {"role": "system", "content": "你是一个教学设计师和知识图谱专家，擅长分析教学大纲并生成层次化的学习路径。你总是返回有效的JSON格式数据。"},
            {"role": "user", "content": prompt}
        ]
        
        result = self._call_api(messages, max_tokens=8000)
        if result:
            try:
                # 清理可能的 markdown 代码块标记
                cleaned_result = result.strip()
                if cleaned_result.startswith("```json"):
                    cleaned_result = cleaned_result[7:]
                if cleaned_result.startswith("```"):
                    cleaned_result = cleaned_result[3:]
                if cleaned_result.endswith("```"):
                    cleaned_result = cleaned_result[:-3]
                cleaned_result = cleaned_result.strip()
                
                return json.loads(cleaned_result)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse AI response as JSON: {result[:200]}... Error: {e}")
                # 尝试提取JSON部分
                try:
                    import re
                    json_match = re.search(r'\{.*\}', result, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass
                return None
        return None
    
    def generate_task(self, level_name: str, level_description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """AI 生成关卡任务"""
        prompt = f"""请为关卡"{level_name}"生成一个学习任务。

关卡描述：{level_description or "无"}

请生成任务内容，包括：
1. 任务名称
2. 任务描述
3. 任务目标

返回JSON格式：
{{
  "name": "任务名称",
  "description": "任务描述",
  "objective": "任务目标"
}}"""
        
        messages = [
            {"role": "system", "content": "你是一个教学设计师，擅长设计学习任务。"},
            {"role": "user", "content": prompt}
        ]
        
        result = self._call_api(messages)
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {result}")
                return None
        return None
    
    def generate_cards(self, task_name: str, task_description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """AI 生成知识卡片和技能卡片"""
        prompt = f"""请为任务"{task_name}"生成知识卡片和技能卡片。

任务描述：{task_description or "无"}

请生成：
1. 知识卡片列表（知识点）
2. 技能卡片列表（掌握的技能）

返回JSON格式：
{{
  "knowledge_cards": [
    {{"title": "知识点1", "content": "内容", "knowledge_point": "知识点名称"}},
    ...
  ],
  "skill_cards": [
    {{"title": "技能1", "content": "内容", "skill_name": "技能名称"}},
    ...
  ]
}}"""
        
        messages = [
            {"role": "system", "content": "你是一个教学设计师，擅长设计知识卡片和技能卡片。"},
            {"role": "user", "content": prompt}
        ]
        
        result = self._call_api(messages)
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {result}")
                return None
        return None
    
    def generate_phases(self, task_name: str, task_description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """AI 生成任务操作环节步骤"""
        prompt = f"""请为任务"{task_name}"生成操作环节和步骤。

任务描述：{task_description or "无"}

请生成：
1. 环节列表（每个环节包含多个步骤）
2. 每个步骤的内容和要求

返回JSON格式：
{{
  "phases": [
    {{
      "phase_name": "环节1",
      "order": 1,
      "steps": [
        {{
          "step_name": "步骤1",
          "content": "步骤内容",
          "requirements": "操作要求",
          "submission_type": "text",
          "order": 1
        }},
        ...
      ]
    }},
    ...
  ]
}}"""
        
        messages = [
            {"role": "system", "content": "你是一个教学设计师，擅长设计学习环节和步骤。"},
            {"role": "user", "content": prompt}
        ]
        
        result = self._call_api(messages)
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {result}")
                return None
        return None
    
    def generate_questions(self, level_name: str, knowledge_points: Optional[list] = None, skill_points: Optional[list] = None) -> Optional[Dict[str, Any]]:
        """AI 生成闯关考题"""
        prompt = f"""请为关卡"{level_name}"生成闯关考题。

知识点：{', '.join(knowledge_points) if knowledge_points else "无"}
技能点：{', '.join(skill_points) if skill_points else "无"}

请生成3-5道题目，包括：
1. 单选题
2. 多选题
3. 判断题
4. 简答题

返回JSON格式：
{{
  "questions": [
    {{
      "question_type": "single_choice",
      "title": "题目标题",
      "content": "题目内容",
      "options": ["选项1", "选项2", "选项3", "选项4"],
      "correct_answer": "选项1",
      "answer_analysis": "答案解析",
      "difficulty": "medium",
      "score": 10.0
    }},
    ...
  ]
}}"""
        
        messages = [
            {"role": "system", "content": "你是一个教学设计师，擅长设计考试题目。"},
            {"role": "user", "content": prompt}
        ]
        
        result = self._call_api(messages)
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {result}")
                return None
        return None
    
    def learning_help(self, question: str, context: Optional[str] = None) -> Optional[str]:
        """AI 学习助手（为学生提供学习指导）"""
        prompt = f"""学生提问：{question}

学习上下文：{context or "无"}

请提供学习指导、知识点解释或学习建议。"""
        
        messages = [
            {"role": "system", "content": "你是一个AI学习助手，擅长为学生提供学习指导和帮助。"},
            {"role": "user", "content": prompt}
        ]
        
        return self._call_api(messages)

    def teaching_guide_to_course_json(self, markdown: str) -> Optional[Dict[str, Any]]:
        """将Markdown实验指导书转换为固定结构的课程JSON（courseData）（非流式）

        生成的JSON结构需与前端demo中的courseData保持一致：
        {
          "steps": [
            {
              "id": "step1-1",
              "type": "content",
              "title": "...",
              "subtitle": "...",
              "content": "<div>...</div>",
              "knowledgeCard": { "icon": "💡", "title": "...", "content": "..." }
            },
            {
              "id": "step1-2",
              "type": "quiz",
              "title": "课堂问答：...",
              "questions": [
                { "id": "q1", "text": "...", "options": [...], "correctAnswer": "A", "explanation": "...", "points": 5 }
              ]
            },
            {
              "id": "op1",
              "type": "operation",
              "title": "操作1：...",
              "subtitle": "掌握10个核心操作（第1个）",
              "content": "<div>...</div>",
              "practice": { "title": "...", "tasks": ["...", "..."] },
              "knowledgeCard": { ... },
              "questions": [ ... ]
            }
          ]
        }
        """
        example_json = {
            "steps": [
                {
                    "id": "step1-1",
                    "type": "content",
                    "title": "认识Excel界面",
                    "subtitle": "步骤一：认识Excel界面（15分钟）",
                    "content": "<div class=\"step-content\">...</div>",
                    "knowledgeCard": {
                        "icon": "💡",
                        "title": "Excel基础概念",
                        "content": "..."
                    }
                }
            ]
        }

        prompt = f"""
你现在的任务：把下面的 Markdown 实验指导书，转换为用于驱动交互页面的 JSON 数据。

【重要约束】：
1. JSON 结构必须与下面示例中的字段完全一致（字段名、嵌套结构、大小写都不能改）；
2. 只返回 JSON，本身不能再包一层 Markdown 代码块，也不要添加注释说明；
3. JSON 最外层必须是一个对象：{{ "steps": [ ... ] }}。

示例结构（仅示例，不要照搬内容）：
```json
{example_json}
```

解析要求：
- 将教案中的「操作步骤」拆分为若干 step，放入 steps 数组；
- 适当合并文字说明、代码块、示意图为 HTML 字符串，放入 step.content（你可以使用 <div>、<p>、<pre>、<ul> 等基础标签）；
- 把「课堂问答」转换为 type = "quiz" 的步骤，问题放入 step.questions 数组；
- 把「立即动手练习 / 综合练习 / 作业打卡」转换为 step.practice（包含 title 和 tasks 数组）；
- 若某一步有重要知识点总结，可以填入 step.knowledgeCard；
- 若某一步需要学生提交练习或作业，请在该 step 中设置 submission，例如：
  "submission": {{
    "enable": true,
    "title": "提交练习结果",
    "description": "请上传截图或文字说明，证明你已完成本步骤练习。",
    "successMessage": "已记录你的提交，继续加油！"
  }}

【交互增强要求】：
1. 如果步骤包含代码示例，在 step 中添加 components 数组，包含 type="code" 的组件，配置包含：
   - language: 编程语言（python/javascript/java/cpp/sql等）
   - template: 代码模板
   - testCases: 测试用例数组（可选）
2. 如果步骤包含"排序"、"分类"等操作，添加 type="drag-drop" 组件，配置包含：
   - items: 可拖拽项目数组
   - targetZones: 目标区域数组
3. 如果步骤包含视频链接，添加 type="video" 组件，配置包含：
   - url: 视频URL
   - checkpoints: 检查点数组（可选，用于弹题）
4. 如果步骤包含图表/流程图，添加 type="drawing" 组件，配置包含：
   - tools: 可用工具数组
   - backgroundImage: 背景图片URL（可选）
5. 为每个步骤设置 difficulty（1-5星），表示难度等级

【游戏化增强要求】：
1. 为每个步骤设置完成奖励，在 step 中添加 rewards（可选）：
   - exp: 经验值（建议10-50）
   - coins: 金币（建议5-20）
2. 在 meta 中添加 scoreConfig（可选）：
   - perQuestion: 每题分数（默认5）
   - perPractice: 每次练习分数（默认10）
   - completeBonus: 完成奖励（默认20）
3. 在 meta 中添加 gamification（可选）：
   - theme: 主题名称
   - difficulty: 整体难度（1-5）
   - timeLimit: 时间限制（分钟，可选）

下面是需要解析的 Markdown 内容：

{markdown}
"""

        messages = [
            {
                "role": "system",
                "content": "你是一名教学设计工程师，只输出严格符合要求的 JSON 数据，不输出任何解释文字。",
            },
            {"role": "user", "content": prompt},
        ]

        result = self._call_api(messages)
        if not result:
            return None

        try:
            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Failed to parse teaching_guide_to_course_json response as JSON, try extracting JSON part")
            # 尝试从回复中提取 JSON 主体
            try:
                import re
                match = re.search(r'\{.*\}', result, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except Exception:
                pass
            return None

    def teaching_guide_to_course_json_stream(
        self,
        markdown: str,
        stream_callback=None,
    ) -> Optional[Dict[str, Any]]:
        """将Markdown实验指导书转换为课程JSON（courseData）（流式输出）

        使用 `_call_api_stream` 获取增量内容，并通过 `stream_callback` 透传给上层，
        最终仍然会尝试将完整内容解析为 JSON。
        """
        example_json = {
            "steps": [
                {
                    "id": "step1-1",
                    "type": "content",
                    "title": "认识Excel界面",
                    "subtitle": "步骤一：认识Excel界面（15分钟）",
                    "content": "<div class=\"step-content\">...</div>",
                    "knowledgeCard": {
                        "icon": "💡",
                        "title": "Excel基础概念",
                        "content": "...",
                    },
                }
            ]
        }

        prompt = f"""
你现在的任务：把下面的 Markdown 实验指导书，转换为用于驱动交互页面的 JSON 数据。

【重要约束】：
1. JSON 结构必须与下面示例中的字段完全一致（字段名、嵌套结构、大小写都不能改）；
2. 只返回 JSON，本身不能再包一层 Markdown 代码块，也不要添加注释说明；
3. JSON 最外层必须是一个对象：{{ "steps": [ ... ] }}。

示例结构（仅示例，不要照搬内容）：
```json
{example_json}
```

解析要求：
- 将教案中的「操作步骤」拆分为若干 step，放入 steps 数组；
- 适当合并文字说明、代码块、示意图为 HTML 字符串，放入 step.content（你可以使用 <div>、<p>、<pre>、<ul> 等基础标签）；
- 把「课堂问答」转换为 type = "quiz" 的步骤，问题放入 step.questions 数组；
- 把「立即动手练习 / 综合练习 / 作业打卡」转换为 step.practice（包含 title 和 tasks 数组）；
- 若某一步有重要知识点总结，可以填入 step.knowledgeCard；
- 若某一步需要学生提交练习或作业，请在该 step 中设置 submission，例如：
  "submission": {{
    "enable": true,
    "title": "提交练习结果",
    "description": "请上传截图或文字说明，证明你已完成本步骤练习。",
    "successMessage": "已记录你的提交，继续加油！"
  }}

【交互增强要求】：
1. 如果步骤包含代码示例，在 step 中添加 components 数组，包含 type="code" 的组件，配置包含：
   - language: 编程语言（python/javascript/java/cpp/sql等）
   - template: 代码模板
   - testCases: 测试用例数组（可选）
2. 如果步骤包含"排序"、"分类"等操作，添加 type="drag-drop" 组件，配置包含：
   - items: 可拖拽项目数组
   - targetZones: 目标区域数组
3. 如果步骤包含视频链接，添加 type="video" 组件，配置包含：
   - url: 视频URL
   - checkpoints: 检查点数组（可选，用于弹题）
4. 如果步骤包含图表/流程图，添加 type="drawing" 组件，配置包含：
   - tools: 可用工具数组
   - backgroundImage: 背景图片URL（可选）
5. 为每个步骤设置 difficulty（1-5星），表示难度等级

【游戏化增强要求】：
1. 为每个步骤设置完成奖励，在 step 中添加 rewards（可选）：
   - exp: 经验值（建议10-50）
   - coins: 金币（建议5-20）
2. 在 meta 中添加 scoreConfig（可选）：
   - perQuestion: 每题分数（默认5）
   - perPractice: 每次练习分数（默认10）
   - completeBonus: 完成奖励（默认20）
3. 在 meta 中添加 gamification（可选）：
   - theme: 主题名称
   - difficulty: 整体难度（1-5）
   - timeLimit: 时间限制（分钟，可选）

下面是需要解析的 Markdown 内容：

{markdown}
"""

        messages = [
            {
                "role": "system",
                "content": "你是一名教学设计工程师，只输出严格符合要求的 JSON 数据，不输出任何解释文字。",
            },
            {"role": "user", "content": prompt},
        ]

        result = self._call_api_stream(messages, callback=stream_callback, max_tokens=8000)
        if not result:
            return None

        try:
            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse teaching_guide_to_course_json_stream response as JSON, try extracting JSON part"
            )
            try:
                import re

                match = re.search(r"\{.*\}", result, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except Exception:
                pass
            return None
    
    def _build_teaching_guide_prompt(
        self,
        task_name: str,
        course_name: Optional[str],
        requirements: str,
        duration: Optional[str],
        template_type: str,
        prompt: Optional[str],
    ) -> str:
        """内部工具函数：构造教案生成的 user prompt"""
        if prompt:
            return prompt

        user_prompt = f"""请生成一份结构化的实验指导书（Markdown格式），要求如下：

## 基本信息
- 任务名称：{task_name}
{f"- 课程/主题：{course_name}" if course_name else ""}
{f"- 任务时长：{duration}" if duration else ""}

## 任务要求
{requirements}

## 生成要求
请按照以下结构生成Markdown格式的实验指导书：

1. **标题**：使用 # 任务名称
2. **学习目标**：包含知识目标、技能目标、素养目标
3. **任务时间**：总时长和建议分配
4. **准备工作**：必备工具列表
5. **操作步骤**：
   - 每个步骤包含标题和时间
   - 详细的操作方法（使用代码块格式）
   - "立即动手"练习任务
   - "课堂问答"部分（包含问题、选项、正确答案、解析）
6. **作业要求**：提交内容和文件命名规范
7. **常见问题**：Q&A格式
8. **学习提示**：学习建议
9. **自我检查**：检查清单

请确保：
- 使用清晰的Markdown格式
- 操作步骤详细且易于理解
- 包含适当的课堂问答题目
- 语言通俗易懂，适合初学者
"""

        if template_type == "detailed":
            user_prompt += "\n\n请生成更详细的内容，包含更多操作示例和扩展知识。"
        elif template_type == "simple":
            user_prompt += "\n\n请生成精简版内容，保留核心要点即可。"

        return user_prompt

    def generate_teaching_guide(
        self,
        task_name: str,
        course_name: Optional[str] = None,
        requirements: str = "",
        duration: Optional[str] = None,
        template_type: str = "standard",
        prompt: Optional[str] = None,
    ) -> Optional[str]:
        """生成实验指导书（Markdown格式，非流式）"""
        user_prompt = self._build_teaching_guide_prompt(
            task_name=task_name,
            course_name=course_name,
            requirements=requirements,
            duration=duration,
            template_type=template_type,
            prompt=prompt,
        )

        result = self._call_api(
            messages=[
                {
                    "role": "system",
                    "content": "你是一位经验丰富的教学设计师，擅长编写结构清晰、易于理解的实验指导书。",
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=4000,
        )

        return result.strip() if result else None

    def generate_teaching_guide_stream(
        self,
        task_name: str,
        course_name: Optional[str] = None,
        requirements: str = "",
        duration: Optional[str] = None,
        template_type: str = "standard",
        prompt: Optional[str] = None,
        stream_callback=None,
    ) -> Optional[str]:
        """生成实验指导书（Markdown格式，流式输出）"""
        user_prompt = self._build_teaching_guide_prompt(
            task_name=task_name,
            course_name=course_name,
            requirements=requirements,
            duration=duration,
            template_type=template_type,
            prompt=prompt,
        )

        messages = [
            {
                "role": "system",
                "content": "你是一位经验丰富的教学设计师，擅长编写结构清晰、易于理解的实验指导书。",
            },
            {"role": "user", "content": user_prompt},
        ]

        result = self._call_api_stream(
            messages,
            callback=stream_callback,
            temperature=0.7,
            max_tokens=4000,
        )
        return result.strip() if result else None

    def generate_teaching_requirements(
        self,
        task_name: str,
        course_name: Optional[str] = None,
        template_type: str = "standard",
    ) -> Optional[str]:
        """根据任务名称与课程主题，生成「任务要求」段落文本

        Parameters
        ----------
        task_name : str
            任务名称（例如：Excel界面速通）
        course_name : Optional[str]
            课程或主题名称（例如：玩转数据从个人生活开始）
        template_type : str
            模板类型（standard/simple/detailed），影响内容的详略程度
        """
        # 根据模板设置期望条目数量与详细程度提示
        if template_type == "simple":
            extra_hint = "请用比较精炼的语言，生成 3-5 条任务要求。"
        elif template_type == "detailed":
            extra_hint = "请写得更细致一些，生成 6-10 条任务要求，并适当拆分为更小的可操作目标。"
        else:
            extra_hint = "请生成 4-8 条任务要求，兼顾知识、技能与学习素养。"

        prompt = f"""请为下面的实践任务生成「任务要求」说明，供教师直接粘贴到实验指导书中。

任务名称：{task_name}
{"课程/主题：" + course_name if course_name else ""}

写作要求：
1. 使用简体中文。
2. 站在教师视角，概括本任务的学习目标、适用对象、学习前提/基础、学习要求等。
3. 重点体现「需要学生达到什么程度」的要求，可以从知识掌握、操作技能、学习习惯与思维素养等角度描述。
4. 输出格式必须是 Markdown 无序列表，每一行以 "- " 开头。
5. 不要输出任何标题（例如“任务要求：”）、前后说明文字或示例提示，只保留列表条目本身。
6. 不要使用代码块、表格或编号列表。

{extra_hint}
"""

        result = self._call_api(
            messages=[
                {
                    "role": "system",
                    "content": "你是一位经验丰富的职业教育教师，善于用清晰、具体的语言描述实践任务的学习要求。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )

        return result.strip() if result else None

    def generate_teaching_requirements_stream(
        self,
        task_name: str,
        course_name: Optional[str] = None,
        template_type: str = "standard",
        stream_callback=None,
    ) -> Optional[str]:
        """流式生成「任务要求」段落文本"""
        if template_type == "simple":
            extra_hint = "请用比较精炼的语言，生成 3-5 条任务要求。"
        elif template_type == "detailed":
            extra_hint = "请写得更细致一些，生成 6-10 条任务要求，并适当拆分为更小的可操作目标。"
        else:
            extra_hint = "请生成 4-8 条任务要求，兼顾知识、技能与学习素养。"

        prompt = f"""请为下面的实践任务生成「任务要求」说明，供教师直接粘贴到实验指导书中。

任务名称：{task_name}
{"课程/主题：" + course_name if course_name else ""}

写作要求：
1. 使用简体中文。
2. 站在教师视角，概括本任务的学习目标、适用对象、学习前提/基础、学习要求等。
3. 重点体现「需要学生达到什么程度」的要求，可以从知识掌握、操作技能、学习习惯与思维素养等角度描述。
4. 输出格式必须是 Markdown 无序列表，每一行以 "- " 开头。
5. 不要输出任何标题（例如“任务要求：”）、前后说明文字或示例提示，只保留列表条目本身。
6. 不要使用代码块、表格或编号列表。

{extra_hint}
"""

        messages = [
            {
                "role": "system",
                "content": "你是一位经验丰富的职业教育教师，善于用清晰、具体的语言描述实践任务的学习要求。",
            },
            {"role": "user", "content": prompt},
        ]

        result = self._call_api_stream(
            messages,
            callback=stream_callback,
            temperature=0.7,
            max_tokens=800,
        )

        return result.strip() if result else None

    def generate_syllabus_stream(
        self,
        course_name: str,
        course_requirements: str,
        stream_callback=None,
    ) -> Optional[str]:
        """AI生成教学大纲（流式输出，返回Markdown格式）
        
        参数：
        - course_name: 课程名称
        - course_requirements: 课程要求（教学目标、适用对象、学习要求等）
        - stream_callback: 流式输出回调函数，接收内容片段
        
        返回：
        - Markdown格式的教学大纲文本
        """
        prompt = f"""请根据以下信息生成一份完整的教学大纲（Markdown格式）。

课程名称：{course_name}

课程要求：
{course_requirements}

请生成一份结构化的教学大纲，包含以下内容：
1. 课程基本信息（课程名称、课程代码、学时、学分等）
2. 课程简介
3. 教学目标
4. 适用对象
5. 先修课程要求
6. 课程内容结构（按章节组织，包含章节名称、主要内容、学时分配）
7. 教学方法
8. 考核方式
9. 参考教材和资源

请使用Markdown格式输出，确保结构清晰、层次分明。直接返回Markdown内容，不要包含其他说明文字。"""
        
        messages = [
            {"role": "system", "content": "你是一个教学设计师和课程规划专家，擅长根据课程要求生成结构化的教学大纲。你总是返回格式良好的Markdown文档。"},
            {"role": "user", "content": prompt}
        ]
        
        result = self._call_api_stream(messages, callback=stream_callback, max_tokens=4000)
        return result

    def _build_data_file_prompt(
        self,
        task_name: str,
        data_requirements: str,
        file_format: str = "csv",
    ) -> str:
        """构造数据文件生成的提示词"""
        file_format = (file_format or "csv").lower()
        if file_format not in ["csv", "json", "txt"]:
            file_format = "csv"

        if file_format == "csv":
            format_hint = (
                "输出内容必须是严格的 CSV 文本，第一行为表头，使用英文逗号分隔，不要包含任何注释、说明文字或代码块标记。"
            )
        elif file_format == "json":
            format_hint = (
                "输出内容必须是合法的 JSON 文本，可以是对象或数组，不要包含任何注释、说明文字或代码块标记。"
            )
        else:
            format_hint = (
                "输出内容必须是纯文本表格或记录形式的示例数据，不要包含任何注释、说明文字或代码块标记。"
            )

        prompt = f"""你是一名数据建模与教学设计专家，请根据下面的任务和数据要求，生成一份可用于课堂实验或练习的示例数据文件内容。

任务名称：{task_name}

数据 / 场景要求（来自教案）：
{data_requirements}

生成要求：
1. 数据要贴合任务情境，具有一定真实性和多样性。
2. 数据规模适中，适合用于 1～2 学时内完成的练习，不要过于庞大。
3. 字段命名要清晰、规范，便于学生理解与后续分析。
4. 数据中要包含一定的复杂性（如重复值、缺失值、异常值等），便于教学中设计思考与讨论。
5. {format_hint}
"""
        return prompt

    def _cleanup_data_file_text(self, raw: Optional[str]) -> Optional[str]:
        """清理模型返回的数据内容（移除 Markdown 代码块等）"""
        if not raw:
            return None
        text = raw.strip()
        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) >= 3:
                text = "".join(parts[1:-1]).strip()
        return text

    def generate_data_file(
        self,
        task_name: str,
        data_requirements: str,
        file_format: str = "csv",
    ) -> Optional[str]:
        """根据教案中的数据要求生成示例数据文件内容（csv/json/txt，非流式）"""
        prompt = self._build_data_file_prompt(task_name, data_requirements, file_format)

        messages = [
            {
                "role": "system",
                "content": "你是一位经验丰富的数据建模与教学设计专家，擅长根据教学任务设计符合教学目标的示例数据集。",
            },
            {"role": "user", "content": prompt},
        ]

        result = self._call_api(
            messages=messages,
            temperature=0.7,
            max_tokens=self.max_tokens,
        )

        return self._cleanup_data_file_text(result)

    def generate_data_file_stream(
        self,
        task_name: str,
        data_requirements: str,
        file_format: str = "csv",
        stream_callback=None,
    ) -> Optional[str]:
        """根据教案中的数据要求生成示例数据文件内容（csv/json/txt，流式输出）"""
        prompt = self._build_data_file_prompt(task_name, data_requirements, file_format)

        messages = [
            {
                "role": "system",
                "content": "你是一位经验丰富的数据建模与教学设计专家，擅长根据教学任务设计符合教学目标的示例数据集。",
            },
            {"role": "user", "content": prompt},
        ]

        result = self._call_api_stream(
            messages=messages,
            callback=stream_callback,
            temperature=0.7,
            max_tokens=self.max_tokens,
        )

        return self._cleanup_data_file_text(result)
