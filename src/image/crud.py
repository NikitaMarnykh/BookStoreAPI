from datetime import datetime
from shutil import copyfileobj
from os import remove
from fastapi import UploadFile, File, HTTPException
from sqlalchemy import insert
from src.image.models_image import Image
from src.image.path_to_media import path


# Добавление изображения
async def add_image(book_id: str, image_file: UploadFile = File(...)):
    image_name = image_file.filename.replace(" ", "_")
    image_point = image_name.find(".")
    image_name = image_name[0:image_point] + str(int(book_id)) + image_name[image_point:len(image_name)]
    file_type = image_file.content_type
    if "image" in file_type:
        with open(f"{path}/{image_name}", "wb") as image:
            copyfileobj(image_file.file, image)
        image_dict = {"name": image_name, "size": image_file.size, "file_type": file_type, "book_id": book_id}
        statement = insert(Image).values(**image_dict)
        return image_dict
    else:
        raise HTTPException(status_code=404, detail="It isn't image")


# Удаление изображения
async def delete_image(image_name: str):
    remove(f"{path}/{image_name}")



