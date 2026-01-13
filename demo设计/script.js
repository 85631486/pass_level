// ==================== 全局状态管理 ====================
const state = {
    currentStep: 0,
    totalSteps: 13, // 总共13个学习步骤
    points: 0,
    timeSpent: 0,
    completedOperations: 0,
    totalOperations: 10,
    answeredQuestions: 0,
    totalQuestions: 18,
    correctAnswers: 0,
    knowledgeCards: [],
    badges: [],
    submissions: {}
};

// ==================== 模拟数据 ====================
const courseData = {
    steps: [
        {
            id: 'step1-1',
            type: 'content',
            title: '认识Excel界面',
            subtitle: '步骤一：认识Excel界面（15分钟）',
            content: `
                <div class="step-content">
                    <h3>1.1 Excel界面导览</h3>
                    <p>打开Excel，认识以下界面元素：</p>
                    <div class="operation-method">
                        <pre>
┌─────────────────────────────────────┐
│ 文件 开始 插入 页面布局 公式 数据... │ ← 功能区/选项卡
├─────────────────────────────────────┤
│ 复制 粘贴 字体 对齐 数字...         │ ← 命令按钮
├──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬───┤
│  │ A│ B│ C│ D│ E│ F│...           │ ← 列标
├──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼───┤
│1 │  │  │  │  │  │  │              │
│2 │  │  │  │  │  │  │              │ ← 单元格区域
│3 │  │  │  │  │  │  │              │
│..│  │  │  │  │  │  │              │
└──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴───┘
    ↑
   行号
                        </pre>
                    </div>
                    <div style="margin-top: 20px;">
                        <h4>关键概念：</h4>
                        <ul style="margin-left: 20px; line-height: 2;">
                            <li><strong>单元格</strong>：一个格子（如A1）</li>
                            <li><strong>行</strong>：横向的，用数字编号（1, 2, 3...）</li>
                            <li><strong>列</strong>：纵向的，用字母编号（A, B, C...）</li>
                            <li><strong>工作表</strong>：底部标签（Sheet1, Sheet2...）</li>
                            <li><strong>功能区</strong>：顶部的命令按钮集合</li>
                        </ul>
                    </div>
                </div>
            `,
            knowledgeCard: {
                icon: '💡',
                title: 'Excel基础概念',
                content: '单元格是Excel的基本单位，由列标（字母）和行号（数字）组成唯一地址，如A1、B5等。掌握单元格引用是Excel学习的基础！'
            }
        },
        {
            id: 'step1-2',
            type: 'quiz',
            title: '课堂问答：认识Excel界面',
            questions: [
                {
                    id: 'q1',
                    text: '在Excel中，列标是用什么表示的？',
                    options: [
                        { value: 'A', text: 'A. 数字（1, 2, 3...）' },
                        { value: 'B', text: 'B. 字母（A, B, C...）' },
                        { value: 'C', text: 'C. 中文（一, 二, 三...）' },
                        { value: 'D', text: 'D. 符号（#, $, %...）' }
                    ],
                    correctAnswer: 'B',
                    explanation: 'Excel中列用字母编号（A、B、C...），行用数字编号（1、2、3...）。单元格地址由列标和行号组成，如A1表示第A列第1行。',
                    points: 5
                },
                {
                    id: 'q2',
                    text: 'Excel顶部的"开始"、"插入"、"数据"等选项卡区域叫什么？',
                    options: [
                        { value: 'A', text: 'A. 工具栏' },
                        { value: 'B', text: 'B. 功能区/选项卡' },
                        { value: 'C', text: 'C. 菜单栏' },
                        { value: 'D', text: 'D. 状态栏' }
                    ],
                    correctAnswer: 'B',
                    explanation: 'Excel顶部包含多个选项卡（如"开始"、"插入"、"数据"等），每个选项卡下包含相关的命令按钮，这个区域称为"功能区"或"选项卡"。',
                    points: 5
                },
                {
                    id: 'q3',
                    text: 'Excel底部显示"Sheet1"、"Sheet2"的标签代表什么？',
                    options: [
                        { value: 'A', text: 'A. 单元格' },
                        { value: 'B', text: 'B. 工作表' },
                        { value: 'C', text: 'C. 工作簿' },
                        { value: 'D', text: 'D. 列' }
                    ],
                    correctAnswer: 'B',
                    explanation: 'Excel底部的工作表标签（Sheet1、Sheet2等）代表不同的工作表。一个Excel文件（工作簿）可以包含多个工作表，每个工作表是独立的表格。',
                    points: 5
                }
            ]
        },
        {
            id: 'op1',
            type: 'operation',
            title: '操作1：选中单元格与区域',
            subtitle: '掌握10个核心操作（第1个）',
            content: `
                <div class="step-content">
                    <div class="operation-method">
                        <h4>1. 单击选中一个单元格</h4>
                        <pre>步骤：
1. 将鼠标指针移动到想要选中的单元格上（例如A1单元格）
2. 鼠标指针会变成白色十字形状
3. 用鼠标左键单击一下该单元格
4. 单元格周围会出现黑色边框，表示已选中
5. 单元格名称会显示在左上角的名称框中（如A1）</pre>
                    </div>

                    <div class="operation-method">
                        <h4>2. 拖动选中连续区域</h4>
                        <pre>步骤：
1. 将鼠标指针移动到要选中区域的第一个单元格上（例如A1）
2. 按住鼠标左键不松开
3. 拖动鼠标到区域的最后一个单元格（例如D10）
4. 松开鼠标左键
5. 整个区域会被选中，显示为蓝色背景
6. 区域范围会显示在名称框中（如A1:D10）</pre>
                    </div>

                    <div class="operation-method">
                        <h4>3. 使用Ctrl键选中不连续单元格</h4>
                        <pre>步骤：
1. 用鼠标左键单击第一个要选中的单元格
2. 按住键盘左下角的Ctrl键（不要松开）
3. 用鼠标左键单击第二个要选中的单元格
4. 继续按住Ctrl键，单击第三个、第四个...单元格
5. 选完所有需要的单元格后，松开Ctrl键
6. 所有选中的单元格都会显示为蓝色背景</pre>
                    </div>

                    <div class="practice-task">
                        <h4>📝 立即动手练习</h4>
                        <ol style="margin-left: 20px; line-height: 2;">
                            <li>打开任务1的数据文件</li>
                            <li>选中"商品名称"整列（点击列标B或C）</li>
                            <li>选中前10行数据（从行号1拖到行号10）</li>
                            <li>选中"金额"列的前20个单元格</li>
                        </ol>
                    </div>
                </div>
            `,
            practice: {
                title: '请完成以下练习并提交结果：',
                tasks: [
                    '✓ 选中"商品名称"整列',
                    '✓ 选中前10行数据',
                    '✓ 选中"金额"列的前20个单元格'
                ]
            },
            knowledgeCard: {
                icon: '⌨️',
                title: 'Ctrl键选择技巧',
                content: '按住Ctrl键可以选择多个不连续的单元格或区域。这在需要对分散的数据进行统一操作时非常有用，比如批量设置格式、复制粘贴等。'
            },
            questions: [
                {
                    id: 'q4',
                    text: '在Excel中，要选中整列，应该点击哪里？',
                    options: [
                        { value: 'A', text: 'A. 单元格' },
                        { value: 'B', text: 'B. 列标（如A、B、C）' },
                        { value: 'C', text: 'C. 行号（如1、2、3）' },
                        { value: 'D', text: 'D. 工作表标签' }
                    ],
                    correctAnswer: 'B',
                    explanation: '点击列标（字母A、B、C等）可以选中整列。点击行号（数字1、2、3等）可以选中整行。',
                    points: 5
                }
            ]
        },
        {
            id: 'op2',
            type: 'operation',
            title: '操作2：复制、粘贴、剪切',
            subtitle: '掌握10个核心操作（第2个）',
            content: `
                <div class="step-content">
                    <div class="operation-method">
                        <h4>复制快捷键：Ctrl+C</h4>
                        <pre>步骤：
1. 先选中要复制的内容（可以是单元格、区域、整列或整行）
2. 同时按下键盘上的Ctrl键和C键
3. 内容会被复制到剪贴板
4. 原位置的数据保持不变</pre>
                    </div>

                    <div class="operation-method">
                        <h4>粘贴快捷键：Ctrl+V</h4>
                        <pre>步骤：
1. 先完成复制操作（使用Ctrl+C）
2. 用鼠标左键单击要粘贴到的目标单元格
3. 同时按下键盘上的Ctrl键和V键
4. 复制的内容会粘贴到目标位置</pre>
                    </div>

                    <div class="practice-task">
                        <h4>📝 立即动手练习</h4>
                        <ol style="margin-left: 20px; line-height: 2;">
                            <li>复制"商品名称"列，粘贴到另一列</li>
                            <li>复制前5行数据到Sheet2</li>
                        </ol>
                    </div>
                </div>
            `,
            practice: {
                title: '请完成复制粘贴练习并提交截图：',
                tasks: [
                    '✓ 复制"商品名称"列到另一列',
                    '✓ 复制前5行数据到Sheet2'
                ]
            },
            knowledgeCard: {
                icon: '📋',
                title: '通用快捷键',
                content: 'Ctrl+C（复制）、Ctrl+V（粘贴）、Ctrl+X（剪切）这三个快捷键在几乎所有Windows软件中都通用！掌握它们可以大大提高工作效率。'
            },
            questions: [
                {
                    id: 'q5',
                    text: '在Excel中，复制的快捷键是什么？',
                    options: [
                        { value: 'A', text: 'A. Ctrl+X' },
                        { value: 'B', text: 'B. Ctrl+C' },
                        { value: 'C', text: 'C. Ctrl+V' },
                        { value: 'D', text: 'D. Ctrl+Z' }
                    ],
                    correctAnswer: 'B',
                    explanation: 'Ctrl+C是复制快捷键，Ctrl+X是剪切，Ctrl+V是粘贴，Ctrl+Z是撤销。',
                    points: 5
                }
            ]
        },
        {
            id: 'op3',
            type: 'operation',
            title: '操作3：撤销与恢复',
            subtitle: '掌握10个核心操作（第3个）',
            content: `
                <div class="step-content">
                    <div class="operation-method">
                        <h4>撤销操作：Ctrl+Z</h4>
                        <pre>步骤：
1. 完成任意一个操作（例如输入文字、删除数据、复制粘贴等）
2. 同时按下键盘上的Ctrl键和Z键
3. 刚才的操作会被撤销，数据恢复到操作前的状态
4. 可以连续按Ctrl+Z多次，每次撤销一步操作</pre>
                    </div>

                    <div class="operation-method">
                        <h4>恢复操作：Ctrl+Y</h4>
                        <pre>步骤：
1. 如果撤销了某个操作，想要恢复它
2. 同时按下键盘上的Ctrl键和Y键
3. 被撤销的操作会被恢复
4. 可以连续按Ctrl+Y多次，每次恢复一步操作</pre>
                    </div>

                    <div class="practice-task">
                        <h4>📝 立即动手练习</h4>
                        <ol style="margin-left: 20px; line-height: 2;">
                            <li>随意修改几个单元格</li>
                            <li>使用Ctrl+Z撤销</li>
                            <li>使用Ctrl+Y恢复</li>
                        </ol>
                    </div>
                </div>
            `,
            practice: {
                title: '请完成撤销恢复练习：',
                tasks: [
                    '✓ 修改单元格并撤销',
                    '✓ 使用恢复功能'
                ]
            },
            knowledgeCard: {
                icon: '↩️',
                title: '后悔药快捷键',
                content: 'Ctrl+Z是"后悔药"，可以撤销几乎所有操作。记住这个快捷键，就不怕操作失误了！但要注意，保存文件后就无法撤销保存前的操作。'
            },
            questions: []
        }
        // 这里可以继续添加更多操作步骤...
    ],

    badges: [
        {
            id: 'badge1',
            icon: '🥇',
            name: '界面探索者',
            description: '完成Excel界面认识',
            unlockCondition: { step: 1 },
            unlocked: false
        },
        {
            id: 'badge2',
            icon: '🥈',
            name: '操作新手',
            description: '完成前5个操作',
            unlockCondition: { operations: 5 },
            unlocked: false
        },
        {
            id: 'badge3',
            icon: '🥉',
            name: '快捷键大师',
            description: '完成所有操作练习',
            unlockCondition: { operations: 10 },
            unlocked: false,
            progress: 0
        }
    ]
};

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', function() {
    initApp();
    startTimer();
});

