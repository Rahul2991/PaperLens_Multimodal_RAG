import time, os, hashlib, magic

def get_unique_filename(filename: str) -> str:
    """Generate a unique filename"""
    timestamp = int(time.time())  # Add a timestamp
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"
    return new_filename

def get_file_hash(file_bytes: bytes) -> str:
    """Generate SHA256 hash for file content."""
    return hashlib.sha256(file_bytes).hexdigest()

async def is_image(file_bytes: bytes) -> bool:
    """Check if the file is an image using MIME type."""
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_bytes)
    return file_type.startswith("image/")

async def is_txt(file_bytes: bytes) -> bool:
    """Check if the file is an image using MIME type."""
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_bytes)
    return file_type == "text/plain"

async def is_pdf(file_bytes: bytes) -> bool:
    """Check if the file is an image using MIME type."""
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_bytes)
    return file_type == "application/pdf"