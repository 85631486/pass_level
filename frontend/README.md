# 学生端（H5）工程

## 准备

- Node.js ≥ 20.15（建议 20.19+ 以避免 Vite 提示）
- npm 10+

## 安装

```powershell
cd frontend
npm install
cp .env.example .env   # 或手动创建 .env
```

`VITE_API_BASE_URL` 默认指向 `http://127.0.0.1:8000/api/v1`。

## 启动

```powershell
npm run dev
```

开发服务器默认运行在 `http://127.0.0.1:5173`。

## 构建

```powershell
npm run build
npm run preview
```

## 目录要点

- `src/router`：路由与登录态守卫
- `src/stores/auth.ts`：Pinia 认证状态、API 调用
- `src/pages`：登录、注册、Dashboard 页面
- `src/api/http.ts`：Axios 实例与拦截器
