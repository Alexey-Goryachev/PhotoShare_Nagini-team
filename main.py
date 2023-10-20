import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.routes.auth import router as auth_router
from src.routes.photos import router as photos_router

from src.database.db import get_db

from src.routes.auth import router as auth_router
from src.routes.comments import router as comment_router
from src.routes.tags import router as tag_router
from src.routes.users import router as user_router
app = FastAPI()

# Конфігурація OAuth2 для Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# default route for the application
# app.include_router(auth_router)
app.include_router(auth_router, prefix='/api')
app.include_router(photos_router, prefix='/api')
app.include_router(comment_router, prefix='/api')
app.include_router(tag_router, prefix='/api')
app.include_router(user_router, prefix='/api')

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


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
        raise HTTPException(status_code=500, detail="Error connecting to the database")
        

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.7", port=8000, reload=True)
