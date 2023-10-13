import os
from fastapi import UploadFile


async def upload_file(file: UploadFile) -> str:
    upload_folder = "uploads"  # Директорія для зберігання файлів
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path  # Повертаємо шлях до збереженого файлу
