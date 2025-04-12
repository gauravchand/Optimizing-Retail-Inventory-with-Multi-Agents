from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class InventoryUpdate(BaseModel):
    store_id: str
    product_id: str
    quantity: int

class PriceUpdate(BaseModel):
    store_id: str
    product_id: str
    new_price: float

class InventoryResponse(BaseModel):
    product_id: str
    name: str
    category: str
    current_stock: int
    min_threshold: int
    price: float
    last_updated: Optional[str]

class ForecastItem(BaseModel):
    product_id: str
    product_name: str
    current_stock: int
    predicted_demand: int
    confidence: float

class AlertItem(BaseModel):
    product_id: str
    product_name: str
    current_stock: int
    min_threshold: int
    urgency: str
    suggested_order: int