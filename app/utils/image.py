"""
Maestro AI Server - 图像处理工具
@author LJY
"""

import base64
from io import BytesIO

from PIL import Image

from app.core import ImageProcessingError


def validate_image(image_data: bytes) -> bool:
    """验证图像数据是否有效"""
    try:
        img = Image.open(BytesIO(image_data))
        img.verify()
        return True
    except Exception:
        return False


def decode_base64_image(base64_string: str | bytes) -> bytes:
    """解码 Base64 图像字符串为原始字节"""
    try:
        if isinstance(base64_string, bytes):
            base64_string = base64_string.decode("utf-8")
        
        # 处理带前缀的 Base64 (如 data:image/png;base64,...)
        if "," in base64_string:
            base64_string = base64_string.split(",", 1)[1]
        
        return base64.b64decode(base64_string)
    except Exception as e:
        raise ImageProcessingError(f"Base64 解码失败: {e}")


def encode_image_to_base64(image_data: bytes) -> str:
    """将图像字节编码为 Base64 字符串"""
    return base64.b64encode(image_data).decode("utf-8")


def get_image_mime_type(image_data: bytes) -> str:
    """获取图像 MIME 类型"""
    try:
        img = Image.open(BytesIO(image_data))
        format_map = {
            "PNG": "image/png",
            "JPEG": "image/jpeg",
            "GIF": "image/gif",
            "WEBP": "image/webp",
        }
        return format_map.get(img.format, "image/png")
    except Exception:
        return "image/png"  # 默认 PNG


def resize_image_if_needed(
    image_data: bytes,
    max_size: tuple[int, int] = (2048, 2048)
) -> bytes:
    """
    如果图像过大则缩放
    避免超出 LLM 的输入限制
    """
    try:
        img = Image.open(BytesIO(image_data))
        
        if img.width <= max_size[0] and img.height <= max_size[1]:
            return image_data
        
        # 保持宽高比缩放
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format=img.format or "PNG")
        return output.getvalue()
    except Exception as e:
        raise ImageProcessingError(f"图像缩放失败: {e}")
