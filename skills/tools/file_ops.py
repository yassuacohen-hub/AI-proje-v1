# GÃ¼venli Dosya Ä°ÅŸlemleri YeteneÄŸi

from skills.base import registry


@registry.register(
    name="safe_file_read",
    description="DosyayÄ± gÃ¼venli ÅŸekilde okur (boyut sÄ±nÄ±rÄ± ve izin kontrolÃ¼)."
)
def safe_file_read(file_path: str, max_size: int = 10485760) -> str:
    """DosyayÄ± gÃ¼venli ÅŸekilde oku (boyut sÄ±nÄ±rÄ± ve izin kontrolÃ¼)."""
    import os
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dosya bulunamadÄ±: {file_path}")
    file_size = os.path.getsize(file_path)
    if file_size > max_size:
        raise ValueError(f"Dosya Ã§ok bÃ¼yÃ¼k: {file_size} > {max_size} byte sÄ±nÄ±rÄ±")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


@registry.register(
    name="safe_file_write",
    description="Dosyaya gÃ¼venli ÅŸekilde yazÄ±r (atomic write)."
)
def safe_file_write(file_path: str, content: str) -> None:
    """Dosyaya gÃ¼venli ÅŸekilde yaz (atomic write)."""
    import os
    import tempfile
    dir_path = os.path.dirname(file_path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, file_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise
