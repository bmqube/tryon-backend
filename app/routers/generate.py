from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, Form
from pydantic import BaseModel
from db import get_db
from sqlalchemy.orm import Session
from dependencies import get_token_header
import os
from models import GeneratedImage
import uuid
import magic
from PIL import Image
from typing import Annotated

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
async def getGeneratedImageList(response: Response, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_token_header)):
    try:
        generated_images = db.query(GeneratedImage).filter(GeneratedImage.user_id == current_user.id).all()
        response.status_code = 200
        return {
            'message': "All Generated Images",
            'data': generated_images
        }
    except Exception as e:
        response.status_code = 400
        return {
            'message': str(e)
        }
    
@router.get("/{generated_image_id}")
async def getGeneratedImageDetails(generated_image_id: str, response: Response, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_token_header)):
    try:
        generated_image = db.query(GeneratedImage).filter(GeneratedImage.id == generated_image_id).first()

        if generated_image is None:
            response.status_code = 400
            return {
                'message': "No session found with this id"
            }
        
        if generated_image.user_id != current_user.id:
            response.status_code = 400
            return {
                'message': "You are not allowed to access this session"
            }
        
        response.status_code = 200
        return {
            'message': "Successfully fetched the generated image",
            'data': generated_image
        }
    except Exception as e:
        response.status_code = 400
        return {
            'message': str(e)
        }
    
async def save_image(file: UploadFile):
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(await file.read())
    await file.seek(0)  # Reset file pointer to the beginning

    if not file_mime_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    _, file_extension = os.path.splitext(file.filename)

    new_filename = str(uuid.uuid4()) + file_extension

    file_location = f"{directory}/{new_filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

        # Create and save thumbnail
    thumbnail_filename = str(uuid.uuid4()) + "_thumbnail" + file_extension
    thumbnail_location = f"{directory}/{thumbnail_filename}"

    with Image.open(file_location) as img:
        img.thumbnail((256, 256))  # Resize image to thumbnail size
        img.save(thumbnail_location)

    return {
        'filename': new_filename,
        'thumbnail': thumbnail_filename
    }

@router.post("/")
async def generateImage(model_image: UploadFile, cloth_image: UploadFile, position: Annotated[str, Form()], response: Response, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_token_header)):
    try:

        model_image_data = await save_image(model_image)
        cloth_image_data = await save_image(cloth_image)

        generated_image = GeneratedImage(
            user_id=current_user.id,
            model_image=model_image_data,
            cloth_image=cloth_image_data,
            position=position,
            generated_image=model_image_data
        )
        
        db.add(generated_image)
        db.commit()
        db.refresh(generated_image)
        
        return {
            'message': "Session created successfully",
            'data': generated_image
        }
    except Exception as e:
        response.status_code = 400
        return {
            'message': str(e)
        }