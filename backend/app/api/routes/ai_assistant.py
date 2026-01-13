"""
AI助理API
"""
import logging
import json
import os
from pathlib import Path
from flask import Blueprint, jsonify, request, Response, stream_with_context, send_from_directory

from ...core.security import login_required
from flask import g
from ...db.session import get_db
from ...services.ai_service import AIService

ai_assistant_bp = Blueprint("ai_assistant", __name__, url_prefix="/api/v1/ai-assistant")
logger = logging.getLogger(__name__)


@ai_assistant_bp.route("/generate-mindmap", methods=["POST"])
@login_required
def generate_mindmap():
    """AI生成思维导图（支持教学大纲解析和流式输出）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        current_user = g.current_user
        # 只有教师和管理员可以使用AI助理
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403
        
        # 检查是否启用流式输出
        stream = data.get("stream", False)
        syllabus = data.get("syllabus", "")
        chapter_name = data.get("chapter_name", "")
        description = data.get("description")
        extra_instructions = data.get("extra_instructions")
        knowledge_points = data.get("knowledge_points", [])
        
        if not syllabus and not chapter_name:
            return jsonify({"detail": "篇章名称或教学大纲不能为空"}), 400
        
        db = get_db()
        ai_service = AIService(db)
        
        # 如果启用流式输出且提供了教学大纲
        if stream and syllabus:
            def generate():
                try:
                    # 发送开始消息
                    yield f"data: {json.dumps({'type': 'start', 'message': '开始分析教学大纲...'})}\n\n"
                    
                    # 使用队列来收集流式内容
                    import queue
                    import threading
                    content_queue = queue.Queue()
                    result_container = {'result': None, 'error': None, 'finished': False}
                    
                    def stream_callback(content: str):
                        # 将内容放入队列
                        content_queue.put(('content', content))
                    
                    def run_ai():
                        try:
                            result = ai_service.generate_mindmap_from_syllabus_stream(
                                syllabus,
                                chapter_name,
                                description,
                                stream_callback=stream_callback,
                                extra_instructions=extra_instructions,
                            )
                            result_container['result'] = result
                        except Exception as e:
                            result_container['error'] = str(e)
                            logger.error(f"Error in AI generation: {e}", exc_info=True)
                        finally:
                            result_container['finished'] = True
                            content_queue.put(('done', None))
                    
                    # 启动AI生成线程
                    ai_thread = threading.Thread(target=run_ai, daemon=True)
                    ai_thread.start()
                    
                    # 实时发送流式内容
                    while not result_container['finished'] or not content_queue.empty():
                        try:
                            item_type, content = content_queue.get(timeout=0.1)
                            if item_type == 'content':
                                yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                            elif item_type == 'done':
                                break
                        except queue.Empty:
                            # 继续等待
                            import time
                            time.sleep(0.05)
                    
                    # 等待线程完成
                    ai_thread.join(timeout=30)
                    
                    # 发送最终结果
                    if result_container['error']:
                        yield f"data: {json.dumps({'type': 'error', 'message': result_container['error']})}\n\n"
                    elif result_container['result']:
                        yield f"data: {json.dumps({'type': 'result', 'data': result_container['result']})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'error', 'message': 'AI生成失败，请检查输入内容'})}\n\n"
                except Exception as e:
                    logger.error(f"Error in stream generation: {e}", exc_info=True)
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            
            return Response(
                stream_with_context(generate()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Connection': 'keep-alive'
                }
            )
        else:
            # 非流式输出
            if syllabus:
                result = ai_service.generate_mindmap_from_syllabus(
                    syllabus, chapter_name, description, extra_instructions=extra_instructions
                )
            else:
                result = ai_service.generate_mindmap(chapter_name, description, knowledge_points)
            
            if result:
                return jsonify(result), 200
            else:
                return jsonify({"detail": "AI生成失败，请检查配置或稍后重试"}), 500
    except Exception as e:
        logger.error(f"Error generating mindmap: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/generate-task", methods=["POST"])
@login_required
def generate_task():
    """AI生成关卡任务"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        current_user = g.current_user
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403
        
        db = get_db()
        ai_service = AIService(db)
        
        level_name = data.get("level_name", "")
        level_description = data.get("level_description")
        
        if not level_name:
            return jsonify({"detail": "关卡名称不能为空"}), 400
        
        result = ai_service.generate_task(level_name, level_description)
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"detail": "AI生成失败，请检查配置或稍后重试"}), 500
    except Exception as e:
        logger.error(f"Error generating task: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/generate-cards", methods=["POST"])
