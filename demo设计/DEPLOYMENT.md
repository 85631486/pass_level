# 部署指南

## 📦 快速部署步骤

### 第一步：环境准备

#### 1. 安装Python 3.8+
```bash
python --version
```

#### 2. 安装Node.js 16.0+
```bash
node --version
npm --version
```

### 第二步：后端部署

#### 1. 进入后端目录
```bash
cd backend
```

#### 2. 创建虚拟环境（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 修改配置
打开 `app.py`，修改以下配置：
```python
app.config['SECRET_KEY'] = 'your-secret-key-change-this'  # 修改为随机字符串
```

#### 5. 初始化数据库
```bash
python app.py
```

第一次运行会自动创建 `learning_platform.db` 数据库文件。

按 `Ctrl+C` 停止服务器。

#### 6. 导入示例数据（可选）

创建文件 `init_data.py`：
```python
from app import app, db
from models import Course, Task, Operation, Badge
import json

with app.app_context():
    # 创建课程
    course = Course(
        course_code='COURSE-01',
        course_name='玩转数据从个人生活开始',
        description='大数据课程第一课'
    )
    db.session.add(course)
    db.session.commit()

    # 创建任务
    task = Task(
        course_id=course.id,
        task_code='TASK-02',
        task_name='Excel界面速通',
        task_order=2,
        total_operations=10,
        total_questions=30,
        time_limit=90
    )
    db.session.add(task)
    db.session.commit()

    # 创建操作（示例：操作1）
    operation1 = Operation(
        task_id=task.id,
        operation_code='OP-01',
        operation_name='选中单元格与区域',
        operation_order=1,
        description='学习如何选中Excel中的单元格和区域',
        steps=json.dumps([
            '将鼠标指针移动到想要选中的单元格上',
            '用鼠标左键单击一下该单元格',
            '单元格周围会出现黑色边框，表示已选中'
        ]),
        practice_task='在数据文件中选中"商品名称"整列',
        points=10
    )
    db.session.add(operation1)
    db.session.commit()

    print('示例数据导入成功！')
```

运行导入脚本：
```bash
python init_data.py
```

#### 7. 启动后端服务
```bash
python app.py
```

后端服务将在 `http://localhost:5000` 运行。

### 第三步：前端部署

#### 1. 进入前端目录
```bash
cd frontend
```

#### 2. 安装依赖
```bash
npm install
# 或使用 yarn
yarn install
```

如果安装速度慢，可以使用淘宝镜像：
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

#### 3. 启动开发服务器
```bash
npm run dev
```

前端服务将在 `http://localhost:3000` 运行。

#### 4. 访问应用
打开浏览器访问：`http://localhost:3000`

### 第四步：注册测试账号

1. 点击"注册"标签
2. 输入学号：`20240001`
3. 输入姓名：`测试学生`
4. 输入密码：`123456`
5. 点击"注册"按钮
6. 切换到"登录"标签
7. 使用刚才的学号和密码登录

## 🔧 生产环境部署

### 后端生产部署

#### 使用 Gunicorn（推荐）

1. 安装 Gunicorn
```bash
pip install gunicorn
```

2. 创建 `gunicorn.conf.py`：
```python
bind = '0.0.0.0:5000'
workers = 4
timeout = 120
```

3. 启动服务
```bash
gunicorn -c gunicorn.conf.py app:app
```

#### 使用 Nginx 反向代理

创建 `/etc/nginx/sites-available/learning-platform`：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/learning-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 前端生产部署

1. 构建生产版本
```bash
cd frontend
npm run build
```

2. 将 `dist` 目录部署到服务器
```bash
# 使用 scp 上传
scp -r dist/* user@server:/var/www/learning-platform/
```

3. 配置 Nginx（见上面的配置）

## 🔐 安全配置

### 1. 修改 SECRET_KEY
在 `backend/app.py` 中：
```python
import secrets
app.config['SECRET_KEY'] = secrets.token_hex(32)
```

### 2. 限制文件上传
在 `backend/app.py` 中已配置：
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'xlsx'}
```

### 3. CORS 配置
生产环境建议限制跨域来源：
```python
from flask_cors import CORS
CORS(app, origins=['https://your-domain.com'])
```

### 4. HTTPS 配置
使用 Let's Encrypt 免费SSL证书：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 数据备份

### 备份数据库
```bash
# 复制数据库文件
cp backend/learning_platform.db backup/learning_platform_$(date +%Y%m%d).db
```

### 自动备份脚本
创建 `backup.sh`：
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backup"
mkdir -p $BACKUP_DIR
cp backend/learning_platform.db $BACKUP_DIR/learning_platform_$DATE.db
# 保留最近7天的备份
find $BACKUP_DIR -name "learning_platform_*.db" -mtime +7 -delete
```

添加到 crontab（每天凌晨2点备份）：
```bash
0 2 * * * /path/to/backup.sh
```

## 🐛 故障排查

### 问题1：后端启动失败

**错误**: `ModuleNotFoundError: No module named 'flask'`

**解决**: 确认已激活虚拟环境并安装依赖
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 问题2：前端连接后端失败

**错误**: `Network Error` 或 `CORS Error`

**解决**:
1. 确认后端已启动在 `http://localhost:5000`
2. 检查 `frontend/vite.config.js` 中的代理配置
3. 确认 `backend/app.py` 中启用了 CORS

### 问题3：数据库锁定

**错误**: `database is locked`

**解决**: SQLite不适合高并发，生产环境建议使用PostgreSQL或MySQL

### 问题4：文件上传失败

**错误**: `413 Request Entity Too Large`

**解决**: 增加 Nginx 上传限制
```nginx
client_max_body_size 20M;
```

## 📞 技术支持

如遇到部署问题，请检查：
1. Python 和 Node.js 版本是否符合要求
2. 所有依赖是否正确安装
3. 端口 5000 和 3000 是否被占用
4. 防火墙是否开放相应端口

## ✅ 部署检查清单

- [ ] Python 3.8+ 已安装
- [ ] Node.js 16.0+ 已安装
- [ ] 后端依赖已安装
- [ ] 前端依赖已安装
- [ ] 数据库已初始化
- [ ] 示例数据已导入
- [ ] 后端服务正常启动
- [ ] 前端服务正常启动
- [ ] 能够成功注册和登录
- [ ] 文件上传功能正常
- [ ] 数据库备份已配置
