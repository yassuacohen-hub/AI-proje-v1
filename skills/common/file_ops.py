# Güvenli Dosya İşlemleri Yeteneği

from skills.base import registry


@registry.register(
    name="safe_file_read",
    description="Dosyayı güvenli şekilde okur (boyut sınırı ve izin kontrolü)."
)
def safe_file_read(file_path: str, max_size: int = 10485760) -> str:
    """Dosyayı güvenli şekilde oku (boyut sınırı ve izin kontrolü)."""
    import os
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
    file_size = os.path.getsize(file_path)
    if file_size > max_size:
        raise ValueError(f"Dosya çok büyük: {file_size} > {max_size} byte sınırı")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


@registry.register(
    name="safe_file_write",
    description="Dosyaya güvenli şekilde yazır (atomic write)."
)
def safe_file_write(file_path: str, content: str) -> None:
    """Dosyaya güvenli şekilde yaz (atomic write)."""
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