function initApp() {
    loadStep(state.currentStep);
    updateUI();
    initDrawers();
    initOutlineTree();
    updateProgressDrawer();
    initBadges();
}

// ==================== 计时器 ====================
function startTimer() {
    setInterval(() => {
        state.timeSpent++;
        updateTimer();
    }, 1000);
}

function updateTimer() {
    const minutes = Math.floor(state.timeSpent / 60);
    const seconds = state.timeSpent % 60;
    const timeString = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    document.getElementById('timeSpent').textContent = timeString;
    document.getElementById('drawerTime').textContent = `${minutes}分钟`;
}

// ==================== 加载步骤内容 ====================
function loadStep(stepIndex) {
    const step = courseData.steps[stepIndex];
    if (!step) return;

    const contentArea = document.getElementById('contentArea');
    let html = '';

    if (step.type === 'content') {
        html = `
            <div class="step-header">
                <h2 class="step-title">${step.title}</h2>
                <p class="step-subtitle">${step.subtitle}</p>
            </div>
            ${step.content}
        `;
    } else if (step.type === 'operation') {
        html = `
            <div class="step-header">
                <h2 class="step-title">${step.title}</h2>
                <p class="step-subtitle">${step.subtitle}</p>
            </div>
            ${step.content}
            ${step.practice ? renderPracticeForm(step.practice) : ''}
            ${step.questions && step.questions.length > 0 ? renderQuestions(step.questions) : ''}
        `;
    } else if (step.type === 'quiz') {
        html = `
            <div class="step-header">
                <h2 class="step-title">${step.title}</h2>
            </div>
            ${renderQuestions(step.questions)}
        `;
    }

    contentArea.innerHTML = html;
    updateButtonStates();
}

