from fastapi import UploadFile
from pathlib import Path


def save_upload_file(file: UploadFile, filename: str = None):
    upload_dir = "uploads"
    upload_dir_path = Path(upload_dir)
    upload_dir_path.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir_path / (filename or file.filename)

    with file_path.open("wb") as f:
        f.write(file.file.read())

    return str(file_path)


def delete_upload_file(file_path: str):
    path = Path(file_path)
    if path.exists():
        path.unlink()
