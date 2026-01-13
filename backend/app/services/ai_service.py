"""AI 服务封装

本模块处在「路由层 / 视图层」与「AIClient 客户端」之间，主要职责：

- 用更贴近业务的函数对 `AIClient` 进行二次封装；
- 负责**记录 AI 交互日志**（写入 `AIAssistantLog`），方便后续审计与分析；
- 不直接关心 HTTP 细节，也不负责权限控制，这些逻辑由 `api/routes/ai_assistant.py` 处理。
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from ..core.ai_client import AIClient
from ..models.ai_assistant_log import AIAssistantLog


class AIService:
    """AI 服务类

    每个 public 方法都对应一个具体业务能力（思维导图 / 任务 / 卡片 / 题目 / 学习助手等）。
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.client = AIClient()
    
    def generate_mindmap(self, chapter_name: str, description: Optional[str] = None, knowledge_points: Optional[list] = None) -> Optional[Dict[str, Any]]:
        """AI 生成思维导图（基于篇章名称和知识点）

        通常用于**较简单**的场景：老师只提供章节名称与若干知识点列表。
        """
        result = self.client.generate_mindmap(chapter_name, description, knowledge_points)
        
        # 记录日志
        self._log_interaction("generate_mindmap", {
            "chapter_name": chapter_name,
            "description": description,
            "knowledge_points": knowledge_points
        }, result)
        
        return result
    
    def generate_mindmap_from_syllabus(
        self,
        syllabus: str,
        chapter_name: Optional[str] = None,
        description: Optional[str] = None,
        extra_instructions: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """从教学大纲生成思维导图（非流式）

        适合对交互要求不高、一次性返回完整 JSON 的场景。
        """
        result = self.client.generate_mindmap_from_syllabus(
            syllabus, chapter_name, description, extra_instructions=extra_instructions
        )
        
        # 记录日志
        self._log_interaction("generate_mindmap_from_syllabus", {
            "syllabus": syllabus,
            "chapter_name": chapter_name,
            "description": description,
            "extra_instructions": extra_instructions,
        }, result)
        
        return result
    
    def generate_mindmap_from_syllabus_stream(
        self,
        syllabus: str,
        chapter_name: Optional[str] = None,
        description: Optional[str] = None,
        stream_callback=None,
        extra_instructions: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """从教学大纲生成思维导图（流式输出）

        Parameters
        ----------
        syllabus: str
            教学大纲全文
        chapter_name: Optional[str]
            篇章名称
        description: Optional[str]
            篇章描述
        stream_callback: Callable[[str], None] | None
            每次收到模型增量内容时回调，用于向前端推送流式数据
        """
        result = self.client.generate_mindmap_from_syllabus_stream(
            syllabus,
            chapter_name,
            description,
            stream_callback=stream_callback,
            extra_instructions=extra_instructions,
        )
        
        # 记录日志
        self._log_interaction("generate_mindmap_from_syllabus_stream", {
            "syllabus": syllabus,
            "chapter_name": chapter_name,
            "description": description,
            "extra_instructions": extra_instructions,
        }, result)
        
        return result
    
    def generate_task(self, level_name: str, level_description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """AI 生成关卡任务"""
        result = self.client.generate_task(level_name, level_description)
        
        self._log_interaction("generate_task", {
            "level_name": level_name,
            "level_description": level_description
        }, result)
        
        return result
    
    def generate_cards(self, task_name: str, task_description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """AI 生成知识卡片和技能卡片"""
        result = self.client.generate_cards(task_name, task_description)
        
        self._log_interaction("generate_cards", {
            "task_name": task_name,
            "task_description": task_description
        }, result)
        
        return result
    
    def generate_phases(self, task_name: str, task_description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """AI 生成任务操作环节步骤"""
        result = self.client.generate_phases(task_name, task_description)
        
        self._log_interaction("generate_phases", {
            "task_name": task_name,
            "task_description": task_description
        }, result)
        
        return result
    
    def generate_questions(self, level_name: str, knowledge_points: Optional[list] = None, skill_points: Optional[list] = None) -> Optional[Dict[str, Any]]:
        """AI 生成闯关考题"""
        result = self.client.generate_questions(level_name, knowledge_points, skill_points)
        
        self._log_interaction("generate_questions", {
            "level_name": level_name,
            "knowledge_points": knowledge_points,
            "skill_points": skill_points
        }, result)
        
        return result
    
    def generate_teaching_guide(
        self,
        task_name: str,
        course_name: Optional[str] = None,
        requirements: str = "",
        duration: Optional[str] = None,
        template_type: str = "standard",
        prompt: Optional[str] = None
    ) -> Optional[str]:
        """生成实验指导书（Markdown格式）
        
        Parameters
        ----------
        task_name : str
            任务名称
        course_name : Optional[str]
            课程/主题名称
        requirements : str
            任务要求
        duration : Optional[str]
            任务时长
        template_type : str
            模板类型（standard/simple/detailed）
        prompt : Optional[str]
            自定义提示词
        
        Returns
        -------
        Optional[str]
            生成的Markdown格式实验指导书
        """
        result = self.client.generate_teaching_guide(
            task_name=task_name,
            course_name=course_name,
            requirements=requirements,
            duration=duration,
            template_type=template_type,
            prompt=prompt
        )
        
        # 记录日志
        self._log_interaction("generate_teaching_guide", {
            "task_name": task_name,
            "course_name": course_name,
            "requirements": requirements,
            "duration": duration,
            "template_type": template_type
        }, {"content": result[:200] + "..." if result and len(result) > 200 else result})
        
        return result

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
        result = self.client.generate_teaching_guide_stream(
            task_name=task_name,
            course_name=course_name,
            requirements=requirements,
            duration=duration,
            template_type=template_type,
            prompt=prompt,
            stream_callback=stream_callback,
        )

        self._log_interaction(
            "generate_teaching_guide_stream",
            {
                "task_name": task_name,
                "course_name": course_name,
                "requirements_preview": requirements[:200],
                "duration": duration,
                "template_type": template_type,
            },
            {"content": result[:200] + "..." if result and len(result) > 200 else result},
        )

        return result

    def generate_teaching_requirements(
        self,
        task_name: str,
        course_name: Optional[str] = None,
        template_type: str = "standard",
    ) -> Optional[str]:
        """生成实验指导书中使用的「任务要求」段落（Markdown 文本）"""
        result = self.client.generate_teaching_requirements(
            task_name=task_name,
            course_name=course_name,
            template_type=template_type,
        )

        # 记录日志（只截取前 200 字符以避免过长）
        self._log_interaction(
            "generate_teaching_requirements",
            {
                "task_name": task_name,
                "course_name": course_name,
                "template_type": template_type,
            },
            {"requirements_preview": result[:200] + "..." if result and len(result) > 200 else result},
        )

        return result

    def generate_teaching_requirements_stream(
        self,
        task_name: str,
        course_name: Optional[str] = None,
        template_type: str = "standard",
        stream_callback=None,
    ) -> Optional[str]:
        """流式生成实验指导书中使用的「任务要求」段落（Markdown 文本）"""
        result = self.client.generate_teaching_requirements_stream(
            task_name=task_name,
            course_name=course_name,
            template_type=template_type,
            stream_callback=stream_callback,
        )

        self._log_interaction(
            "generate_teaching_requirements_stream",
            {
                "task_name": task_name,
                "course_name": course_name,
                "template_type": template_type,
            },
            {"requirements_preview": result[:200] + "..." if result and len(result) > 200 else result},
        )

        return result

    def generate_syllabus_stream(
        self,
        course_name: str,
        course_requirements: str,
        stream_callback=None,
    ) -> Optional[str]:
        """AI生成教学大纲（流式输出）
        
        参数：
        - course_name: 课程名称
        - course_requirements: 课程要求
        - stream_callback: 流式输出回调函数
        
        返回：
        - Markdown格式的教学大纲文本
        """
        result = self.client.generate_syllabus_stream(
            course_name,
            course_requirements,
            stream_callback=stream_callback,
        )
        
        # 记录日志
        self._log_interaction("generate_syllabus_stream", {
            "course_name": course_name,
            "course_requirements": course_requirements,
        }, result)
        
        return result
    
    def learning_help(self, question: str, context: Optional[str] = None) -> Optional[str]:
        """AI 学习助手（面向学生端的问答助手）"""
        result = self.client.learning_help(question, context)
        
        self._log_interaction("learning_help", {
            "question": question,
            "context": context
        }, {"response": result})
        
        return result

    def teaching_guide_to_course_json(self, markdown: str) -> Optional[Dict[str, Any]]:
        """将Markdown实验指导书转换为课程JSON（courseData）"""
        result = self.client.teaching_guide_to_course_json(markdown)
        self._log_interaction(
            "teaching_guide_to_course_json",
            {"markdown_preview": markdown[:200]},
            result,
        )
        return result

    def teaching_guide_to_course_json_stream(
        self,
        markdown: str,
        stream_callback=None,
    ) -> Optional[Dict[str, Any]]:
        """将Markdown实验指导书转换为课程JSON（courseData）（流式输出，支持长文分块）

        为避免单次调用超出大模型生成长度限制，这里会将 Markdown 按字符数切分为多个分块，
        逐块调用 AIClient.teaching_guide_to_course_json_stream，然后在服务端合并 steps。
        """

        def _split_markdown(md: str, max_chars: int = 4000) -> list[str]:
            lines = md.splitlines(keepends=True)
            chunks: list[str] = []
            current: list[str] = []
            current_len = 0

            for line in lines:
                # 尽量在段落/标题边界切分
                if current and current_len + len(line) > max_chars:
                    chunks.append("".join(current))
                    current = []
                    current_len = 0
                current.append(line)
                current_len += len(line)

            if current:
                chunks.append("".join(current))
            return chunks

        chunks = _split_markdown(markdown)
        total_chunks = len(chunks)

        merged: Dict[str, Any] = {"steps": []}

        for idx, chunk_md in enumerate(chunks):
            part_no = idx + 1
            if stream_callback:
                # 向上游输出分块进度日志
                stream_callback(f"[分块 {part_no}/{total_chunks}] 开始解析本部分教案内容...\n")

            partial = self.client.teaching_guide_to_course_json_stream(
                chunk_md,
                stream_callback=stream_callback,
            )

            if not partial or "steps" not in partial or not isinstance(partial["steps"], list):
                if stream_callback:
                    stream_callback(f"[分块 {part_no}/{total_chunks}] 未获得有效的 steps 结果，已跳过该分块。\n")
                continue

            for step in partial["steps"]:
                if not isinstance(step, dict):
                    continue
                orig_id = str(step.get("id") or f"step-{part_no}-{len(merged['steps']) + 1}")
                # 为避免多个分块之间 ID 冲突，统一加上前缀
                step["id"] = f"p{part_no}-{orig_id}"
                merged["steps"].append(step)

            if stream_callback:
                stream_callback(f"[分块 {part_no}/{total_chunks}] 已成功解析 {len(partial['steps'])} 个步骤。\n")

        result: Optional[Dict[str, Any]] = merged if merged["steps"] else None

        self._log_interaction(
            "teaching_guide_to_course_json_stream",
            {"markdown_preview": markdown[:200], "chunks": total_chunks},
            result,
        )
        return result

    def generate_data_file(
        self,
        task_name: str,
        data_requirements: str,
        file_format: str = "csv",
    ) -> Optional[str]:
        """根据教案中的数据要求生成示例数据文件内容"""
        result = self.client.generate_data_file(
            task_name=task_name,
            data_requirements=data_requirements,
            file_format=file_format,
        )

        self._log_interaction(
            "generate_data_file",
            {
                "task_name": task_name,
                "file_format": file_format,
                "data_requirements_preview": data_requirements[:200],
            },
            {"content_preview": result[:200] + "..." if result and len(result) > 200 else result},
        )

        return result

    def generate_data_file_stream(
        self,
        task_name: str,
        data_requirements: str,
        file_format: str = "csv",
        stream_callback=None,
    ) -> Optional[str]:
        """根据教案中的数据要求生成示例数据文件内容（流式输出）"""
        result = self.client.generate_data_file_stream(
            task_name=task_name,
            data_requirements=data_requirements,
            file_format=file_format,
            stream_callback=stream_callback,
        )

        self._log_interaction(
            "generate_data_file_stream",
            {
                "task_name": task_name,
                "file_format": file_format,
                "data_requirements_preview": data_requirements[:200],
            },
            {"content_preview": result[:200] + "..." if result and len(result) > 200 else result},
        )

        return result
    
    def _log_interaction(self, action: str, input_data: dict, output_data: Any):
        """记录 AI 交互日志

        日志写入失败时**不会中断主流程**，仅打印 warning。
        """
        try:
            log = AIAssistantLog(
                action=action,
                input_data=input_data,
                output_data=output_data
            )
            self.db.add(log)
            self.db.commit()
        except Exception as e:
            # 日志记录失败不影响主流程
            import logging
            logging.getLogger(__name__).warning(f"Failed to log AI interaction: {e}")