@login_required
def generate_cards():
    """AI生成知识/技能卡片"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        current_user = g.current_user
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403
        
        db = get_db()
        ai_service = AIService(db)
        
        task_name = data.get("task_name", "")
        task_description = data.get("task_description")
        
        if not task_name:
            return jsonify({"detail": "任务名称不能为空"}), 400
        
        result = ai_service.generate_cards(task_name, task_description)
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"detail": "AI生成失败，请检查配置或稍后重试"}), 500
    except Exception as e:
        logger.error(f"Error generating cards: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/generate-phases", methods=["POST"])
@login_required
def generate_phases():
    """AI生成环节步骤"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        current_user = g.current_user
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403
        
        db = get_db()
        ai_service = AIService(db)
        
        task_name = data.get("task_name", "")
        task_description = data.get("task_description")
        
        if not task_name:
            return jsonify({"detail": "任务名称不能为空"}), 400
        
        result = ai_service.generate_phases(task_name, task_description)
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"detail": "AI生成失败，请检查配置或稍后重试"}), 500
    except Exception as e:
        logger.error(f"Error generating phases: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/generate-questions", methods=["POST"])
@login_required
def generate_questions():
    """AI生成闯关考题"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        current_user = g.current_user
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403
        
        db = get_db()
        ai_service = AIService(db)
        
        level_name = data.get("level_name", "")
        knowledge_points = data.get("knowledge_points", [])
        skill_points = data.get("skill_points", [])
        
        if not level_name:
            return jsonify({"detail": "关卡名称不能为空"}), 400
        
        result = ai_service.generate_questions(level_name, knowledge_points, skill_points)
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"detail": "AI生成失败，请检查配置或稍后重试"}), 500
    except Exception as e:
        logger.error(f"Error generating questions: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/generate-teaching-guide", methods=["POST"])
@login_required
def generate_teaching_guide():
    """AI生成实验指导书（Markdown格式）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        current_user = g.current_user
        # 只有教师和管理员可以使用AI助理
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403
        
        task_name = data.get("task_name", "")
        course_name = data.get("course_name")
        requirements = data.get("requirements", "")
        duration = data.get("duration")
        template_type = data.get("template_type", "standard")
        prompt = data.get("prompt")
        
        if not task_name or not requirements:
            return jsonify({"detail": "任务名称和任务要求不能为空"}), 400
        
        db = get_db()
        ai_service = AIService(db)
        
        content = ai_service.generate_teaching_guide(
            task_name=task_name,
            course_name=course_name,
            requirements=requirements,
            duration=duration,
            template_type=template_type,
            prompt=prompt
        )
        
        if not content:
            return jsonify({"detail": "生成失败，请稍后重试"}), 500
        
        return jsonify({"content": content}), 200
    except Exception as e:
        logger.error(f"Error generating teaching guide: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/generate-teaching-guide-stream", methods=["POST"])
