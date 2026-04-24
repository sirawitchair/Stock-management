import os
from sqlalchemy.orm import Session
from models import Item

UPLOAD_DIR = "static/uploads"

def get_all_items(db: Session):
    """ดึงข้อมูลสินค้าทั้งหมดจากฐานข้อมูล"""
    return db.query(Item).all()

def create_new_item(db: Session, item_data: dict):
    """บันทึกสินค้าใหม่ลงในฐานข้อมูล"""
    new_item = Item(**item_data)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

def delete_item_by_id(db: Session, item_id: int):
    """ลบสินค้าและไฟล์รูปภาพที่เกี่ยวข้อง"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        # ลบไฟล์รูปภาพออกจากโฟลเดอร์ static
        if item.images:
            for img in item.images.split(","):
                file_path = os.path.join(UPLOAD_DIR, img)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting file: {e}")
        db.delete(item)
        db.commit()
        return True
    return False