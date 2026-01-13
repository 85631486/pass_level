"""
过关斩将 - 游戏教学平台 2.0
Flask 后端主应用
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

# 初始化 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大上传

# 允许的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'xlsx'}

# 初始化扩展
CORS(app)
db = SQLAlchemy(app)

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================
# 数据库模型 - 直接在这里定义，避免循环导入
# ============================================

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
    content = db.Column(db.Text)
    total_operations = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    time_limit = db.Column(db.Integer)
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
    steps = db.Column(db.Text)
    practice_task = db.Column(db.Text)
    points = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
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
    unlock_condition = db.Column(db.Text)
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


# ============================================
# 路由 - 认证相关
# ============================================
@app.route('/api/auth/login', methods=['POST'])
def login():
    """学生登录"""
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password')

    student = Student.query.filter_by(student_id=student_id).first()

    if student and check_password_hash(student.password, password):
        student.last_login = datetime.now()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'id': student.id,
                'student_id': student.student_id,
                'name': student.name
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '学号或密码错误'
        }), 401


@app.route('/api/auth/register', methods=['POST'])
def register():
    """学生注册"""
    data = request.get_json()
    student_id = data.get('student_id')
    name = data.get('name')
    password = data.get('password')

    # 检查学号是否已存在
    if Student.query.filter_by(student_id=student_id).first():
        return jsonify({
            'success': False,
            'message': '该学号已被注册'
        }), 400

    # 创建新学生
    new_student = Student(
        student_id=student_id,
        name=name,
        password=generate_password_hash(password)
    )

    db.session.add(new_student)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '注册成功',
        'data': {
            'id': new_student.id,
            'student_id': new_student.student_id,
            'name': new_student.name
        }
    })


# ============================================
# 路由 - 任务相关
# ============================================
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取所有任务列表"""
    course_id = request.args.get('course_id', type=int)

    query = Task.query
    if course_id:
        query = query.filter_by(course_id=course_id)

    tasks = query.order_by(Task.task_order).all()

    return jsonify({
        'success': True,
        'data': [task.to_dict() for task in tasks]
    })


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task_detail(task_id):
    """获取任务详情"""
    task = Task.query.get_or_404(task_id)

    # 获取任务的所有操作
    operations = Operation.query.filter_by(task_id=task_id).order_by(Operation.operation_order).all()

    task_data = task.to_dict()
    task_data['operations'] = [op.to_dict() for op in operations]

    return jsonify({
        'success': True,
        'data': task_data
    })


# ============================================
# 路由 - 操作相关
# ============================================
@app.route('/api/operations/<int:operation_id>', methods=['GET'])
def get_operation_detail(operation_id):
    """获取操作详情"""
    operation = Operation.query.get_or_404(operation_id)

    # 获取知识卡片
    cards = KnowledgeCard.query.filter_by(operation_id=operation_id).all()

    # 获取即时测试题
    questions = InstantQuestion.query.filter_by(operation_id=operation_id).all()

    operation_data = operation.to_dict()
    operation_data['knowledge_cards'] = [card.to_dict() for card in cards]
    operation_data['instant_questions'] = [q.to_dict(include_answer=False) for q in questions]

    return jsonify({
        'success': True,
        'data': operation_data
    })


@app.route('/api/operations/<int:operation_id>/submit', methods=['POST'])
def submit_operation(operation_id):
    """提交操作结果"""
    student_id = request.form.get('student_id', type=int)
    task_id = request.form.get('task_id', type=int)

    # 处理文件上传
    file_path = None
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 创建学生专属目录
            student_dir = os.path.join(app.config['UPLOAD_FOLDER'], f'student_{student_id}')
            os.makedirs(student_dir, exist_ok=True)

            # 保存文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{timestamp}_{filename}'
            file_path = os.path.join(student_dir, filename)
            file.save(file_path)

    # 创建提交记录
    submission = OperationSubmission(
        student_id=student_id,
        operation_id=operation_id,
        task_id=task_id,
        submission_type='file',
        file_path=file_path,
        points_earned=10
    )

    db.session.add(submission)

    # 更新学生进度
    progress = StudentProgress.query.filter_by(
        student_id=student_id,
        task_id=task_id
    ).first()

    if progress:
        progress.operations_completed += 1
        progress.total_points += 10
        progress.updated_at = datetime.now()

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '提交成功',
        'data': {
            'points_earned': 10,
            'submission_id': submission.id
        }
    })


