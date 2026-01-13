"""
从Markdown文件导入课程数据的工具脚本
使用方法：python import_from_md.py
"""

import re
import json
from app import app, db
from models import Course, Task, Operation, KnowledgeCard, InstantQuestion

def parse_markdown_file(file_path):
    """解析Markdown文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取任务标题
    title_match = re.search(r'# (.*?)\n', content)
    task_name = title_match.group(1) if title_match else '未命名任务'

    # 提取学习目标
    goals_section = re.search(r'## 📌 学习目标(.*?)---', content, re.DOTALL)

    # 提取任务时间
    time_match = re.search(r'总时长.*?(\d+)分钟', content)
    time_limit = int(time_match.group(1)) if time_match else 90

    # 提取操作步骤
    operations = parse_operations(content)

    return {
        'task_name': task_name.replace('任务2:', '').replace('：', '').strip(),
        'time_limit': time_limit,
        'operations': operations
    }

def parse_operations(content):
    """解析操作步骤"""
    operations = []

    # 匹配操作章节
    operation_pattern = r'#### 操作(\d+)：(.*?)\（'
    operation_matches = re.finditer(operation_pattern, content)

    for match in operation_matches:
        op_num = int(match.group(1))
        op_name = match.group(2).strip()

        # 查找该操作的内容
        op_start = match.end()
        next_op_match = re.search(r'#### 操作\d+：', content[op_start:])
        op_end = op_start + next_op_match.start() if next_op_match else len(content)
        op_content = content[op_start:op_end]

        # 提取操作说明
        desc_match = re.search(r'操作方法：(.*?)(?=练习任务：|$)', op_content, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ''

        # 提取步骤
        steps = extract_steps(op_content)

        # 提取练习任务
        practice_match = re.search(r'练习任务：(.*?)(?=---|####|$)', op_content, re.DOTALL)
        practice_task = practice_match.group(1).strip() if practice_match else ''

        # 提取课堂问答
        questions = extract_questions(op_content)

        # 提取知识卡片
        knowledge_cards = extract_knowledge_cards(op_content, op_name)

        operations.append({
            'operation_code': f'OP-{op_num:02d}',
            'operation_name': op_name,
            'operation_order': op_num,
            'description': description[:500],
            'steps': steps,
            'practice_task': practice_task,
            'questions': questions,
            'knowledge_cards': knowledge_cards
        })

    return operations

def extract_steps(content):
    """提取操作步骤"""
    steps = []

    # 匹配步骤
    step_pattern = r'步骤：\n(.*?)(?=\*\*|练习任务|$)'
    step_matches = re.finditer(step_pattern, content, re.DOTALL)

    for match in step_matches:
        step_content = match.group(1)
        # 提取编号步骤
        numbered_steps = re.findall(r'(\d+)\.\s+(.*?)(?=\n\d+\.|$)', step_content, re.DOTALL)
        for num, step_text in numbered_steps:
            steps.append(step_text.strip())

    return steps[:10]  # 最多10个步骤

def extract_questions(content):
    """提取课堂问答题"""
    questions = []

    # 匹配问题
    question_pattern = r'\*\*问题(\d+)：\*\* (.*?)\n\n(A\..*?)\n(B\..*?)\n(C\..*?)\n(D\..*?)\n\n\*\*正确答案：([A-D])\*\*\n\n\*\*解析：\*\* (.*?)(?=---|$)'
    question_matches = re.finditer(question_pattern, content, re.DOTALL)

    for match in question_matches:
        questions.append({
            'question_text': match.group(2).strip(),
            'option_a': match.group(3).replace('A. ', '').strip(),
            'option_b': match.group(4).replace('B. ', '').strip(),
            'option_c': match.group(5).replace('C. ', '').strip(),
            'option_d': match.group(6).replace('D. ', '').strip(),
            'correct_answer': match.group(7).strip(),
            'explanation': match.group(8).strip()
        })

    return questions

def extract_knowledge_cards(content, operation_name):
    """提取知识卡片"""
    cards = []

    # 从操作说明中提取提示
    tip_pattern = r'\*\*💡 提示：\*\*\n(.*?)(?=\n\n|$)'
    tip_matches = re.finditer(tip_pattern, content, re.DOTALL)

    for match in tip_matches:
        tip_text = match.group(1).strip()
        cards.append({
            'card_title': f'{operation_name}小技巧',
            'card_content': tip_text,
            'card_type': 'tip',
            'trigger_timing': 'after'
        })

    return cards

def import_data(md_file_path):
    """导入数据到数据库"""
    with app.app_context():
        # 解析Markdown文件
        print('正在解析Markdown文件...')
        data = parse_markdown_file(md_file_path)

        # 创建或获取课程
        course = Course.query.filter_by(course_code='COURSE-01').first()
        if not course:
            course = Course(
                course_code='COURSE-01',
                course_name='玩转数据从个人生活开始',
                description='大数据课程第一课'
            )
            db.session.add(course)
            db.session.commit()
            print(f'✓ 创建课程: {course.course_name}')

        # 创建任务
        task = Task(
            course_id=course.id,
            task_code='TASK-02',
            task_name=data['task_name'],
            task_order=2,
            total_operations=len(data['operations']),
            total_questions=sum(len(op['questions']) for op in data['operations']),
            time_limit=data['time_limit']
        )
        db.session.add(task)
        db.session.commit()
        print(f'✓ 创建任务: {task.task_name}')

        # 创建操作
        for op_data in data['operations']:
            operation = Operation(
                task_id=task.id,
                operation_code=op_data['operation_code'],
                operation_name=op_data['operation_name'],
                operation_order=op_data['operation_order'],
                description=op_data['description'],
                steps=json.dumps(op_data['steps'], ensure_ascii=False),
                practice_task=op_data['practice_task'],
                points=10
            )
            db.session.add(operation)
            db.session.commit()
            print(f'  ✓ 创建操作 {operation.operation_order}: {operation.operation_name}')

            # 创建知识卡片
            for card_data in op_data['knowledge_cards']:
                card = KnowledgeCard(
                    operation_id=operation.id,
                    card_title=card_data['card_title'],
                    card_content=card_data['card_content'],
                    card_type=card_data['card_type'],
                    trigger_timing=card_data['trigger_timing']
                )
                db.session.add(card)

            # 创建即时测试题
            for q_data in op_data['questions']:
                question = InstantQuestion(
                    operation_id=operation.id,
                    question_text=q_data['question_text'],
                    option_a=q_data['option_a'],
                    option_b=q_data['option_b'],
                    option_c=q_data['option_c'],
                    option_d=q_data['option_d'],
                    correct_answer=q_data['correct_answer'],
                    explanation=q_data['explanation'],
                    points=5
                )
                db.session.add(question)

            db.session.commit()
            print(f'    ✓ 创建 {len(op_data["knowledge_cards"])} 个知识卡片')
            print(f'    ✓ 创建 {len(op_data["questions"])} 道测试题')

        print('\n✅ 数据导入完成！')
        print(f'任务: {task.task_name}')
        print(f'操作数: {len(data["operations"])}')
        print(f'总题数: {task.total_questions}')

if __name__ == '__main__':
    import sys

    # Markdown文件路径
    md_file = '../md文档/课程1-玩转数据从个人生活开始/任务2-Excel界面速通-实验指导书.md'

    if len(sys.argv) > 1:
        md_file = sys.argv[1]

    try:
        import_data(md_file)
    except Exception as e:
        print(f'❌ 导入失败: {e}')
        import traceback
        traceback.print_exc()