@login_required
def generate_teaching_guide_stream():
    """AI生成实验指导书（Markdown格式，SSE 流式输出日志与最终结果）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        # 只有教师和管理员可以使用AI助理
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403

        task_name = data.get("task_name", "").strip()
        course_name = (data.get("course_name") or "").strip() or None
        requirements = data.get("requirements", "")
        duration = (data.get("duration") or "").strip() or None
        template_type = (data.get("template_type") or "standard").strip() or "standard"
        prompt = data.get("prompt")

        if not task_name or not requirements:
            return jsonify({"detail": "任务名称和任务要求不能为空"}), 400

        db = get_db()
        ai_service = AIService(db)

        def generate():
            try:
                # 发送开始消息
                yield f"data: {json.dumps({'type': 'start', 'message': '开始生成教案...'})}\n\n"

                import queue
                import threading

                content_queue: "queue.Queue[tuple[str, str | None]]" = queue.Queue()
                result_container = {"result": None, "error": None, "finished": False}

                def stream_callback(chunk: str):
                    # 将大模型增量内容放入队列
                    content_queue.put(("content", chunk))

                def run_ai():
                    try:
                        result = ai_service.generate_teaching_guide_stream(
                            task_name=task_name,
                            course_name=course_name,
                            requirements=requirements,
                            duration=duration,
                            template_type=template_type,
                            prompt=prompt,
                            stream_callback=stream_callback,
                        )
                        result_container["result"] = result
                    except Exception as e:
                        result_container["error"] = str(e)
                        logger.error(f"Error in generate_teaching_guide_stream: {e}", exc_info=True)
                    finally:
                        result_container["finished"] = True
                        content_queue.put(("done", None))

                ai_thread = threading.Thread(target=run_ai, daemon=True)
                ai_thread.start()

                # 实时发送内容
                while True:
                    try:
                        item_type, content = content_queue.get(timeout=1)
                        if item_type == "content" and content:
                            yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                        elif item_type == "done":
                            break
                    except queue.Empty:
                        if result_container["finished"]:
                            break
                        continue

                ai_thread.join(timeout=120)

                if result_container["error"]:
                    yield f"data: {json.dumps({'type': 'error', 'message': result_container['error']})}\n\n"
                elif result_container["result"]:
                    yield f"data: {json.dumps({'type': 'result', 'content': result_container['result']})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': '生成失败'})}\n\n"
            except Exception as e:
                logger.error(f"Error in generate_teaching_guide_stream: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        logger.error(f"Error in generate_teaching_guide_stream entry: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

@ai_assistant_bp.route("/generate-teaching-requirements", methods=["POST"])
@login_required
def generate_teaching_requirements():
    """AI 生成实验指导书中的「任务要求」段落（Markdown 文本）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        # 只有教师和管理员可以使用AI助理
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403

        task_name = (data.get("task_name") or "").strip()
        course_name = (data.get("course_name") or "").strip() or None
        template_type = (data.get("template_type") or "standard").strip() or "standard"

        if not task_name:
            return jsonify({"detail": "任务名称不能为空"}), 400

        db = get_db()
        ai_service = AIService(db)

        requirements = ai_service.generate_teaching_requirements(
            task_name=task_name,
            course_name=course_name,
            template_type=template_type,
        )

        if not requirements:
            return jsonify({"detail": "生成任务要求失败，请稍后重试"}), 500

        return jsonify({"requirements": requirements}), 200
    except Exception as e:
        logger.error(f"Error generating teaching requirements: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/generate-teaching-requirements-stream", methods=["POST"])
@login_required
def generate_teaching_requirements_stream():
    """AI 流式生成「任务要求」段落（Markdown 文本），并通过 SSE 输出进度日志"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        # 只有教师和管理员可以使用AI助理
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403

        task_name = (data.get("task_name") or "").strip()
        course_name = (data.get("course_name") or "").strip() or None
        template_type = (data.get("template_type") or "standard").strip() or "standard"

        if not task_name:
            return jsonify({"detail": "任务名称不能为空"}), 400

        db = get_db()
        ai_service = AIService(db)

        def generate():
            try:
                # 发送开始消息
                yield f"data: {json.dumps({'type': 'start', 'message': '开始生成任务要求...'})}\n\n"

                import queue
                import threading

                content_queue: "queue.Queue[tuple[str, str | None]]" = queue.Queue()
                result_container = {"result": None, "error": None, "finished": False}

                def stream_callback(chunk: str):
                    content_queue.put(("content", chunk))

                def run_ai():
                    try:
                        result = ai_service.generate_teaching_requirements_stream(
                            task_name=task_name,
                            course_name=course_name,
                            template_type=template_type,
                            stream_callback=stream_callback,
                        )
                        result_container["result"] = result
                    except Exception as e:
                        result_container["error"] = str(e)
                        logger.error(
                            f"Error in generate_teaching_requirements_stream: {e}",
                            exc_info=True,
                        )
                    finally:
                        result_container["finished"] = True
                        content_queue.put(("done", None))

                ai_thread = threading.Thread(target=run_ai, daemon=True)
                ai_thread.start()

                while True:
                    try:
                        item_type, content = content_queue.get(timeout=1)
                        if item_type == "content" and content:
                            yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                        elif item_type == "done":
                            break
                    except queue.Empty:
                        if result_container["finished"]:
                            break
                        continue

                ai_thread.join(timeout=60)

                if result_container["error"]:
                    yield f"data: {json.dumps({'type': 'error', 'message': result_container['error']})}\n\n"
                elif result_container["result"]:
                    yield f"data: {json.dumps({'type': 'result', 'requirements': result_container['result']})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': '生成任务要求失败'})}\n\n"
            except Exception as e:
                logger.error(f"Error in generate_teaching_requirements_stream: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        logger.error(f"Error in generate_teaching_requirements_stream entry: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/generate-data-file", methods=["POST"])
@login_required
def generate_data_file():
    """根据教案中的数据要求生成示例数据文件内容（csv/json/txt）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        # 只有教师和管理员可以使用AI助理
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403

        task_name = (data.get("task_name") or "").strip()
        data_requirements = (data.get("data_requirements") or "").strip()
        file_format = (data.get("file_format") or "csv").strip().lower() or "csv"

        if not task_name:
            return jsonify({"detail": "任务名称不能为空"}), 400
        if not data_requirements:
            return jsonify({"detail": "数据要求不能为空"}), 400

        if file_format not in ["csv", "json", "txt"]:
            file_format = "csv"

        db = get_db()
        ai_service = AIService(db)

        content = ai_service.generate_data_file(
            task_name=task_name,
            data_requirements=data_requirements,
            file_format=file_format,
        )

        if not content:
            return jsonify({"detail": "生成数据文件失败，请稍后重试"}), 500

        # 简单生成一个推荐的文件名
        safe_task_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in task_name)[:50] or "data"
        ext = "csv" if file_format == "csv" else "json" if file_format == "json" else "txt"
        filename = f"{safe_task_name}_sample.{ext}"

        # 将文件写入 backend/data/generated 目录下
        project_root = Path(__file__).resolve().parents[3]
        data_dir = project_root / "data" / "generated"
        data_dir.mkdir(parents=True, exist_ok=True)
        file_path = data_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # 构造可在 Markdown 中引用的 URL
        base_url = request.host_url.rstrip("/")
        file_url = f"{base_url}/api/v1/ai-assistant/data-files/{filename}"

        return jsonify(
            {
                "filename": filename,
                "content": content,
                "file_format": file_format,
                "url": file_url,
            }
        ), 200
    except Exception as e:
        logger.error(f"Error generating data file: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/generate-data-file-stream", methods=["POST"])
