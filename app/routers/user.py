from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, Form
from pydantic import BaseModel
from db import get_db
from sqlalchemy.orm import Session
from dependencies import get_token_header
import os
from models import User
import uuid
import magic
from PIL import Image
from typing import Annotated
import httpx
from io import BytesIO

directory = "files"
if not os.path.exists(directory):
    os.makedirs(directory)

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

class UserSchema(BaseModel):
    id: str
    fullname: str
    email: str

class creditSchema(BaseModel):
    email: str
    credit: int

@router.get("/credit")
async def getUserCredit(response:Response, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_token_header)):
    try:
        user = db.query(User).filter(User.email == current_user.email).first()

        if user is None:
            response.status_code = 400
            return {
                'message': "No user found with this email"
            }
        
        return {
            'message': "User credit",
            'data': {
                'email': user.email,
                'credit': user.credit
            }
        }
    except Exception as e:
        response.status_code = 400
        return {
            'message': str(e)
        }

@router.put("/credit")
async def appendCredit(input: creditSchema, response: Response, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_token_header)):
    try:
        # print(current_user.email)
        if current_user.role != "admin":
            response.status_code = 400
            return {
                'message': "You are not allowed to access this endpoint"
            }
        
        user = db.query(User).filter(User.email == input.email).first()

        if user is None:
            response.status_code = 400
            return {
                'message': "No user found with this email"
            }
        
        user.credit += int(input.credit)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            'message': "Credit added successfully",
            'data': {
                'email': user.email,
                'credit': user.credit
            }
        }
    except Exception as e:
        response.status_code = 400
        return {
            'message': str(e)
        }