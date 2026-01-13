"""
通用异常类
"""


class BaseAppException(Exception):
    """应用基础异常类"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(BaseAppException):
    """资源未找到异常"""
    def __init__(self, message: str = "资源未找到"):
        super().__init__(message, code=404)


class ValidationError(BaseAppException):
    """验证错误异常"""
    def __init__(self, message: str = "验证失败"):
        super().__init__(message, code=400)


class UnauthorizedError(BaseAppException):
    """未授权异常"""
    def __init__(self, message: str = "未授权"):
        super().__init__(message, code=401)


class ForbiddenError(BaseAppException):
    """禁止访问异常"""
    def __init__(self, message: str = "禁止访问"):
        super().__init__(message, code=403)


class ConflictError(BaseAppException):
    """冲突异常"""
    def __init__(self, message: str = "资源冲突"):
        super().__init__(message, code=409)

