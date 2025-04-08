from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int

class ProductCreate(ProductBase):
    pass 

class Product(ProductBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True