# ============================================
# 路由 - 测试题相关
# ============================================
@app.route('/api/questions/instant/<int:question_id>/answer', methods=['POST'])
def answer_instant_question(question_id):
    """回答即时测试题"""
    data = request.get_json()
    student_id = data.get('student_id')
    student_answer = data.get('answer')
    operation_id = data.get('operation_id')

    question = InstantQuestion.query.get_or_404(question_id)

    # 判断答案是否正确
    is_correct = (student_answer.upper() == question.correct_answer.upper())
    points_earned = question.points if is_correct else 0

    # 保存答题记录
    answer_record = InstantAnswer(
        student_id=student_id,
        question_id=question_id,
        operation_id=operation_id,
        student_answer=student_answer.upper(),
        is_correct=is_correct,
        points_earned=points_earned
    )

    db.session.add(answer_record)

    # 更新学生进度
    if is_correct:
        # 注意：这里需要通过task_id查找，而不是operation_id
        operation = Operation.query.get(operation_id)
        if operation:
            progress = StudentProgress.query.filter_by(
                student_id=student_id,
                task_id=operation.task_id
            ).first()

            if progress:
                progress.questions_correct += 1
                progress.total_points += points_earned
                progress.updated_at = datetime.now()

    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation,
            'points_earned': points_earned
        }
    })


@app.route('/api/tasks/<int:task_id>/unified-questions', methods=['GET'])
def get_unified_questions(task_id):
    """获取统一测试题"""
    questions = UnifiedQuestion.query.filter_by(task_id=task_id).all()

    return jsonify({
        'success': True,
        'data': [q.to_dict(include_answer=False) for q in questions]
    })


@app.route('/api/tasks/<int:task_id>/unified-test/submit', methods=['POST'])
def submit_unified_test(task_id):
    """提交统一测试答案"""
    data = request.get_json()
    student_id = data.get('student_id')
    answers = data.get('answers')  # {question_id: answer}

    total_points = 0
    correct_count = 0
    results = []

    for question_id, student_answer in answers.items():
        question = UnifiedQuestion.query.get(int(question_id))
        if not question:
            continue

        is_correct = (student_answer.upper() == question.correct_answer.upper())
        points_earned = question.points if is_correct else 0

        # 保存答题记录
        answer_record = UnifiedAnswer(
            student_id=student_id,
            task_id=task_id,
            question_id=question_id,
            student_answer=student_answer.upper(),
            is_correct=is_correct,
            points_earned=points_earned
        )

        db.session.add(answer_record)

        if is_correct:
            correct_count += 1
            total_points += points_earned

        results.append({
            'question_id': question_id,
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation
        })

    # 更新学生进度
    progress = StudentProgress.query.filter_by(
        student_id=student_id,
        task_id=task_id
    ).first()

    if progress:
        progress.total_points += total_points
        progress.updated_at = datetime.now()

    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'total_points': total_points,
            'correct_count': correct_count,
            'total_questions': len(answers),
            'results': results
        }
    })


# ============================================
# 路由 - 学习进度相关
# ============================================
@app.route('/api/progress/start', methods=['POST'])
def start_task():
    """开始学习任务"""
    data = request.get_json()
    student_id = data.get('student_id')
    task_id = data.get('task_id')

    # 检查是否已有进度记录
    progress = StudentProgress.query.filter_by(
        student_id=student_id,
        task_id=task_id
    ).first()

    if not progress:
        progress = StudentProgress(
            student_id=student_id,
            task_id=task_id,
            status='in_progress',
            start_time=datetime.now()
        )
        db.session.add(progress)
    else:
        progress.status = 'in_progress'
        if not progress.start_time:
            progress.start_time = datetime.now()

    db.session.commit()

    return jsonify({
        'success': True,
        'data': progress.to_dict()
    })


