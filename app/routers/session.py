# from fastapi import APIRouter, Depends, HTTPException, Response
# from pydantic import BaseModel
# from models import ChatSession, ChatMessage
# import hashlib, uuid
# from db import get_db
# from sqlalchemy.orm import Session
# import bcrypt
# from auth.jwt_handler import signJWT
# from dependencies import get_token_header

# router = APIRouter(
#     prefix="/session",
#     tags=["session"],
#     responses={404: {"description": "Not found"}},
# )

# class SessionSchema(BaseModel):
#     book_name: str
#     chapter_no: int

# class UserSchema(BaseModel):
#     id: str
#     fullname: str
#     email: str
#     class_num: int

# @router.get("/")
# async def getAllSession(response: Response, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_token_header)):
#     try:
#         sessions = db.query(ChatSession).filter(ChatSession.created_by == current_user.id).all()
#         response.status_code = 200
#         return {
#             'message': "All Sessions",
#             'data': sessions
#         }
#     except Exception as e:
#         response.status_code = 400
#         return {
#             'message': str(e)
#         }
    
# @router.get("/{session_id}")
# async def getAllMessage(session_id: str, response: Response, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_token_header)):
#     try:
#         current_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()

#         if current_session is None:
#             response.status_code = 400
#             return {
#                 'message': "No session found with this id"
#             }
        
#         if current_session.created_by != current_user.id:
#             response.status_code = 400
#             return {
#                 'message': "You are not allowed to access this session"
#             }

#         messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
#         response.status_code = 200
#         return {
#             'message': "All Messages",
#             'data': {
#                 'session': current_session,
#                 'messages': messages
#             }
#         }
#     except Exception as e:
#         response.status_code = 400
#         return {
#             'message': str(e)
#         }

# @router.post("/")
# async def createSession(input: SessionSchema, response: Response, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_token_header)):
#     try:
#         chat_name =  input.book_name + ' - Chapt.' + str(input.chapter_no)
#         db_session = ChatSession(name=chat_name, created_by=current_user.id, class_num=current_user.class_num, book_name=input.book_name, chapter_no=input.chapter_no)

#         db.add(db_session)
#         db.commit()
#         db.refresh(db_session)

#         response.status_code = 201
#         return {
#             'message': "Session created successfully",
#             'data': db_session
#         }
#     except Exception as e:
#         response.status_code = 400
#         return {
#             'message': str(e)
#         }