from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.models.image import Image, ImageCreate

router = APIRouter()

# Створення зображення


@router.post("/images/")
async def create_image(image: ImageCreate, db: Session = Depends(get_db)):
    db_image = Image(**image.dict())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# Отримання зображення за ідентифікатором


@router.get("/images/{image_id}")
async def read_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

# Оновлення зображення за ідентифікатором


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

# Видалення зображення за ідентифікатором


@router.delete("/images/{image_id}")
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    db.delete(db_image)
    db.commit()
    return {"message": "Image deleted"}