@app.route('/api/progress/<int:student_id>/<int:task_id>', methods=['GET'])
def get_progress(student_id, task_id):
    """获取学习进度"""
    progress = StudentProgress.query.filter_by(
        student_id=student_id,
        task_id=task_id
    ).first()

    if not progress:
        return jsonify({
            'success': True,
            'data': {
                'status': 'not_started',
                'total_points': 0,
                'current_operation': 0,
                'operations_completed': 0,
                'questions_correct': 0
            }
        })

    return jsonify({
        'success': True,
        'data': progress.to_dict()
    })


@app.route('/api/progress/complete', methods=['POST'])
def complete_task():
    """完成任务"""
    data = request.get_json()
    student_id = data.get('student_id')
    task_id = data.get('task_id')

    progress = StudentProgress.query.filter_by(
        student_id=student_id,
        task_id=task_id
    ).first()

    if progress:
        progress.status = 'completed'
        progress.complete_time = datetime.now()
        progress.updated_at = datetime.now()

        # 检查并颁发徽章
        check_and_award_badges(student_id, task_id)

        db.session.commit()

        return jsonify({
            'success': True,
            'data': progress.to_dict()
        })

    return jsonify({
        'success': False,
        'message': '未找到学习进度'
    }), 404


# ============================================
# 路由 - 知识卡片相关
# ============================================
@app.route('/api/knowledge-cards/collect', methods=['POST'])
def collect_knowledge_card():
    """收集知识卡片"""
    data = request.get_json()
    student_id = data.get('student_id')
    card_id = data.get('card_id')

    # 检查是否已收集
    existing = StudentKnowledgeCard.query.filter_by(
        student_id=student_id,
        card_id=card_id
    ).first()

    if existing:
        return jsonify({
            'success': True,
            'message': '该卡片已收集'
        })

    collection = StudentKnowledgeCard(
        student_id=student_id,
        card_id=card_id
    )

    db.session.add(collection)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '收集成功'
    })


@app.route('/api/knowledge-cards/<int:student_id>', methods=['GET'])
def get_collected_cards(student_id):
    """获取学生收集的知识卡片"""
    collections = StudentKnowledgeCard.query.filter_by(student_id=student_id).all()
    card_ids = [c.card_id for c in collections]

    cards = KnowledgeCard.query.filter(KnowledgeCard.id.in_(card_ids)).all() if card_ids else []

    return jsonify({
        'success': True,
        'data': [card.to_dict() for card in cards]
    })


# ============================================
# 路由 - 徽章相关
# ============================================
@app.route('/api/badges/<int:student_id>', methods=['GET'])
def get_student_badges(student_id):
    """获取学生的徽章"""
    student_badges = StudentBadge.query.filter_by(student_id=student_id).all()
    badge_ids = [sb.badge_id for sb in student_badges]

    badges = Badge.query.filter(Badge.id.in_(badge_ids)).all() if badge_ids else []

    return jsonify({
        'success': True,
        'data': [badge.to_dict() for badge in badges]
    })


def check_and_award_badges(student_id, task_id):
    """检查并颁发徽章"""
    progress = StudentProgress.query.filter_by(
        student_id=student_id,
        task_id=task_id
    ).first()

    if not progress:
        return

    # 徽章逻辑示例
    badges_to_award = []

    # 1. 完成任务徽章
    if progress.status == 'completed':
        badges_to_award.append('task_completed')

    # 2. 全部操作完成徽章
    task = Task.query.get(task_id)
    if task and progress.operations_completed >= task.total_operations:
        badges_to_award.append('all_operations_completed')

    # 3. 满分徽章
    if task:
        max_points = task.total_operations * 10 + task.total_questions * 5
        if progress.total_points >= max_points:
            badges_to_award.append('perfect_score')

    # 颁发徽章
    for badge_code in badges_to_award:
        badge = Badge.query.filter_by(badge_code=badge_code).first()
        if badge:
            existing = StudentBadge.query.filter_by(
                student_id=student_id,
                badge_id=badge.id
            ).first()

            if not existing:
                student_badge = StudentBadge(
                    student_id=student_id,
                    badge_id=badge.id
                )
                db.session.add(student_badge)


