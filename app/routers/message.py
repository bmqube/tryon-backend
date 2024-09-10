# from fastapi import APIRouter, Depends, HTTPException, Response
# from pydantic import BaseModel
# from models import ChatMessage, ChatSession, ChapterContent
# from db import get_db
# from sqlalchemy.orm import Session
# from dependencies import get_token_header
# import google.generativeai as genai
# from google.api_core import exceptions as google_exceptions
# import logging

# router = APIRouter(
#     prefix="/message",
#     tags=["message"],
#     responses={404: {"description": "Not found"}},
# )

# class MessageSchema(BaseModel):
#     session_id: str
#     message: str

# class UserSchema(BaseModel):
#     id: str
#     fullname: str
#     email: str
#     class_num: int

# # Function to get chapter content from the database
# def get_chapter_content(db: Session, class_num: int, book_name: str, chapter_no: int) -> str:
#     chapter_content = db.query(ChapterContent).filter(
#         ChapterContent.class_num == class_num,
#         ChapterContent.book_name == book_name,
#         ChapterContent.chapter_no == chapter_no
#     ).first()
    
#     if not chapter_content:
#         raise HTTPException(status_code=404, detail="Chapter content not found")

#     return chapter_content.content

# # Updated getResponse function
# async def getResponse(prompt: str, chapter_content:str, chat_history: list[ChatMessage]) -> str:
#     # Fetch the chapter content from the database
    
#     generation_config = {
#         "temperature": 0.9,
#         "top_p": 0.95,
#         "top_k": 1,
#         "max_output_tokens": 99998,
#     }
#     safety_settings = [
#         {
#             "category": "HARM_CATEGORY_DANGEROUS",
#             "threshold": "BLOCK_NONE",
#         },
#         {
#             "category": "HARM_CATEGORY_HARASSMENT",
#             "threshold": "BLOCK_NONE",
#         },
#         {
#             "category": "HARM_CATEGORY_HATE_SPEECH",
#             "threshold": "BLOCK_NONE",
#         },
#         {
#             "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#             "threshold": "BLOCK_NONE",
#         },
#         {
#             "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#             "threshold": "BLOCK_NONE",
#         },
#     ]

#     instruction =  """
#     You are a helpful assistant tutor for a 9th grade student. 
#     Your task is to assist the student with their understanding using the given context.
#     Don't give answers directly rather try to assist them with guiding hints.
#     The context for the chapter is as follows:
#     """ + chapter_content
#     print(instruction)
#     if len(chat_history)>0:
#         formatted_chat_history = [
#             {
#                 'role': 'model' if obj.is_response else 'user',
#                 'parts': [obj.message]
#             }
#             for obj in chat_history
#         ]
#         formatted_chat_history.reverse()
#         formatted_chat_history.append(            
#             {
#                 'role': 'user',
#                 'parts': [prompt]
#             })
#         # print(formatted_chat_history)
#     else:
#         formatted_chat_history=[
#         {
#             'role': 'user' ,
#             'parts': [prompt]
#         }
            
#         ]
        

#     api_key = ""
#     genai.configure(api_key=api_key)
#     genini = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=instruction)
#     try:
#         res = genini.generate_content(formatted_chat_history,
#                                     generation_config=generation_config,stream=True,safety_settings=safety_settings)
#     except google_exceptions.InvalidArgument as e:
#         print(e)
#     except Exception as e:
#         logging.error(e)
#         print("Error occured. Please refresh your page and try again.")
        
#     if res is not None:
#         res_text = ""
#         for chunk in res:
#             if chunk.candidates:
#                 res_text += chunk.text
#             if res_text == "":
#                 res_text = "unappropriate words"
#                 print("Your words violate the rules that have been set. Please try again!")

#     # Here, you would normally use the chapter_content and prompt to generate a response.
#     # For this example, let's just return the content and the prompt together
#     return res_text

# @router.post("/")
# async def sendMessage(input: MessageSchema, response: Response, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_token_header)):
#     try:
#         current_session: ChatSession = db.query(ChatSession).filter(ChatSession.id == input.session_id).first()
        
#         if not current_session:
#             raise HTTPException(status_code=404, detail="Chat session not found")

#         db_message = ChatMessage(session_id=input.session_id, message=input.message, is_response=False)
#         db.add(db_message)

#         chapter_content = get_chapter_content(db, current_session.class_num, current_session.book_name, current_session.chapter_no)

#         chat_history = db.query(ChatMessage).filter(ChatMessage.session_id == input.session_id).order_by(ChatMessage.created_at.desc()).limit(6).all()
            
#         # Pass the db session to getResponse
#         llm_response = await getResponse(input.message, chapter_content, chat_history)
#         db.commit()

#         dp_message_response = ChatMessage(session_id=input.session_id, message=llm_response, is_response=True)
#         db.add(dp_message_response)
#         db.commit()

#         db.refresh(dp_message_response)
        
#         response.status_code = 201
#         return {
#             'message': "Message sent successfully",
#             'data': dp_message_response
#         }
#     except HTTPException as e:
#         response.status_code = e.status_code
#         return {
#             'message': e.detail
#         }
#     except Exception as e:
#         response.status_code = 400
#         return {
#             'message': str(e)
#         }
