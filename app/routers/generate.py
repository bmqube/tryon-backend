from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile
from pydantic import BaseModel
from db import get_db
from sqlalchemy.orm import Session
from dependencies import get_token_header
import os

directory = "files"
if not os.path.exists(directory):
    os.makedirs(directory)

router = APIRouter(
    prefix="/generate",
    tags=["generate"],
    responses={404: {"description": "Not found"}},
)

class UserSchema(BaseModel):
    id: str
    fullname: str
    email: str

@router.get("/")
async def getAllSession(response: Response, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_token_header)):
    try:
        sessions = db.query(ChatSession).filter(ChatSession.created_by == current_user.id).all()
        response.status_code = 200
        return {
            'message': "All Sessions",
            'data': sessions
        }
    except Exception as e:
        response.status_code = 400
        return {
            'message': str(e)
        }
    
@router.get("/{session_id}")
async def getAllMessage(session_id: str, response: Response, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_token_header)):
    try:
        current_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()

        if current_session is None:
            response.status_code = 400
            return {
                'message': "No session found with this id"
            }
        
        if current_session.created_by != current_user.id:
            response.status_code = 400
            return {
                'message': "You are not allowed to access this session"
            }

        messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
        response.status_code = 200
        return {
            'message': "All Messages",
            'data': {
                'session': current_session,
                'messages': messages
            }
        }
    except Exception as e:
        response.status_code = 400
        return {
            'message': str(e)
        }

@router.post("/")
async def createSession(files: list[UploadFile], response: Response, db: Session = Depends(get_db)):
    try:
        for file in files:
            file_location = f"{directory}/{file.filename}"
            with open(file_location, "wb+") as file_object:
                file_object.write(file.file.read())
        return {"filenames": [file.filename for file in files]}
        
        return {
            'message': "Session created successfully",
            'data': 'db_session'
        }
    except Exception as e:
        response.status_code = 400
        return {
            'message': str(e)
        }