# ============================================
# 路由 - 学习总结
# ============================================
@app.route('/api/summary/<int:student_id>/<int:task_id>', methods=['GET'])
def get_learning_summary(student_id, task_id):
    """生成学习总结"""
    progress = StudentProgress.query.filter_by(
        student_id=student_id,
        task_id=task_id
    ).first()

    if not progress:
        return jsonify({
            'success': False,
            'message': '未找到学习记录'
        }), 404

    # 统计数据
    task = Task.query.get(task_id)
    student = Student.query.get(student_id)

    # 操作提交记录
    submissions = OperationSubmission.query.filter_by(
        student_id=student_id,
        task_id=task_id
    ).all()

    # 即时测试答题情况
    instant_answers = db.session.query(InstantAnswer).join(
        InstantQuestion
    ).filter(
        InstantAnswer.student_id == student_id,
        InstantQuestion.operation_id.in_(
            [op.id for op in Operation.query.filter_by(task_id=task_id).all()]
        )
    ).all()

    instant_correct = sum(1 for a in instant_answers if a.is_correct)

    # 统一测试答题情况
    unified_answers = UnifiedAnswer.query.filter_by(
        student_id=student_id,
        task_id=task_id
    ).all()

    unified_correct = sum(1 for a in unified_answers if a.is_correct)

    # 知识卡片收集
    collected_cards = StudentKnowledgeCard.query.filter_by(
        student_id=student_id
    ).count()

    # 获得的徽章
    badges = db.session.query(Badge).join(
        StudentBadge
    ).filter(
        StudentBadge.student_id == student_id
    ).all()

    # 计算学习时长
    time_spent = 0
    if progress.start_time and progress.complete_time:
        time_spent = (progress.complete_time - progress.start_time).total_seconds() / 60

    summary = {
        'student_name': student.name,
        'task_name': task.task_name,
        'total_points': progress.total_points,
        'operations_completed': progress.operations_completed,
        'total_operations': task.total_operations,
        'instant_questions_correct': instant_correct,
        'instant_questions_total': len(instant_answers),
        'unified_questions_correct': unified_correct,
        'unified_questions_total': len(unified_answers),
        'knowledge_cards_collected': collected_cards,
        'badges_earned': len(badges),
        'badges': [badge.to_dict() for badge in badges],
        'time_spent_minutes': round(time_spent, 2),
        'completion_rate': round(progress.operations_completed / task.total_operations * 100, 2) if task.total_operations > 0 else 0,
        'status': progress.status
    }

    return jsonify({
        'success': True,
        'data': summary
    })


# ============================================
# 初始化数据库
# ============================================
@app.route('/api/init-db', methods=['POST'])
def init_database():
    """初始化数据库（仅用于开发）"""
    db.create_all()

    # 创建示例徽章
    badges_data = [
        {'badge_code': 'task_completed', 'badge_name': '任务完成', 'badge_description': '完成一个任务'},
        {'badge_code': 'all_operations_completed', 'badge_name': '操作大师', 'badge_description': '完成所有操作'},
        {'badge_code': 'perfect_score', 'badge_name': '满分学霸', 'badge_description': '获得满分'},
        {'badge_code': 'speed_learner', 'badge_name': '速度之星', 'badge_description': '在规定时间内完成任务'},
        {'badge_code': 'knowledge_collector', 'badge_name': '知识收藏家', 'badge_description': '收集所有知识卡片'},
    ]

    for badge_data in badges_data:
        if not Badge.query.filter_by(badge_code=badge_data['badge_code']).first():
            badge = Badge(**badge_data)
            db.session.add(badge)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '数据库初始化成功'
    })


# ============================================
# 启动应用
# ============================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('数据库初始化完成！')
    app.run(debug=True, host='0.0.0.0', port=5000)
