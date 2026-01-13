-- ============================================
-- 过关斩将 - 游戏教学平台 2.0 数据库设计
-- ============================================

-- 1. 学生表
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(50) UNIQUE NOT NULL,      -- 学号
    name VARCHAR(100) NOT NULL,                  -- 姓名
    password VARCHAR(255) NOT NULL,              -- 密码（哈希存储）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 2. 课程表
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code VARCHAR(50) UNIQUE NOT NULL,     -- 课程编号
    course_name VARCHAR(200) NOT NULL,           -- 课程名称
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 任务表（从md文档解析）
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    task_code VARCHAR(50) NOT NULL,              -- 任务编号 如：task-2
    task_name VARCHAR(200) NOT NULL,             -- 任务名称
    task_order INTEGER NOT NULL,                 -- 任务顺序
    content TEXT,                                 -- 任务完整内容（JSON格式）
    total_operations INTEGER DEFAULT 0,           -- 总操作数
    total_questions INTEGER DEFAULT 0,            -- 总问题数
    time_limit INTEGER,                           -- 建议时长（分钟）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- 4. 操作步骤表
CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    operation_code VARCHAR(50) NOT NULL,         -- 操作编号 如：op-1
    operation_name VARCHAR(200) NOT NULL,        -- 操作名称
    operation_order INTEGER NOT NULL,            -- 操作顺序
    description TEXT,                             -- 操作说明
    steps TEXT,                                   -- 操作步骤（JSON格式）
    practice_task TEXT,                           -- 练习任务
    points INTEGER DEFAULT 10,                    -- 该操作积分
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- 5. 知识卡片表（预定义）
CREATE TABLE IF NOT EXISTS knowledge_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    card_title VARCHAR(200) NOT NULL,            -- 卡片标题
    card_content TEXT NOT NULL,                  -- 卡片内容
    card_type VARCHAR(50) DEFAULT 'tip',         -- 卡片类型：tip/warning/info/success
    trigger_timing VARCHAR(50) DEFAULT 'after',  -- 触发时机：before/during/after
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES operations(id)
);

-- 6. 即时测试题表（课堂问答）
CREATE TABLE IF NOT EXISTS instant_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,               -- 关联到操作
    question_text TEXT NOT NULL,                 -- 问题内容
    option_a TEXT NOT NULL,                      -- 选项A
    option_b TEXT NOT NULL,                      -- 选项B
    option_c TEXT NOT NULL,                      -- 选项C
    option_d TEXT NOT NULL,                      -- 选项D
    correct_answer CHAR(1) NOT NULL,             -- 正确答案：A/B/C/D
    explanation TEXT,                            -- 解析
    points INTEGER DEFAULT 5,                    -- 该题积分
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES operations(id)
);

-- 7. 统一测试题表（后台配置）
CREATE TABLE IF NOT EXISTS unified_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    explanation TEXT,
    points INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- 8. 成就徽章表
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    badge_code VARCHAR(50) UNIQUE NOT NULL,      -- 徽章编码
    badge_name VARCHAR(100) NOT NULL,            -- 徽章名称
    badge_icon VARCHAR(200),                     -- 徽章图标路径
    badge_description TEXT,                      -- 徽章描述
    unlock_condition TEXT,                       -- 解锁条件（JSON格式）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. 学生学习进度表
CREATE TABLE IF NOT EXISTS student_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'not_started',    -- not_started/in_progress/completed
    total_points INTEGER DEFAULT 0,              -- 总积分
    current_operation INTEGER DEFAULT 0,         -- 当前操作编号
    operations_completed INTEGER DEFAULT 0,      -- 已完成操作数
    questions_correct INTEGER DEFAULT 0,         -- 答对题目数
    start_time TIMESTAMP,
    complete_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    UNIQUE(student_id, task_id)
);

-- 10. 操作提交记录表
CREATE TABLE IF NOT EXISTS operation_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    operation_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    submission_type VARCHAR(50) DEFAULT 'file',  -- file/text
    file_path VARCHAR(500),                      -- 文件路径
    submission_text TEXT,                        -- 文本内容
    points_earned INTEGER DEFAULT 0,             -- 获得积分
    status VARCHAR(50) DEFAULT 'submitted',      -- submitted/reviewed
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (operation_id) REFERENCES operations(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- 11. 即时测试答题记录
CREATE TABLE IF NOT EXISTS instant_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    operation_id INTEGER NOT NULL,
    student_answer CHAR(1) NOT NULL,             -- 学生答案
    is_correct BOOLEAN DEFAULT 0,                -- 是否正确
    points_earned INTEGER DEFAULT 0,             -- 获得积分
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (question_id) REFERENCES instant_questions(id),
    FOREIGN KEY (operation_id) REFERENCES operations(id)
);

-- 12. 统一测试答题记录
CREATE TABLE IF NOT EXISTS unified_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    student_answer CHAR(1) NOT NULL,
    is_correct BOOLEAN DEFAULT 0,
    points_earned INTEGER DEFAULT 0,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (question_id) REFERENCES unified_questions(id)
);

-- 13. 学生获得徽章记录
CREATE TABLE IF NOT EXISTS student_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (badge_id) REFERENCES badges(id),
    UNIQUE(student_id, badge_id)
);

-- 14. 知识卡片收集记录
CREATE TABLE IF NOT EXISTS student_knowledge_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    card_id INTEGER NOT NULL,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (card_id) REFERENCES knowledge_cards(id),
    UNIQUE(student_id, card_id)
);

-- ============================================
-- 索引优化
-- ============================================
CREATE INDEX idx_student_progress ON student_progress(student_id, task_id);
CREATE INDEX idx_operation_submissions ON operation_submissions(student_id, task_id);
CREATE INDEX idx_instant_answers ON instant_answers(student_id, operation_id);
CREATE INDEX idx_unified_answers ON unified_answers(student_id, task_id);
CREATE INDEX idx_student_badges ON student_badges(student_id);
