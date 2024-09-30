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
import httpx
from io import BytesIO
from typing import Optional
from fastapi.responses import JSONResponse

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

async def fetch_data(
    person_image: UploadFile, 
    cloth_image: UploadFile, 
    position: str, 
    mask_image: UploadFile = None, 
    guidance_scale: float = 2.55, 
    num_inference_steps: int=15,
    seed:int=422
) -> UploadFile:
    
    print("HEDA 2", num_inference_steps, seed, guidance_scale)

    url = "https://galilei.fringecore.sh/tryon"  # Replace with the actual API URL
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=100) as client:
            files = {
                'person_image': (person_image.filename, person_image.file, person_image.content_type),
                'cloth_image': (cloth_image.filename, cloth_image.file, cloth_image.content_type)
            }

            if mask_image is not None:
                files['mask_image'] = (mask_image.filename, mask_image.file, mask_image.content_type)

            data = {
                'cloth_type': position,
                'guidance_scale': guidance_scale,
                'num_inference_steps': num_inference_steps,
                'seed': seed
            }

            response = await client.post(url, files=files, data=data)
            response.raise_for_status()

            file_content = response.content
            file_name = "generated_image.jpg"

            upload_file = UploadFile(filename=file_name, file=BytesIO(file_content))
            return upload_file
    except httpx.HTTPStatusError as exc:
        print("HEDA")
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        print(exc)
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/")
async def generateImage(
    person_image: UploadFile, 
    cloth_image: UploadFile, 
    position: Annotated[str, Form()], 
    response: Response,
    mask_image: UploadFile = None, 
    guidance_scale: Annotated[str, Form()] = "2.35", 
    num_inference_steps: Annotated[str, Form()] = "10",
    seed: Annotated[str, Form()] = "130", 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_token_header)
):
    # print("HEDA", num_inference_steps, seed, guidance_scale)
    try:
        if current_user.credit < 1:
            response.status_code = 400
            return {
                'message': "You do not have enough credits to create a session"
            }
        person_image_data = await save_image(person_image)
        cloth_image_data = await save_image(cloth_image)

        data = await fetch_data(person_image, cloth_image, position, mask_image, float(guidance_scale), int(num_inference_steps), int(seed))
        generated_image_data = await save_image(data)
        
        generated_image = GeneratedImage(
            user_id=current_user.id,
            person_image=person_image_data,
            cloth_image=cloth_image_data,
            position=position,
            generated_image=generated_image_data
        )

        current_user.credit -= 1
        db.add(current_user)
        
        db.add(generated_image)
        db.commit()
        db.refresh(generated_image)
        
    #     return {
    #         'message': "Image generated successfully",
    #         'data': generated_image
    #     }
    # except Exception as e:
    #     response.status_code = 400
    #     return {
    #         'message': str(e)
    #     }
        return {
            'message': "Image generated successfully",
            'data': generated_image
        }
    except Exception as e:
        response.status_code = 400
        return {
            'message': str(e)
        }