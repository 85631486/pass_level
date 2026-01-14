import json
import logging
import os
import re
from typing import Any, Callable, Dict, List, Optional

import httpx
from openai import OpenAI

logger = logging.getLogger(__name__)

def _extract_content_from_choices(choice: Dict[str, Any]) -> str:
    """从 OpenAI 响应的 choices 中提取内容"""
    if "message" in choice and "content" in choice["message"]:
        return choice["message"]["content"] or ""
    if "delta" in choice and "content" in choice["delta"]:
        return choice["delta"]["content"] or ""
    return ""

def _extract_content_from_response(result: Dict[str, Any]) -> str:
    """从 OpenAI 响应中提取完整内容"""
    if "choices" in result and len(result["choices"]) > 0:
        return _extract_content_from_choices(result["choices"][0])
    return ""

def _parse_sse_data_line(line: str) -> Optional[str]:
    """解析 SSE 数据行"""
    if line.startswith("data: "):
        data = line[6:].strip()
        if data == "[DONE]":
            return None
        return data
    return None

def _check_stream_response_status(response: httpx.Response, api_name: str = "API") -> None:
    """检查流式响应状态码"""
    if response.status_code != 200:
        logger.error(f"{api_name} stream request failed with status {response.status_code}")
        response.read()
        logger.error(f"Error detail: {response.text}")
        response.raise_for_status()

def _handle_http_error(e: httpx.HTTPStatusError, api_name: str = "API") -> Exception:
    """处理 HTTP 错误"""
    logger.error(f"{api_name} request failed: {e.response.text}")
    return e

def _handle_stream_http_error(e: httpx.HTTPStatusError, api_name: str = "API") -> Exception:
    """处理流式 HTTP 错误"""
    logger.error(f"{api_name} stream request failed: {e.response.text}")
    return e

