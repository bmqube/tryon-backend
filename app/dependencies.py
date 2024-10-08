from typing import Annotated, Union

from auth.jwt_handler import decodeJWT
from db import get_db
from fastapi import Depends, Header, HTTPException
from models import User
from sqlalchemy.orm import Session


async def get_token_header(Authorization: Annotated[Union[str, None], Header()], db: Session = Depends(get_db)):
    if Authorization is None:
        raise HTTPException(status_code=400, detail="You need to be logged in to access this route")
    
    # print(Authorization)
    try:
        payload = decodeJWT(Authorization.split(" ")[1])
        # print(payload)
        user = db.query(User).filter(User.id == payload['user_id']).first()
        if user is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid token")
    