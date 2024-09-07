import cloudinary.uploader
from fastapi import HTTPException
from Settings import setting
import io
from fastapi import Depends,status
conf = cloudinary.config(
    cloud_name=setting.CLOUD_NAME,
    api_key=setting.API_KEY,
    api_secret=setting.API_SECRET,
    secure=True,
)
async def upload_image(image_stream: io.BytesIO) -> dict:
    try:
        upload_result = cloudinary.uploader.upload(image_stream)
        file_url = upload_result["secure_url"]
        file_public_id = upload_result["public_id"]
        return {"url": file_url, "public_id": file_public_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image upload failed: {str(e)}",
        )

def delete_image(public_id):
    cloudinary.uploader.destroy(public_id)
