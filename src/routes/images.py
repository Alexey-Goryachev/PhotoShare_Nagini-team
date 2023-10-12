from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.models.image import Image, ImageCreate, ImageFile, ImageFileCreate
from src.utils import save_upload_file

router = APIRouter()


@router.post("/images/")
async def create_image(
    image: ImageCreate,
    file: UploadFile = File(None),  # Додаю завантаження файлу
    db: Session = Depends(get_db)
):
    db_image = Image(**image.dict())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    if file:
        # Зберегти завантажений файл
        file_path = save_upload_file(file, db_image.id)
        db_image.image_url = file_path
        db.commit()

    return db_image


@router.get("/images/{image_id}")
async def read_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.put("/images/{image_id}")
async def update_image(image_id: int, image: ImageCreate, db: Session = Depends(get_db)):
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    for key, value in image.dict().items():
        setattr(db_image, key, value)
    db.commit()
    db.refresh(db_image)
    return db_image


@router.delete("/images/{image_id}")
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    # Додаю видалення файлу, якщо він прив'язаний до запису
    # if db_image.image_url:
        # delete_upload_file(db_image.image_url)

    db.delete(db_image)
    db.commit()
    return {"message": "Image deleted"}

# Новий роутер для завантаження файлів


@router.post("/files/", response_model=ImageFile)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_path = save_upload_file(file)

    # Створимо запис для файлу в базі даних
    image_file = ImageFileCreate(description=file.filename)
    image_file.file_path = file_path

    return image_file