function renderPracticeForm(practice) {
    return `
        <div class="practice-task">
            <h4>${practice.title}</h4>
            <ul style="margin: 16px 0 16px 20px; line-height: 2;">
                ${practice.tasks.map(task => `<li>${task}</li>`).join('')}
            </ul>
            <div class="practice-form">
                <div class="form-group">
                    <label>上传操作截图：</label>
                    <input type="file" accept="image/*" id="practiceFile">
                </div>
                <div class="form-group">
                    <label>或者描述你的操作过程：</label>
                    <textarea id="practiceText" placeholder="请描述你完成练习的步骤..."></textarea>
                </div>
            </div>
        </div>
    `;
}

function renderQuestions(questions) {
    return questions.map((q, index) => `
        <div class="question-card" data-question-id="${q.id}">
            <h4>📝 问题 ${index + 1}</h4>
            <p class="question-text">${q.text}</p>
            <div class="options">
                ${q.options.map(opt => `
                    <div class="option">
                        <input type="radio" name="${q.id}" value="${opt.value}" id="${q.id}_${opt.value}">
                        <label for="${q.id}_${opt.value}">${opt.text}</label>
                    </div>
                `).join('')}
            </div>
            <div class="question-feedback" style="display: none;"></div>
        </div>
    `).join('');
}

