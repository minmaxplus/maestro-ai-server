"""
Maestro AI Server 自定义异常模块
@author LJY
"""


class MaestroAIError(Exception):
    """Maestro AI 服务基础异常"""
    pass


class LLMError(MaestroAIError):
    """LLM 调用相关异常"""
    pass


class ImageProcessingError(MaestroAIError):
    """图像处理异常"""
    pass


class ValidationError(MaestroAIError):
    """数据验证异常"""
    pass


class AuthenticationError(MaestroAIError):
    """认证异常"""
    pass
