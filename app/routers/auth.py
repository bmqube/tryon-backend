import bcrypt
from auth.jwt_handler import signJWT
from db import get_db
from fastapi import APIRouter, Depends, HTTPException, Response
from models import User
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

class RegisterSchema(BaseModel):
    fullname: str
    email: str
    password: str

class LoginSchema(BaseModel):
    email: str
    password: str
    

@router.post("/login")
async def login(input: LoginSchema, response:Response, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == input.email).first()
        if user:
            if bcrypt.checkpw(input.password.encode('utf-8'), user.password.encode('utf-8')):
                response.status_code = 200
                return signJWT(str(user.id))
            else:
                response.status_code = 400
                return {
                    'message': "Invalid password"
                }
        else:
            response.status_code = 400
            return {
                'message': "No user found with this email"
            }
    except Exception as e:
        response.status_code = 400
        return {
            'message': str(e)
        }

@router.post("/register")
async def register(input: RegisterSchema, response:Response, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == input.email).first()
        if user:
            response.status_code = 400
            return {
                'message': "User already exists with this email"
            }

        hashed_password = bcrypt.hashpw(input.password.encode('utf-8'), bcrypt.gensalt())

        db_user = User(fullname=input.fullname, email=input.email, password=hashed_password.decode('utf-8'))

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        response.status_code = 201
        return {
            'message': "User created successfully",
            'data': {
                "id": str(db_user.id),
                "fullname": db_user.fullname,
                "email": db_user.email,
                "credit": db_user.credit
            }
        }
    except Exception as e:
        response.status_code = 400
        return {
            'message': str(e)
        }