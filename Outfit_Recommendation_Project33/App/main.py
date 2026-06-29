from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from App.routes.auth import router as auth_router
from App.routes.predict import router as predict_router
from App.database import engine, Base
from App.models import EditItem, ClosetEditItem
from fastapi import Form
Base.metadata.create_all(bind=engine, checkfirst=True)
app = FastAPI()
origins = ["http://localhost:4200", "http://127.0.0.1:4200"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(auth_router, prefix="/auth")
app.include_router(predict_router, prefix="/predict")
##################################################################################


from fastapi import FastAPI, UploadFile, File, HTTPException, Path,Query, Body
from fastapi.staticfiles import StaticFiles
from outfit_recommender import OutfitRecommender
from py.recognition_module import single_classification
from typing import Optional
from App.cloudinary_config import *
import tempfile,shutil,os,uuid,requests
from App.EachUser import *
import cloudinary.api


# ==================== CLOSET (Cloudinary) ====================

@app.post("/closet/items")
async def add_closet_item(
    user_id: str = Query(...),
    file: UploadFile = File(...),
):
    try:
        suffix = "." + (file.filename or "img").split(".")[-1].lower()
    except Exception:
        suffix = ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        category, _info, meta = single_classification(tmp_path)
        result = cloudinary.uploader.upload(
            tmp_path,
            folder=f"closet/{user_id}",
            resource_type="image",
            context={
                "category": category,
                "subtype": meta.get("subtype") or "",
                "gender": meta.get("gender") or "",
                "season": meta.get("season") or "",
                "usage": meta.get("usage") or "",
                "color": meta.get("color") or "",
            },
        )
        return {
            "public_id": result["public_id"],
            "url": result["secure_url"],
            "category": category,
            "subtype": meta.get("subtype"),
            "f": meta.get("gender"),
            "season": meta.get("season"),
            "usage": meta.get("usage"),
            "color": meta.get("color"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Closet upload failed: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.get("/closet/items")
def list_closet_items(user_id: str = Query(...)):

    try:

        data = cloudinary.api.resources(
            type="upload",
            prefix=f"closet/{user_id}/",
            resource_type="image",
            max_results=100,
            context=True,
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Cloudinary list failed: {e}"
        )

    items = []

    for r in data.get("resources", []):

        print("RESOURCE =", r)

        custom = (
            (r.get("context") or {})
            .get("custom") or {}
        )

        items.append({

            "public_id": r.get("public_id"),

            "url": r.get("secure_url"),

            "category": custom.get("category"),

            "subtype": custom.get("subtype"),

            "gender": custom.get("gender"),

            "season": custom.get("season"),

            "usage": custom.get("usage"),

            "color": custom.get("color"),

        })

    return {"items": items}

@app.delete("/closet/items/{public_id:path}")
def delete_closet_item(public_id: str, user_id: str = Query(...)):
    if not public_id.startswith(f"closet/{user_id}/"):
        raise HTTPException(status_code=404, detail="Item not found")
    try:
        result = cloudinary.uploader.destroy(public_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary delete failed: {e}")
    if result.get("result") == "not found":
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "deleted", "public_id": public_id}

# ==================== UPLOADS (local + rec) ====================
@app.post("/uploads/items")
async def add_item(
    user_id: str = Query(...),
    source: str = Query(..., description="upload or closet"),
    file: Optional[UploadFile] = File(None),
    #public_id: Optional[str] = Query(None),
     public_id: Optional[str] = Form(None),
):
    uploads, rec = get_user_state(user_id)
    if source == "upload":
        if not file:
            raise HTTPException(status_code=400, detail="file required when source=upload")
        ext = (file.filename or "img").split(".")[-1]
        user_folder = os.path.join(UPLOAD_ROOT, user_id)
        os.makedirs(user_folder, exist_ok=True)
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(user_folder, filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        try:
            category, _info, meta = single_classification(file_path)
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Classification failed: {e}")
        item = dict(meta)
        item["category"] = category
        item["file_path"] = file_path
        item["image_url"] = f"/images/{user_id}/{filename}"
        item["cloudinary_public_id"] = None
        item["cloudinary_url"] = None
        item["source"] = "upload"
    elif source == "closet":
        if not public_id:
            raise HTTPException(status_code=400, detail="public_id required when source=closet")
        if not public_id.startswith(f"closet/{user_id}/"):
            raise HTTPException(status_code=404, detail="Closet item not found")
        try:
            r = cloudinary.api.resource(public_id)
        except Exception:
            raise HTTPException(status_code=404, detail="Closet item not found")
        image_url = r.get("secure_url")
        custom = (r.get("context") or {}).get("custom") or {}
        if not image_url:
            raise HTTPException(status_code=404, detail="Closet image url not found")
        # Copy selected closet photo into uploads folder
        try:
            resp = requests.get(image_url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch closet image: {e}")
        user_folder = os.path.join(UPLOAD_ROOT, user_id)
        os.makedirs(user_folder, exist_ok=True)
        filename = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(user_folder, filename)
        with open(file_path, "wb") as f:
            f.write(resp.content)
        item = {
            "subtype": custom.get("subtype"),
            "gender": custom.get("gender"),
            "season": custom.get("season"),
            "usage": custom.get("usage"),
            "color": custom.get("color"),
            "category": custom.get("category"),
            "file_path": file_path,
            "image_url": f"/images/{user_id}/{filename}",
            "cloudinary_public_id": public_id,
            "cloudinary_url": image_url,
            "source": "closet",
        }
    else:
        raise HTTPException(status_code=400, detail="source must be upload or closet")
    item["id"] = next_user_id(user_id)
    cat = item.get("category")
    if cat == "top":
        rec.top.append(item)
    elif cat == "bottom":
        rec.bottom.append(item)
    elif cat == "foot":
        rec.shoes.append(item)
    else:
        rec.top.append(item)
    uploads.append(item)
    return item


@app.get("/uploads/items")
def list_items(user_id: str = Query(...)):
    uploads, _ = get_user_state(user_id)
    return {
        "items": [item for item in uploads if item.get("source") == "upload"]
    }

from typing import Optional
from App.models import EditItem

@app.put("/uploads/items/{item_id}")
def update_upload_item(
    item_id: int,
    user_id: str = Query(...),
    updated: EditItem = Body(...),
):
    uploads, rec = get_user_state(user_id)
    item = find_upload(user_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    data = updated.model_dump(exclude_unset=True)
    if "type" in data and data["type"] is not None:
        item["subtype"] = data["type"]
    if "gender" in data and data["gender"] is not None:
        item["gender"] = data["gender"]
    if "color" in data and data["color"] is not None:
        item["color"] = data["color"]
    if "season" in data and data["season"] is not None:
        item["season"] = data["season"]
    if "usage" in data and data["usage"] is not None:
        item["usage"] = data["usage"]

    for lst in (rec.top, rec.bottom, rec.shoes):
        for i, v in enumerate(lst):
            if v.get("id") == item_id:
                lst[i] = item
                break
    return item

@app.put("/closet/items/{public_id:path}")
def update_closet_item(
    public_id: str,
    updated: ClosetEditItem = Body(...)
):
    try:

        data = updated.model_dump(exclude_unset=True)
        resource = cloudinary.api.resource(
             public_id,
             context=True
            )

        existing = (
             (resource.get("context") or {})
             .get("custom") or {}
             )
        context = {
    "category": existing.get("category"),
    "subtype": data.get("type", existing.get("subtype")),
    "gender": data.get("gender", existing.get("gender")),
    "season": data.get("season", existing.get("season")),
    "usage": data.get("usage", existing.get("usage")),
    "color": data.get("color", existing.get("color")),
            }
        context_str = "|".join(
        f"{k}={v}"
        for k, v in context.items()
        if v is not None
       )

        cloudinary.api.update(
         public_id,
          context=context_str
        )
        return {
            "message": "Closet item updated"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.delete("/uploads/items/{item_id}")
def delete_item(item_id: int, user_id: str = Query(...)):
    uploads, rec = get_user_state(user_id)
    for i, item in enumerate(uploads):
        if item.get("id") == item_id:
            fp = item.get("file_path")
            if fp and os.path.exists(fp):
                os.remove(fp)
            remove_from_rec(rec, item_id)
            uploads.pop(i)
            return {"message": "Item deleted successfully", "id": item_id}
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/uploads/session")
def clear_upload_session(user_id: str = Query(...)):
    uploads_by_user.pop(user_id, None)
    rec_by_user.pop(user_id, None)
    id_by_user.pop(user_id, None)

    return {"message": "session cleared"}


@app.get("/generate/outfit")
def generate_outfit(
    user_id: str = Query(...),
    usage: str | None = Query(None),
    use_closet: bool = Query(False)
):
    uploads, rec = get_user_state(user_id)

    try:

        # Load all closet items if requested
        if use_closet:

            uploads.clear()
            rec.top.clear()
            rec.bottom.clear()
            rec.shoes.clear()

            data = cloudinary.api.resources(
                type="upload",
                prefix=f"closet/{user_id}/",
                resource_type="image",
                max_results=100,
                context=True,
            )

            for r in data.get("resources", []):

                custom = (
                    (r.get("context") or {})
                    .get("custom") or {}
                )
                print("================================")
                print("PUBLIC ID =", r.get("public_id"))
                print("CATEGORY =", custom.get("category"))
                print("SUBTYPE =", custom.get("subtype"))
                print("GENDER =", custom.get("gender"))
                print("USAGE =", custom.get("usage"))
                print("================================")

                item = {
                    "id": next_user_id(user_id),
                    "subtype": custom.get("subtype"),
                    "gender": custom.get("gender"),
                    "season": custom.get("season"),
                    "usage": custom.get("usage"),
                    "color": custom.get("color"),
                    "color_group": int(custom.get("color_group", 0)),
                    "category": custom.get("category"),
                    "image_url": r.get("secure_url"),
                    "cloudinary_public_id": r.get("public_id"),
                    "source": "closet",
                }

                uploads.append(item)

                if item["category"] == "top":
                    rec.top.append(item)

                elif item["category"] == "bottom":
                    rec.bottom.append(item)

                elif item["category"] == "foot":
                    rec.shoes.append(item)
        print("TOP COUNT =", len(rec.top))
        print("BOTTOM COUNT =", len(rec.bottom))
        print("SHOE COUNT =", len(rec.shoes))

        if not use_closet:
            rebuild_rec_from_uploads(rec, uploads, source="upload")

        outfit = rec.generate_outfit(
            usage=usage
        )

        if outfit is None:
            raise HTTPException(
                status_code=400,
                detail="Could not generate outfit"
            )

        if use_closet:
            clear_upload_state(uploads, rec)

        return outfit

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )




#####################
from App.cloudinary_config import is_cloudinary_configured
from App.database import SessionLocal
from App.database import Base, engine
from fastapi import APIRouter, Depends, HTTPException
from App.models import UserPhoto
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import Form      
@app.post("/upload-profile-photo")
async def upload_profile_photo(user_id: str = Form(...) , file: UploadFile = File(...), db=Depends(get_db)):
    if not is_cloudinary_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "Cloudinary is not configured. Set CLOUDINARY_URL, or "
                "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET "
                "(e.g. in a .env file next to the app)."
            ),
        )
    await file.seek(0)
    result = None
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder=f"profile/{user_id}",
        )

        existing = db.query(UserPhoto).filter(UserPhoto.user_id == user_id).first()

        if existing:
            old_public_id = existing.public_id
            existing.public_id = result["public_id"]
            existing.image_url = result["secure_url"]
        else:
            db.add(
                UserPhoto(
                    user_id=user_id,
                    public_id=result["public_id"],
                    image_url=result["secure_url"],
                )
            )

        db.commit()

        if existing and old_public_id:
            try:
                cloudinary.uploader.destroy(old_public_id)
            except Exception:
                pass
    except Exception:
        db.rollback()
        if result and result.get("public_id"):
            try:
                cloudinary.uploader.destroy(result["public_id"])
            except Exception:
                pass
        raise

    return {"url": result["secure_url"]}


@app.get("/get-profile-photo")
def get_profile_photo(user_id: str, db=Depends(get_db)):
    user_photo = db.query(UserPhoto).filter(UserPhoto.user_id == user_id).first()

    if not user_photo:
        raise HTTPException(status_code=404, detail="No photo found")

    return {
        "user_id": user_id,
        "image_url": user_photo.image_url
    }


@app.delete("/delete-profile-photo")
async def delete_profile_photo(user_id: str, db=Depends(get_db)):
    if not is_cloudinary_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "Cloudinary is not configured. Set CLOUDINARY_URL, or "
                "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET "
                "(e.g. in a .env file next to the app)."
            ),
        )

    user_photo = db.query(UserPhoto).filter(UserPhoto.user_id == user_id).first()

    if not user_photo:
        raise HTTPException(status_code=404, detail="No photo found")

    # delete from Cloudinary
    cloudinary.uploader.destroy(user_photo.public_id)

    # delete from DB
    db.delete(user_photo)
    db.commit()

    return {"message": "Deleted successfully"}

from App.EachUser import UPLOAD_ROOT
app.mount("/images", StaticFiles(directory=UPLOAD_ROOT), name="images")
