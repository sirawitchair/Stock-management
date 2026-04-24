import os
import uuid
from typing import List, Optional
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import crud
from models import Item

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "static/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    items = crud.get_all_items(db)
    for item in items:
        item.image_list = item.images.split(",") if item.images else []
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"items": items}
    )

@app.get("/add", response_class=HTMLResponse)
async def add_item_page(request: Request):
    return templates.TemplateResponse(request=request, name="add.html")

@app.post("/add")
async def create_item_route(
    name: str = Form(...),
    price: int = Form(...),
    gender: str = Form(...),
    category: str = Form(...),
    rarity: str = Form(...),
    duration: str = Form(...),
    is_active: bool = Form(True), # รับค่าสถานะ
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    valid_files = [f for f in files if f.filename != ""]
    if len(valid_files) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 images allowed")

    saved_filenames = []
    for file in valid_files:
        file_ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        with open(os.path.join(UPLOAD_DIR, unique_name), "wb") as buffer:
            buffer.write(await file.read())
        saved_filenames.append(unique_name)

    item_data = {
        "name": name, "price": price, "gender": gender, "category": category,
        "rarity": rarity, "duration": duration, "images": ",".join(saved_filenames),
        "is_active": is_active
    }
    crud.create_new_item(db, item_data)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{item_id}")
async def delete_item_route(item_id: int, db: Session = Depends(get_db)):
    crud.delete_item_by_id(db, item_id)
    return RedirectResponse(url="/", status_code=303)

# เพิ่มส่วนของ Route สำหรับการแก้ไขข้อมูล (Edit)
@app.get("/edit/{item_id}", response_class=HTMLResponse)
async def edit_item_page(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse(
        request=request, 
        name="edit.html", 
        context={"item": item}
    )

@app.post("/edit/{item_id}")
async def update_item(
    item_id: int,
    name: str = Form(...),
    price: int = Form(...),
    gender: str = Form(...),
    category: str = Form(...),
    rarity: str = Form(...),
    duration: str = Form(...),
    is_active: bool = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # จัดการรูปภาพใหม่ (ถ้ามีการอัปโหลดใหม่)
    valid_files = [f for f in files if f.filename != ""] if files else []
    if valid_files:
        # ลบรูปเก่าออกก่อน
        if item.images:
            for img in item.images.split(","):
                try: os.remove(os.path.join(UPLOAD_DIR, img))
                except: pass
        
        saved_filenames = []
        for file in valid_files[:3]:
            file_ext = os.path.splitext(file.filename)[1]
            unique_name = f"{uuid.uuid4()}{file_ext}"
            with open(os.path.join(UPLOAD_DIR, unique_name), "wb") as buffer:
                buffer.write(await file.read())
            saved_filenames.append(unique_name)
        item.images = ",".join(saved_filenames)

    # อัปเดตข้อมูลอื่นๆ
    item.name = name
    item.price = price
    item.gender = gender
    item.category = category
    item.rarity = rarity
    item.duration = duration
    item.is_active = is_active
    
    db.commit()
    return RedirectResponse(url="/", status_code=303)