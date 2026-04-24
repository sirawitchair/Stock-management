from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Integer)
    gender = Column(String)
    category = Column(String)
    rarity = Column(String)
    duration = Column(String)
    images = Column(String)
    is_active = Column(Boolean, default=True) # เพิ่มสถานะเปิด/ปิด หรือ มี/หมด