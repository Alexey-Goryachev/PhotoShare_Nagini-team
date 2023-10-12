from sqlalchemy import text
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.models.image import Image, ImageCreate  # Імпорт моделі для зображень
from src.routes.images import router  # Імпорт маршрутів для зображень

app = FastAPI()


# default route for the application
@app.get("/")
async def read_root():
    return {"message": "Welcome to Photoshare"}


@app.get("/api/healthchecker/")
async def healthchecker(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome, connection established!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Error connecting to the database")


# Підключення маршрутів для роботи з зображеннями
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.7", port=8000,
                reload=True, log_level="debug")
