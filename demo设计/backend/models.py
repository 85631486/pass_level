"""
数据库模型定义
"""

from datetime import datetime
from app import db


class Student(db.Model):
    """学生表"""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Course(db.Model):
    """课程表"""
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(50), unique=True, nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'description': self.description
        }


class Task(db.Model):
    """任务表"""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    task_code = db.Column(db.String(50), nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    task_order = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text)  # JSON格式
    total_operations = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    time_limit = db.Column(db.Integer)  # 分钟
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'task_code': self.task_code,
            'task_name': self.task_name,
            'task_order': self.task_order,
            'total_operations': self.total_operations,
            'total_questions': self.total_questions,
            'time_limit': self.time_limit
        }


class Operation(db.Model):
    """操作步骤表"""
    __tablename__ = 'operations'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    operation_code = db.Column(db.String(50), nullable=False)
    operation_name = db.Column(db.String(200), nullable=False)
    operation_order = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    steps = db.Column(db.Text)  # JSON格式
    practice_task = db.Column(db.Text)
    points = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'task_id': self.task_id,
            'operation_code': self.operation_code,
            'operation_name': self.operation_name,
            'operation_order': self.operation_order,
            'description': self.description,
            'steps': json.loads(self.steps) if self.steps else [],
            'practice_task': self.practice_task,
            'points': self.points
        }


class KnowledgeCard(db.Model):
    """知识卡片表"""
    __tablename__ = 'knowledge_cards'

    id = db.Column(db.Integer, primary_key=True)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'), nullable=False)
    card_title = db.Column(db.String(200), nullable=False)
    card_content = db.Column(db.Text, nullable=False)
    card_type = db.Column(db.String(50), default='tip')
    trigger_timing = db.Column(db.String(50), default='after')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'operation_id': self.operation_id,
            'card_title': self.card_title,
            'card_content': self.card_content,
            'card_type': self.card_type,
            'trigger_timing': self.trigger_timing
        }


class InstantQuestion(db.Model):
    """即时测试题表"""
    __tablename__ = 'instant_questions'

    id = db.Column(db.Integer, primary_key=True)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.Text)
    points = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self, include_answer=True):
        data = {
            'id': self.id,
            'operation_id': self.operation_id,
            'question_text': self.question_text,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'points': self.points
        }
        if include_answer:
            data['correct_answer'] = self.correct_answer
            data['explanation'] = self.explanation
        return data


class UnifiedQuestion(db.Model):
    """统一测试题表"""
    __tablename__ = 'unified_questions'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.Text)
    points = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self, include_answer=True):
        data = {
            'id': self.id,
            'task_id': self.task_id,
            'question_text': self.question_text,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'points': self.points
        }
        if include_answer:
            data['correct_answer'] = self.correct_answer
            data['explanation'] = self.explanation
        return data


class Badge(db.Model):
    """成就徽章表"""
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    badge_code = db.Column(db.String(50), unique=True, nullable=False)
    badge_name = db.Column(db.String(100), nullable=False)
    badge_icon = db.Column(db.String(200))
    badge_description = db.Column(db.Text)
    unlock_condition = db.Column(db.Text)  # JSON格式
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'badge_code': self.badge_code,
            'badge_name': self.badge_name,
            'badge_icon': self.badge_icon,
            'badge_description': self.badge_description
        }


class StudentProgress(db.Model):
    """学生学习进度表"""
    __tablename__ = 'student_progress'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    status = db.Column(db.String(50), default='not_started')
    total_points = db.Column(db.Integer, default=0)
    current_operation = db.Column(db.Integer, default=0)
    operations_completed = db.Column(db.Integer, default=0)
    questions_correct = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime)
    complete_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (db.UniqueConstraint('student_id', 'task_id'),)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'task_id': self.task_id,
            'status': self.status,
            'total_points': self.total_points,
            'current_operation': self.current_operation,
            'operations_completed': self.operations_completed,
            'questions_correct': self.questions_correct,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'complete_time': self.complete_time.strftime('%Y-%m-%d %H:%M:%S') if self.complete_time else None
        }


class OperationSubmission(db.Model):
    """操作提交记录表"""
    __tablename__ = 'operation_submissions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    submission_type = db.Column(db.String(50), default='file')
    file_path = db.Column(db.String(500))
    submission_text = db.Column(db.Text)
    points_earned = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='submitted')
    submitted_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'operation_id': self.operation_id,
            'task_id': self.task_id,
            'submission_type': self.submission_type,
            'file_path': self.file_path,
            'points_earned': self.points_earned,
            'status': self.status,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if self.submitted_at else None
        }


class InstantAnswer(db.Model):
    """即时测试答题记录"""
    __tablename__ = 'instant_answers'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('instant_questions.id'), nullable=False)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'), nullable=False)
    student_answer = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    points_earned = db.Column(db.Integer, default=0)
    answered_at = db.Column(db.DateTime, default=datetime.now)


class UnifiedAnswer(db.Model):
    """统一测试答题记录"""
    __tablename__ = 'unified_answers'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('unified_questions.id'), nullable=False)
    student_answer = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    points_earned = db.Column(db.Integer, default=0)
    answered_at = db.Column(db.DateTime, default=datetime.now)


class StudentBadge(db.Model):
    """学生获得徽章记录"""
    __tablename__ = 'student_badges'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (db.UniqueConstraint('student_id', 'badge_id'),)


class StudentKnowledgeCard(db.Model):
    """知识卡片收集记录"""
    __tablename__ = 'student_knowledge_cards'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('knowledge_cards.id'), nullable=False)
    collected_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (db.UniqueConstraint('student_id', 'card_id'),)
