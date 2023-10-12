import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.routes.auth import router
from src.authentication.app import app as fastapi_app
from src.database.db import get_db

app = FastAPI()

app.include_router(router, prefix='/api')
app.mount("/auth", fastapi_app)


#default route for the application
@app.get("/")
async def read_root():
    return {"message": "Welcome to Photoshare"}


@app.get("/api/healthchecker/")
async def healthchecker(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome, connection established!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.7", port=8000, reload=True)