class AIClient:
    """AI 客户端，封装大模型 API 调用"""

    def __init__(self):
        self.config = self._load_config()
        self.api_key = os.getenv("DASH_SCOPE_API_KEY", "sk-08872de4c2f546be94f741d608b36e67")
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen-plus"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.temperature = 0.5
        self.max_tokens = 8000
        self.timeout = 180

    def _load_config(self) -> dict:
        """加载配置（存根）"""
        return {}

    def _call_api(self, messages: list, **kwargs) -> Optional[str]:
        """通用 API 调用"""
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                **{k: v for k, v in kwargs.items() if k not in ["model", "temperature", "max_tokens"]}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return None

    def _call_api_stream(self, messages: list, callback: Optional[Callable] = None, **kwargs) -> Optional[str]:
        """通用流式 API 调用"""
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                stream=True,
                **{k: v for k, v in kwargs.items() if k not in ["model", "temperature", "max_tokens", "stream"]}
            )
            full_content = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    if callback:
                        callback(content)
            return full_content
        except Exception as e:
            logger.error(f"Stream API call failed: {e}")
            return None

    def _cleanup_json_response(self, raw_json_str: str) -> Optional[Dict[str, Any]]:
        """清理并解析 AI 返回的 JSON 字符串"""
        if not raw_json_str:
            return None
        
        clean_str = re.sub(r"```json\s*|\s*```", "", raw_json_str).strip()
        
        try:
            return json.loads(clean_str)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", clean_str, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            logger.error(f"Failed to parse JSON: {clean_str}")
            return None

    # --- 业务方法 ---

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
        system_prompt = "你是一位资深的教育专家和课程设计师，擅长编写高质量的实验指导书和教学任务书。"
        user_content = f"请为课程「{course_name or '未命名课程'}」中的任务「{task_name}」编写一份实验指导书。\n"
        if duration: user_content += f"建议时长：{duration}\n"
        if requirements: user_content += f"任务要求：{requirements}\n"
        user_content += "\n请使用 Markdown 格式输出，包含：学习目标、任务时间、准备工作、操作步骤、课堂问答、作业要求等部分。"
        if prompt: user_content += f"\n额外要求：{prompt}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        return self._call_api_stream(messages, callback=stream_callback)

    def generate_teaching_requirements_stream(
        self,
        task_name: str,
        course_name: Optional[str] = None,
        template_type: str = "standard",
        stream_callback=None,
    ) -> Optional[str]:
        """流式生成「任务要求」段落"""
        messages = [
            {"role": "system", "content": "你是一位资深的教育专家。"},
            {"role": "user", "content": f"请为课程「{course_name or ''}」的任务「{task_name}」生成一段详细的「任务要求」描述，使用 Markdown 列表格式。"}
        ]
        return self._call_api_stream(messages, callback=stream_callback)

    def generate_syllabus_stream(
        self,
        course_name: str,
        course_requirements: str,
        stream_callback=None,
    ) -> Optional[str]:
        """AI生成教学大纲（流式输出）"""
        messages = [
            {"role": "system", "content": "你是一位资深的教育专家。"},
            {"role": "user", "content": f"请为课程「{course_name}」生成一份详细的教学大纲。要求如下：\n{course_requirements}"}
        ]
        return self._call_api_stream(messages, callback=stream_callback)

    def teaching_guide_to_course_json_stream(
        self,
        markdown: str,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> Optional[Dict[str, Any]]:
        """将 Markdown 实验指导书转换为可视化编辑器可用的 JSON 结构（流式）"""
        prompt = self._build_teaching_guide_to_course_json_prompt(markdown)
        messages = [
            {"role": "system", "content": "你是一位顶级的教学设计师和前端工程师，只输出严格符合要求的 JSON 数据，不输出任何解释文字。"},
            {"role": "user", "content": prompt}
        ]
        raw_response = self._call_api_stream(messages, callback=None)
        return self._cleanup_json_response(raw_response)

    def _build_teaching_guide_to_course_json_prompt(self, markdown: str) -> str:
        """构建 Markdown 转 JSON 的 Prompt"""
        example_json = {
            "meta": {
                "title": "课程标题",
                "preparations": ["预备知识1"],
                "goals": [{"title": "知识目标", "items": ["目标1"]}]
            },
            "steps": [
                {
                    "id": "step-1",
                    "title": "步骤标题",
                    "canvasConfig": { "width": 1200, "height": 800, "backgroundColor": "#ffffff" },
                    "components": [
                        {
                            "id": "comp-1-1",
                            "type": "text",
                            "config": { "content": "<h1>内容</h1>" },
                            "position": { "x": 100, "y": 50 },
                            "size": { "width": 1000, "height": 100 }
                        }
                    ]
                }
            ]
        }
        return f"""
请将以下 Markdown 实验指导书转换为可视化幻灯片编辑器的 JSON 数据。
严格遵守以下 JSON 结构示例：
{json.dumps(example_json, indent=2, ensure_ascii=False)}

要求：
1. 拆分步骤：每个 ## 标题为一个 step。
2. 组件化：文本转 type:"text" (HTML格式), 代码转 type:"code", 题目转 type:"quiz"。
3. 自动布局：为每个组件分配 position(x,y) 和 size(width,height)。
4. 只输出 JSON，不要解释。

待转换内容：
{markdown}
"""

    def generate_mindmap(self, chapter_name: str, description: Optional[str] = None, knowledge_points: Optional[list] = None) -> Optional[Dict[str, Any]]:
        """生成思维导图 JSON"""
        prompt = f"请为章节「{chapter_name}」生成一个思维导图 JSON 结构。描述：{description or ''}。知识点：{knowledge_points or []}"
        messages = [{"role": "user", "content": prompt}]
        raw = self._call_api(messages)
        return self._cleanup_json_response(raw)

    def generate_data_file_stream(self, task_name: str, data_requirements: str, file_format: str = "csv", stream_callback=None) -> Optional[str]:
        """生成示例数据文件内容"""
        messages = [
            {"role": "system", "content": "你是一个数据生成专家。"},
            {"role": "user", "content": f"请为任务「{task_name}」生成一份格式为 {file_format} 的示例数据。要求：{data_requirements}"}
        ]
        return self._call_api_stream(messages, callback=stream_callback)

    # 存根方法
    def generate_teaching_guide(self, **kwargs): return self.generate_teaching_guide_stream(**kwargs)
    def generate_teaching_requirements(self, **kwargs): return self.generate_teaching_requirements_stream(**kwargs)
    def generate_task(self, name, desc): return self._cleanup_json_response(self._call_api([{"role":"user","content":f"生成任务JSON: {name}"}]))
    def generate_cards(self, name, desc): return self._cleanup_json_response(self._call_api([{"role":"user","content":f"生成卡片JSON: {name}"}]))
    def generate_phases(self, name, desc): return self._cleanup_json_response(self._call_api([{"role":"user","content":f"生成步骤JSON: {name}"}]))
    def generate_questions(self, name, kp, sp): return self._cleanup_json_response(self._call_api([{"role":"user","content":f"生成题目JSON: {name}"}]))
    def generate_mindmap_from_syllabus_stream(self, **kwargs): return self.generate_mindmap(**kwargs)
    def generate_mindmap_from_syllabus(self, **kwargs): return self.generate_mindmap(**kwargs)
    def generate_data_file(self, **kwargs): return self.generate_data_file_stream(**kwargs)
    def learning_help(self, q, c): return self._call_api([{"role":"user","content":f"问题: {q}\n背景: {c}"}])
    def teaching_guide_to_course_json(self, md): return self.teaching_guide_to_course_json_stream(md)
