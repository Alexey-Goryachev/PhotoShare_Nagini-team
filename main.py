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
    """
    The read_items function returns a list of items.
        
        ---
        get:
          description: Get all items in the system.  This is a very long description that will be displayed on multiple lines.  It should wrap at some point, but I'm not sure how to make it do so automatically without using &lt;br&gt; tags or something like that...I guess we'll see what happens!
          responses:
            200: # HTTP status code 200 means &quot;OK&quot; (i.e., no error) and is the default response for GET requests if you don't specify anything else here...
    
    :param token: Annotated[str: Tell fastapi that the token is a string, and it should be validated using the oauth2_scheme
    :param Depends(oauth2_scheme)]: Tell fastapi that the token parameter is dependent on the oauth2_scheme
    :return: A dictionary of the form:
    """
    return {"token": token}


@app.get("/")
async def read_root():
    """
    The read_root function returns a JSON object with the message &quot;Welcome to Photoshare&quot;
        ---
        tags: [root]
        responses: 
            200: 
                description: A welcome message from Photoshare.
    
    :return: A dictionary with a key &quot;message&quot; and value &quot;welcome to photoshare&quot;
    """
    return {"message": "Welcome to Photoshare"}


@app.get("/api/healthchecker/")
async def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is used to check the health of the database.
    It will return a message if it can connect to the database, and an error otherwise.
    
    :param db: Session: Pass the database session to the function
    :return: A dictionary with a message
    """
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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