// ==================== 按钮控制 ====================
function updateButtonStates() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const completeBtn = document.getElementById('completeBtn');

    prevBtn.disabled = state.currentStep === 0;

    const currentStepData = courseData.steps[state.currentStep];

    // 如果当前步骤有练习或测试，显示提交按钮
    if (currentStepData && (currentStepData.practice || currentStepData.questions)) {
        submitBtn.style.display = 'block';
        nextBtn.style.display = 'none';
    } else {
        submitBtn.style.display = 'none';
        nextBtn.style.display = 'block';
    }

    // 最后一步显示完成按钮
    if (state.currentStep === state.totalSteps - 1) {
        nextBtn.style.display = 'none';
        completeBtn.style.display = 'block';
    } else {
        completeBtn.style.display = 'none';
    }
}

document.getElementById('prevBtn').addEventListener('click', () => {
    if (state.currentStep > 0) {
        state.currentStep--;
        loadStep(state.currentStep);
        updateUI();
    }
});

document.getElementById('nextBtn').addEventListener('click', () => {
    if (state.currentStep < courseData.steps.length - 1) {
        state.currentStep++;
        loadStep(state.currentStep);
        updateUI();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

document.getElementById('submitBtn').addEventListener('click', handleSubmit);

document.getElementById('completeBtn').addEventListener('click', () => {
    showCompleteModal();
});

// ==================== 提交处理 ====================
function handleSubmit() {
    const currentStepData = courseData.steps[state.currentStep];

    // 处理练习提交
    if (currentStepData.practice) {
        const file = document.getElementById('practiceFile')?.files[0];
        const text = document.getElementById('practiceText')?.value;

        if (file || text) {
            // 保存提交记录
            state.submissions[currentStepData.id] = { file, text };

            // 增加积分
            addPoints(10);

            // 完成操作数+1
            if (currentStepData.type === 'operation') {
                state.completedOperations++;
            }

            // 显示知识卡片
            if (currentStepData.knowledgeCard) {
                showKnowledgeCard(currentStepData.knowledgeCard);
                state.knowledgeCards.push(currentStepData.knowledgeCard);
            }

            // 检查徽章
            checkBadges();
        } else {
            alert('请上传截图或填写操作说明！');
            return;
        }
    }

    // 处理测试题
    if (currentStepData.questions && currentStepData.questions.length > 0) {
        let allAnswered = true;

        currentStepData.questions.forEach(q => {
            const selected = document.querySelector(`input[name="${q.id}"]:checked`);
            if (!selected) {
                allAnswered = false;
                return;
            }

            const isCorrect = selected.value === q.correctAnswer;
            const questionCard = document.querySelector(`[data-question-id="${q.id}"]`);
            const feedback = questionCard.querySelector('.question-feedback');

            // 显示反馈
            feedback.style.display = 'block';
            if (isCorrect) {
                feedback.className = 'question-feedback correct';
                feedback.innerHTML = `
                    <div><strong>✅ 回答正确！+${q.points}分</strong></div>
                    <div class="explanation">💡 ${q.explanation}</div>
                `;
                addPoints(q.points);
                state.correctAnswers++;

                // 标记选项为正确
                selected.closest('.option').classList.add('correct');
            } else {
                feedback.className = 'question-feedback incorrect';
                feedback.innerHTML = `
                    <div><strong>❌ 回答错误</strong></div>
                    <div class="explanation">💡 ${q.explanation}</div>
                `;

                // 标记选项为错误
                selected.closest('.option').classList.add('incorrect');
                // 显示正确答案
                document.querySelector(`input[name="${q.id}"][value="${q.correctAnswer}"]`).closest('.option').classList.add('correct');
            }

            state.answeredQuestions++;

            // 禁用所有选项
            questionCard.querySelectorAll('input[type="radio"]').forEach(input => {
                input.disabled = true;
            });
        });

        if (!allAnswered) {
            alert('请回答所有问题！');
            return;
        }
    }

    // 更新UI
    updateUI();

    // 自动进入下一步
    setTimeout(() => {
        if (state.currentStep < courseData.steps.length - 1) {
            state.currentStep++;
            loadStep(state.currentStep);
            updateUI();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }, 2000);
}

// ==================== 积分动画 ====================
function addPoints(points) {
    state.points += points;

    // 显示积分动画
    const pointsAnim = document.createElement('div');
    pointsAnim.className = 'points-animation';
    pointsAnim.textContent = `+${points}分`;
    document.body.appendChild(pointsAnim);

    setTimeout(() => {
        pointsAnim.remove();
    }, 1000);
}

// ==================== 知识卡片弹窗 ====================
function showKnowledgeCard(card) {
    const modal = document.getElementById('cardModal');
    document.getElementById('cardTitle').textContent = card.title;
    document.getElementById('cardContent').innerHTML = `<p>${card.content}</p>`;
    document.querySelector('.card-modal-header .card-icon').textContent = card.icon;
    modal.classList.add('show');
}

function closeCardModal() {
    document.getElementById('cardModal').classList.remove('show');
}

// ==================== 完成弹窗 ====================
function showCompleteModal() {
    const modal = document.getElementById('completeModal');

    const minutes = Math.floor(state.timeSpent / 60);
    const accuracy = Math.round((state.correctAnswers / state.totalQuestions) * 100);

    document.getElementById('finalTime').textContent = `${minutes}分钟`;
    document.getElementById('finalPoints').textContent = `${state.points}分`;
    document.getElementById('finalOps').textContent = `${state.completedOperations}/${state.totalOperations}`;
    document.getElementById('finalAccuracy').textContent = `${state.correctAnswers}/${state.totalQuestions} (${accuracy}%)`;
    document.getElementById('finalCards').textContent = `${state.knowledgeCards.length}张`;
    document.getElementById('finalBadges').textContent = `${state.badges.filter(b => b.unlocked).length}个`;

    modal.classList.add('show');
}

// ==================== 抽屉控制 ====================
function initDrawers() {
    // 抽屉按钮点击
    document.querySelectorAll('.drawer-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const drawerType = this.getAttribute('data-drawer');
            openDrawer(drawerType);
        });
    });

    // 关闭按钮
    document.querySelectorAll('.close-drawer').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.drawer').classList.remove('open');
        });
    });

    // 点击弹窗背景关闭
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('show');
            }
        });
    });
}

