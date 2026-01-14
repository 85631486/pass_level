from app.main import create_app

app = create_app()

if __name__ == "__main__":
    # 禁用 debug 模式以避免子进程重启问题
    app.run(host="0.0.0.0", port=8000, debug=False)
