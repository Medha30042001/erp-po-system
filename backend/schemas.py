from pydantic import BaseModel
from typing import List

class VendorCreate(BaseModel):
    name: str
    contact: str
    rating: float

class ProductCreate(BaseModel):
    name: str
    sku: str
    unit_price: float
    stock_level: int

class PurchaseOrderItemCreate(BaseModel):
    product_id: str
    quantity: int

class PurchaseOrderCreate(BaseModel):
    vendor_id: str
    items: List[PurchaseOrderItemCreate]