function openDrawer(type) {
    // 关闭所有抽屉
    document.querySelectorAll('.drawer').forEach(d => d.classList.remove('open'));

    // 打开指定抽屉
    const drawerMap = {
        'outline': 'drawerOutline',
        'progress': 'drawerProgress',
        'cards': 'drawerCards',
        'badges': 'drawerBadges'
    };

    const drawer = document.getElementById(drawerMap[type]);
    if (drawer) {
        drawer.classList.add('open');

        // 更新抽屉内容
        if (type === 'progress') updateProgressDrawer();
        if (type === 'cards') updateCardsDrawer();
        if (type === 'badges') updateBadgesDrawer();
    }
}

// ==================== 任务大纲 ====================
function initOutlineTree() {
    const tree = document.getElementById('outlineTree');

    const outline = {
        '步骤一：认识Excel界面': [0, 1],
        '步骤二：掌握10个核心操作': [2, 3, 4],
        '步骤三：综合练习': [],
        '步骤四：AI答疑': []
    };

    let html = '';
    let globalIndex = 0;

    for (const [stepName, indices] of Object.entries(outline)) {
        const isCompleted = indices.length > 0 && indices.every(i => i < state.currentStep);
        const isCurrent = indices.includes(state.currentStep);
        const isLocked = indices.length > 0 && indices[0] > state.currentStep;

        let stepClass = 'outline-step';
        if (isCompleted) stepClass += ' completed';
        if (isCurrent) stepClass += ' current';
        if (isLocked) stepClass += ' locked';

        const icon = isCompleted ? '✓' : isCurrent ? '🔄' : '🔒';

        html += `<div class="${stepClass}">${icon} ${stepName}</div>`;

        if (indices.length > 0) {
            html += '<div class="outline-operations">';
            indices.forEach(i => {
                const step = courseData.steps[i];
                const opCompleted = i < state.currentStep;
                const opIcon = opCompleted ? '✓' : i === state.currentStep ? '🔄' : '🔒';
                html += `<div class="outline-operation">${opIcon} ${step.title}</div>`;
            });
            html += '</div>';
        }
    }

    tree.innerHTML = html;
}

