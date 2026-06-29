from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from App.services.auth_service import verify_token
from App.services.file_service import save_user_images
from App.services.kaggle_service import run_kaggle_flow
router = APIRouter()
import os
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
def get_current_user(token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks

@router.post("/post")
async def predict(
    background_tasks: BackgroundTasks,
    person_image: UploadFile = File(...),
    cloth_image: UploadFile = File(...),
    category: str = Form(...),
    
):
    urls = await save_user_images(person_image, cloth_image, category)
    
    if not urls:
        raise HTTPException(status_code=500, detail="Failed to upload images")
    background_tasks.add_task(run_kaggle_flow, "User_Inputs", background_tasks)
    return {
        "status": "processing",
        "message": "We started the Kaggle notebook. You can check the result in a few minutes."
    }
@router.get("/get")
def get_latest_image():
    folder = "outputs"
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        raise HTTPException(status_code=404, detail="No images found")
    latest_file = max(files, key=lambda f:os.path.getmtime(os.path.join(folder, f))) 
    return FileResponse(os.path.join(folder, latest_file))