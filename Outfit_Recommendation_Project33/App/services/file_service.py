import os
from fastapi import UploadFile
import cloudinary
# إعداد Cloudinary
cloudinary.config(
   cloud_name=,
    api_key=,
    api_secret=
)

UPLOAD_FOLDER = r"D:\Project\Outfit_Recommendation_Project33\images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def save_user_images(person_image: UploadFile, cloth_image: UploadFile, category: str):
    try:
        print("save_user_images")
        print("Using Cloudinary cloud_name:", cloudinary.config().cloud_name)
        person_content = await person_image.read()
        cloth_content = await cloth_image.read()
        person_path = os.path.join(UPLOAD_FOLDER, "000706_0.jpg")
        cloth_path = os.path.join(UPLOAD_FOLDER, "000706_1.jpg")
        category_path = os.path.join(UPLOAD_FOLDER, "category.txt")

        with open(person_path, "wb") as f:
            f.write(person_content)
        with open(cloth_path, "wb") as f:
            f.write(cloth_content)
        with open(category_path, "w") as f:
            f.write(category)

        print("Saved locally at:", UPLOAD_FOLDER)
        person_result = cloudinary.uploader.upload(
            person_path,
            folder="User_Inputs",
            public_id="000706_0",
            overwrite=True,
            resource_type="image",
            timeout=60
        )
        print("Person image uploaded:", person_result.get("secure_url"))

        cloth_result = cloudinary.uploader.upload(
            cloth_path,
            folder="User_Inputs",
            public_id="000706_1",
            overwrite=True,
            resource_type="image",
            timeout=60
        )
        print("Cloth image uploaded:", cloth_result.get("secure_url"))

        category_result = cloudinary.uploader.upload(
            category_path,
            folder="User_Inputs",
            public_id="category",
            resource_type="raw",
            overwrite=True,
            timeout=60
        )
        print("Category file uploaded:", category_result.get("secure_url"))
        return {
            "person_url": person_result['secure_url'],
            "cloth_url": cloth_result['secure_url'],
            "category_url": category_result['secure_url'],
            "local_paths": [person_path, cloth_path, category_path]
        }

    except Exception as e:
        print("ERROR during upload:", e)
        return None