// ==================== 进度抽屉更新 ====================
function updateProgressDrawer() {
    const progress = Math.round((state.currentStep / state.totalSteps) * 100);
    document.getElementById('circleText').textContent = `${progress}%`;

    const circle = document.getElementById('circleProgress');
    const offset = 314 - (314 * progress) / 100;
    circle.style.strokeDashoffset = offset;

    document.getElementById('currentStep').textContent = courseData.steps[state.currentStep]?.title || '-';
    document.getElementById('completedOps').textContent = `${state.completedOperations}/${state.totalOperations}`;
    document.getElementById('answeredQuestions').textContent = `${state.answeredQuestions}/${state.totalQuestions}`;
    document.getElementById('drawerPoints').textContent = `${state.points}分`;

    // 操作列表
    const opList = document.getElementById('operationList');
    let html = '<h4 style="margin-top: 24px; margin-bottom: 12px;">操作完成度:</h4>';

    for (let i = 0; i < state.totalOperations; i++) {
        const completed = i < state.completedOperations;
        html += `
            <div class="operation-item">
                <span class="name">${completed ? '✓' : '⭕'} 操作${i + 1}</span>
                <span class="points">${completed ? '+10分' : '-'}</span>
            </div>
        `;
    }

    opList.innerHTML = html;
}