@login_required
def generate_data_file_stream():
    """根据教案中的数据要求生成示例数据文件内容（csv/json/txt），并通过 SSE 输出流式日志"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403

        task_name = (data.get("task_name") or "").strip()
        data_requirements = (data.get("data_requirements") or "").strip()
        file_format = (data.get("file_format") or "csv").strip().lower() or "csv"

        if not task_name:
            return jsonify({"detail": "任务名称不能为空"}), 400
        if not data_requirements:
            return jsonify({"detail": "数据要求不能为空"}), 400
        if file_format not in ["csv", "json", "txt"]:
            file_format = "csv"

        db = get_db()
        ai_service = AIService(db)

        def generate():
            try:
                # 发送开始消息
                yield f"data: {json.dumps({'type': 'start', 'message': '开始根据教案生成示例数据文件...'})}\n\n"

                import queue
                import threading

                content_queue: 'queue.Queue[tuple[str, str | None]]' = queue.Queue()
                result_container = {'result': None, 'error': None, 'finished': False}

                def stream_callback(chunk: str):
                    content_queue.put(('content', chunk))

                def run_ai():
                    try:
                        result = ai_service.generate_data_file_stream(
                            task_name=task_name,
                            data_requirements=data_requirements,
                            file_format=file_format,
                            stream_callback=stream_callback,
                        )
                        result_container['result'] = result
                    except Exception as e:
                        result_container['error'] = str(e)
                        logger.error(f"Error in generate_data_file_stream: {e}", exc_info=True)
                    finally:
                        result_container['finished'] = True
                        content_queue.put(('done', None))

                ai_thread = threading.Thread(target=run_ai, daemon=True)
                ai_thread.start()

                while True:
                    try:
                        item_type, content = content_queue.get(timeout=1)
                        if item_type == 'content' and content:
                            yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                        elif item_type == 'done':
                            break
                    except queue.Empty:
                        if result_container['finished']:
                            break
                        continue

                ai_thread.join(timeout=120)

                if result_container['error']:
                    yield f"data: {json.dumps({'type': 'error', 'message': result_container['error']})}\n\n"
                elif result_container['result']:
                    content = result_container['result']
                    if not content:
                        yield f"data: {json.dumps({'type': 'error', 'message': '生成数据文件失败，请稍后重试'})}\n\n"
                        return

                    # 写入文件并返回 URL（与非流式接口保持一致）
                    project_root = Path(__file__).resolve().parents[3]
                    data_dir = project_root / "data" / "generated"
                    data_dir.mkdir(parents=True, exist_ok=True)

                    safe_task_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in task_name)[:50] or "data"
                    ext = "csv" if file_format == "csv" else "json" if file_format == "json" else "txt"
                    filename = f"{safe_task_name}_sample.{ext}"
                    file_path = data_dir / filename
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    base_url = request.host_url.rstrip("/")
                    file_url = f"{base_url}/api/v1/ai-assistant/data-files/{filename}"

                    yield f"data: {json.dumps({'type': 'result', 'filename': filename, 'file_format': file_format, 'url': file_url})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': '生成数据文件失败，请稍后重试'})}\n\n"
            except Exception as e:
                logger.error(f"Error in generate_data_file_stream: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        logger.error(f"Error in generate_data_file_stream entry: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/data-files/<path:filename>", methods=["GET"])
def get_data_file(filename: str):
    """提供生成的数据文件下载/访问接口，支持在 Markdown 中通过 URL 访问

    说明：该链接需要能被浏览器/Markdown 直接打开，因此这里不做登录校验。
    若后续需要权限控制，可改为短期签名 URL 或带 token 的一次性链接。
    """
    safe_name = os.path.basename(filename)
    project_root = Path(__file__).resolve().parents[3]
    data_dir = project_root / "data" / "generated"
    if not (data_dir / safe_name).exists():
        return jsonify({"detail": "文件不存在"}), 404

    return send_from_directory(data_dir, safe_name, as_attachment=False)

@ai_assistant_bp.route("/generate-syllabus", methods=["POST"])
@login_required
def generate_syllabus():
    """AI生成教学大纲（流式输出，返回Markdown格式）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        current_user = g.current_user
        # 只有教师和管理员可以使用AI助理
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403
        
        course_name = data.get("course_name", "").strip()
        course_requirements = data.get("course_requirements", "").strip()
        stream = data.get("stream", False)
        
        if not course_name or not course_requirements:
            return jsonify({"detail": "课程名称和课程要求不能为空"}), 400
        
        db = get_db()
        ai_service = AIService(db)
        
        # 如果启用流式输出
        if stream:
            def generate():
                try:
                    # 发送开始消息
                    yield f"data: {json.dumps({'type': 'start', 'message': '开始生成教学大纲...'})}\n\n"
                    
                    # 使用队列来收集流式内容
                    import queue
                    import threading
                    content_queue = queue.Queue()
                    result_container = {'result': None, 'error': None, 'finished': False}
                    
                    def stream_callback(content: str):
                        # 将内容放入队列
                        content_queue.put(('content', content))
                    
                    def run_ai():
                        try:
                            result = ai_service.generate_syllabus_stream(
                                course_name,
                                course_requirements,
                                stream_callback=stream_callback,
                            )
                            result_container['result'] = result
                        except Exception as e:
                            result_container['error'] = str(e)
                            logger.error(f"Error in AI generation: {e}", exc_info=True)
                        finally:
                            result_container['finished'] = True
                            content_queue.put(('done', None))
                    
                    # 启动AI生成线程
                    ai_thread = threading.Thread(target=run_ai, daemon=True)
                    ai_thread.start()
                    
                    # 从队列中读取内容并发送
                    while True:
                        try:
                            item = content_queue.get(timeout=1)
                            if item[0] == 'content':
                                yield f"data: {json.dumps({'type': 'content', 'content': item[1]})}\n\n"
                            elif item[0] == 'done':
                                break
                        except queue.Empty:
                            if result_container['finished']:
                                break
                            continue
                    
                    # 发送结果
                    if result_container['error']:
                        yield f"data: {json.dumps({'type': 'error', 'message': result_container['error']})}\n\n"
                    elif result_container['result']:
                        yield f"data: {json.dumps({'type': 'result', 'data': result_container['result']})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'error', 'message': '生成失败'})}\n\n"
                        
                except Exception as e:
                    logger.error(f"Error in stream generation: {e}", exc_info=True)
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            
            return Response(
                stream_with_context(generate()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )
        else:
            # 非流式输出
            result = ai_service.generate_syllabus_stream(
                course_name,
                course_requirements,
            )
            
            if result:
                return jsonify({"syllabus": result}), 200
            else:
                return jsonify({"detail": "生成失败"}), 500
                
    except Exception as e:
        logger.error(f"Error generating syllabus: {e}", exc_info=True)
        return jsonify({"detail": f"生成失败: {str(e)}"}), 500


@ai_assistant_bp.route("/learning-help", methods=["POST"])
@login_required
def learning_help():
    """AI学习助手（学生端）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        current_user = g.current_user
        db = get_db()
        ai_service = AIService(db)
        
        question = data.get("question", "")
        context = data.get("context")
        
        if not question:
            return jsonify({"detail": "问题不能为空"}), 400
        
        result = ai_service.learning_help(question, context)
        
        if result:
            return jsonify({"answer": result}), 200
        else:
            return jsonify({"detail": "AI助手暂时无法回答，请稍后重试"}), 500
    except Exception as e:
        logger.error(f"Error in learning help: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/teaching-guide-to-course-json", methods=["POST"])
@login_required
def teaching_guide_to_course_json():
    """将Markdown教案转换为固定结构的课程JSON（courseData）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        current_user = g.current_user
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403
        
        markdown = data.get("markdown", "")
        if not markdown or not markdown.strip():
            return jsonify({"detail": "markdown 内容不能为空"}), 400
        
        db = get_db()
        ai_service = AIService(db)
        result = ai_service.teaching_guide_to_course_json(markdown)
        
        if not result:
            return jsonify({"detail": "大模型转换失败，请稍后重试"}), 500
        
        # 简单校验：必须包含 steps 数组
        if "steps" not in result or not isinstance(result["steps"], list):
            return jsonify({"detail": "AI 返回的结构不符合约定，请检查 Prompt 或稍后重试"}), 500
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error converting teaching guide to course json: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@ai_assistant_bp.route("/teaching-guide-to-course-json-stream", methods=["POST"])
@login_required
def teaching_guide_to_course_json_stream():
    """将Markdown教案转换为课程JSON（courseData），并通过SSE流式返回中间日志与最终结果"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        current_user = g.current_user
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以使用AI助理"}), 403
        
        markdown = data.get("markdown", "")
        if not markdown or not markdown.strip():
            return jsonify({"detail": "markdown 内容不能为空"}), 400
        
        db = get_db()
        ai_service = AIService(db)

        def generate():
            try:
                # 发送开始消息
                yield f"data: {json.dumps({'type': 'start', 'message': '开始调用大模型，解析 Markdown 教案并生成交互式关卡 JSON ...'})}\n\n"

                import queue
                import threading
                content_queue: "queue.Queue[tuple[str, str | None]]" = queue.Queue()
                result_container = {"result": None, "error": None, "finished": False}

                def stream_callback(chunk: str):
                    # 将大模型的增量内容放入队列
                    content_queue.put(("content", chunk))

                def run_ai():
                    try:
                        result = ai_service.teaching_guide_to_course_json_stream(
                            markdown=markdown,
                            stream_callback=stream_callback,
                        )
                        result_container["result"] = result
                    except Exception as e:
                        result_container["error"] = str(e)
                        logger.error(f"Error in teaching_guide_to_course_json_stream: {e}", exc_info=True)
                    finally:
                        result_container["finished"] = True
                        content_queue.put(("done", None))

                ai_thread = threading.Thread(target=run_ai, daemon=True)
                ai_thread.start()

                # 实时发送内容
                while True:
                    try:
                        item_type, content = content_queue.get(timeout=1)
                        if item_type == "content" and content:
                            # 为避免日志过长，可按需截断单次片段
                            yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                        elif item_type == "done":
                            break
                    except queue.Empty:
                        if result_container["finished"]:
                            break
                        continue

                ai_thread.join(timeout=60)

                if result_container["error"]:
                    yield f"data: {json.dumps({'type': 'error', 'message': result_container['error']})}\n\n"
                elif result_container["result"]:
                    result = result_container["result"]
                    # 简单校验：必须包含 steps 数组
                    if "steps" not in result or not isinstance(result["steps"], list):
                        yield f"data: {json.dumps({'type': 'error', 'message': 'AI 返回的结构不符合约定，请检查 Prompt 或稍后重试'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'result', 'data': result})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': '大模型转换失败，请稍后重试'})}\n\n"
            except Exception as e:
                logger.error(f"Error in teaching_guide_to_course_json_stream: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        logger.error(f"Error in teaching_guide_to_course_json_stream entry: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

