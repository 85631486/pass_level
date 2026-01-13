# 过关斩将 - 游戏教学平台 2.0

## 📋 项目简介

这是一个基于 Vue.js + Flask + SQLite 的交互式学习系统，专为《Excel界面速通》等实操课程设计。系统采用游戏化教学理念，通过关卡、积分、徽章等机制，让学生在实际操作中不断发现和学习知识技巧。

## ✨ 核心功能

### 1. 学习模块
- **任务学习页面**：大页面设计，抽屉式收纳各板块
- **分步骤操作指导**：每个操作都有详细步骤说明
- **实时知识卡片**：完成操作后自动弹出相关知识卡片
- **操作结果提交**：支持文件上传（截图、文档）

### 2. 测试系统
- **即时测试题**：每个操作完成后弹出相关测试题
- **统一测试**：所有操作完成后的综合测试
- **答题反馈**：即时显示正确答案和解析

### 3. 游戏化元素
- **关卡系统**：10个操作 = 10个关卡
- **积分系统**：操作提交、答题正确获得积分
- **成就徽章**：完成特定条件解锁徽章
- **知识卡片收集**：收集学习过程中的知识卡片

### 4. 进度管理
- **学习进度跟踪**：实时显示完成度
- **提交记录查看**：查看所有操作提交历史
- **学习总结报告**：完成后生成个人学习总结

## 🏗️ 技术架构

### 前端技术栈
- **Vue 3**：渐进式JavaScript框架
- **Vite**：下一代前端构建工具
- **Element Plus**：Vue 3 UI组件库
- **Pinia**：Vue 3 状态管理
- **Vue Router**：路由管理
- **Axios**：HTTP客户端

### 后端技术栈
- **Flask**：Python轻量级Web框架
- **Flask-SQLAlchemy**：ORM工具
- **Flask-CORS**：跨域资源共享
- **SQLite**：轻量级数据库
- **Werkzeug**：文件上传处理

## 📁 项目结构

```
demo设计/
├── backend/                    # 后端项目
│   ├── app.py                 # Flask主应用
│   ├── models.py              # 数据库模型
│   ├── requirements.txt       # Python依赖
│   └── uploads/               # 文件上传目录
│
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── api/               # API接口
│   │   │   └── index.js
│   │   ├── stores/            # Pinia状态管理
│   │   │   ├── user.js
│   │   │   └── learning.js
│   │   ├── router/            # 路由配置
│   │   │   └── index.js
│   │   ├── views/             # 页面组件
│   │   │   ├── Login.vue
│   │   │   ├── TaskList.vue
│   │   │   ├── LearningPage.vue
│   │   │   └── Summary.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
└── database_design.sql        # 数据库设计文档
```

## 🚀 快速开始

### 环境要求

- **Node.js**: 16.0+
- **Python**: 3.8+
- **npm** 或 **yarn**

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python app.py
```

首次运行会自动创建数据库和表结构。

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动开发服务器

**启动后端（端口5000）：**
```bash
cd backend
python app.py
```

**启动前端（端口3000）：**
```bash
cd frontend
npm run dev
```

### 5. 访问应用

打开浏览器访问：`http://localhost:3000`

## 📊 数据库设计

系统包含14张主要数据表：

1. **students** - 学生表
2. **courses** - 课程表
3. **tasks** - 任务表
4. **operations** - 操作步骤表
5. **knowledge_cards** - 知识卡片表（预定义）
6. **instant_questions** - 即时测试题表
7. **unified_questions** - 统一测试题表
8. **badges** - 成就徽章表
9. **student_progress** - 学生学习进度表
10. **operation_submissions** - 操作提交记录表
11. **instant_answers** - 即时测试答题记录
12. **unified_answers** - 统一测试答题记录
13. **student_badges** - 学生获得徽章记录
14. **student_knowledge_cards** - 知识卡片收集记录

详细设计见 `database_design.sql` 文件。

## 🎮 使用流程

### 学生使用流程

1. **注册/登录**
   - 输入学号、姓名、密码注册
   - 登录后进入任务列表

2. **选择任务**
   - 查看任务列表
   - 点击任务卡片开始学习

3. **学习操作**
   - 阅读操作说明和详细步骤
   - 查看知识卡片
   - 完成练习任务
   - 上传操作结果（截图）

4. **即时测试**
   - 完成操作后弹出测试题
   - 选择答案并提交
   - 查看正确答案和解析

5. **统一测试**
   - 完成所有操作后
   - 进行综合测试
   - 提交答案获得积分

6. **完成学习**
   - 点击"完成学习"按钮
   - 查看学习总结报告
   - 获得徽章奖励

### 教师/管理员操作

1. **初始化数据库**
   ```bash
   POST /api/init-db
   ```

2. **导入课程数据**
   - 手动插入课程、任务、操作等数据
   - 或编写数据导入脚本

3. **配置知识卡片**
   - 为每个操作配置知识卡片
   - 设置卡片类型和触发时机

4. **设置测试题**
   - 配置即时测试题
   - 配置统一测试题
   - 设置正确答案和解析

5. **配置徽章**
   - 创建成就徽章
   - 设置解锁条件

## 🎨 界面设计

### 色调
- **主色调**：白色和灰色
- **强调色**：渐变紫色（#667eea - #764ba2）
- **成功色**：绿色（#67c23a）
- **警告色**：橙色（#ffa500）

### 布局特点
- **大页面设计**：主内容区占据主要空间
- **抽屉式收纳**：右侧抽屉展示辅助信息
- **浮动按钮**：快速访问各功能模块
- **知识卡片浮动**：右侧固定位置显示

## 🔌 API接口文档

### 认证相关
- `POST /api/auth/login` - 登录
- `POST /api/auth/register` - 注册

### 任务相关
- `GET /api/tasks` - 获取任务列表
- `GET /api/tasks/:id` - 获取任务详情

### 操作相关
- `GET /api/operations/:id` - 获取操作详情
- `POST /api/operations/:id/submit` - 提交操作结果

### 测试题相关
- `POST /api/questions/instant/:id/answer` - 回答即时测试题
- `GET /api/tasks/:id/unified-questions` - 获取统一测试题
- `POST /api/tasks/:id/unified-test/submit` - 提交统一测试

### 进度相关
- `POST /api/progress/start` - 开始任务
- `GET /api/progress/:studentId/:taskId` - 获取进度
- `POST /api/progress/complete` - 完成任务

### 知识卡片相关
- `POST /api/knowledge-cards/collect` - 收集知识卡片
- `GET /api/knowledge-cards/:studentId` - 获取已收集卡片

### 徽章相关
- `GET /api/badges/:studentId` - 获取学生徽章

### 总结相关
- `GET /api/summary/:studentId/:taskId` - 获取学习总结

## 📝 后续扩展建议

### 短期扩展
1. **数据导入工具**：从Markdown文件自动解析并导入数据
2. **后台管理界面**：管理课程、任务、题目等
3. **成绩导出**：导出学生成绩为Excel
4. **学习报告PDF**：生成PDF格式的学习报告

### 长期扩展
1. **AI辅助学习**：集成AI答疑功能
2. **协作学习**：学生间可以互相帮助
3. **视频教程**：嵌入操作演示视频
4. **实时评分**：根据提交内容自动评分
5. **排行榜系统**：学生积分排行
6. **多课程支持**：扩展到其他实操课程

## 🐛 已知问题

1. 文件上传大小限制为16MB
2. 暂不支持移动端适配
3. 暂无后台管理界面

## 📄 License

MIT License

## 👥 贡献者

设计开发：Claude Code

## 📮 联系方式

如有问题或建议，请提交 Issue。