// ==================== 知识卡包更新 ====================
function updateCardsDrawer() {
    document.getElementById('cardsCount').textContent = state.knowledgeCards.length;

    const grid = document.getElementById('cardsGrid');
    grid.innerHTML = state.knowledgeCards.map(card => `
        <div class="knowledge-card" onclick="showKnowledgeCard(${JSON.stringify(card).replace(/"/g, '&quot;')})">
            <div class="card-icon">${card.icon}</div>
            <div class="card-title">${card.title}</div>
            <div class="card-stars">⭐⭐⭐</div>
        </div>
    `).join('');
}

// ==================== 徽章系统 ====================
function initBadges() {
    state.badges = courseData.badges.map(b => ({...b}));
    updateBadgesDrawer();
}

function checkBadges() {
    courseData.badges.forEach((badge, index) => {
        if (state.badges[index].unlocked) return;

        let shouldUnlock = false;

        if (badge.unlockCondition.step && state.currentStep >= badge.unlockCondition.step) {
            shouldUnlock = true;
        }

        if (badge.unlockCondition.operations && state.completedOperations >= badge.unlockCondition.operations) {
            shouldUnlock = true;
        }

        if (shouldUnlock) {
            state.badges[index].unlocked = true;
            showBadgeUnlocked(badge);
        } else if (badge.unlockCondition.operations) {
            state.badges[index].progress = Math.round((state.completedOperations / badge.unlockCondition.operations) * 100);
        }
    });

    updateBadgesDrawer();
}

function showBadgeUnlocked(badge) {
    alert(`🎉 恭喜解锁徽章：${badge.icon} ${badge.name}\n${badge.description}`);
}

function updateBadgesDrawer() {
    const badgesCount = state.badges.filter(b => b.unlocked).length;
    document.getElementById('badgesCount').textContent = badgesCount;

    const grid = document.getElementById('badgesGrid');
    grid.innerHTML = state.badges.map(badge => `
        <div class="badge-item ${badge.unlocked ? '' : 'locked'}">
            <div class="badge-icon">${badge.icon}</div>
            <div class="badge-name">${badge.name}</div>
            <div class="badge-desc">${badge.description}</div>
            ${!badge.unlocked && badge.progress ? `<div class="badge-progress">${badge.progress}%</div>` : ''}
        </div>
    `).join('');
}

// ==================== UI更新 ====================
function updateUI() {
    // 更新顶部进度条
    const progress = Math.round((state.currentStep / state.totalSteps) * 100);
    document.getElementById('totalProgress').style.width = `${progress}%`;
    document.getElementById('progressText').textContent = `${progress}%`;

    // 更新积分
    document.getElementById('totalPoints').textContent = `${state.points}分`;

    // 更新大纲
    initOutlineTree();

    // 更新进度抽屉
    updateProgressDrawer();
}
