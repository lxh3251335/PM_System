"""
密码哈希工具模块
使用 bcrypt 哈希，兼容旧版 SHA256 格式并支持自动迁移
"""
import hashlib
import bcrypt


def hash_password_bcrypt(password: str) -> str:
    """使用 bcrypt 哈希密码"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码，兼容 bcrypt 和旧版 SHA256"""
    if hashed.startswith("$2"):
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    return hashed == hashlib.sha256(plain.encode("utf-8")).hexdigest()


def needs_rehash(hashed: str) -> bool:
    """判断是否是旧的 SHA256 格式，需要迁移到 bcrypt"""
    return not hashed.startswith("$2")
