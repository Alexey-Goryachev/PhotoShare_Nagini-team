import os
import uuid  # Додайте цей імпорт
from fastapi import UploadFile
from pathlib import Path

# Функція для завантаження файлу на сервер


async def upload_file(file: UploadFile):
    # Створіть шлях для завантаження файлу
    upload_folder = "upload_folder"  # Замініть це на шлях до вашої теки завантаження
    Path(upload_folder).mkdir(parents=True, exist_ok=True)

    # Генеруйте унікальне ім'я файлу
    file_name = f"{str(uuid.uuid4())}_{file.filename}"

    # Створіть повний шлях до файлу
    file_path = os.path.join(upload_folder, file_name)

    # Зчитайте дані з файлу та збережіть їх у новий файл
    with open(file_path, "wb") as new_file:
        new_file.write(file.file.read())

    return file_name
