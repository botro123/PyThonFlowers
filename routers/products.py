from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.db import get_db
from controller.products import create_product, get_product, get_products
from schemas.products import Product as ProductS, ProductCreate


product = APIRouter(
    prefix = "/product"
    
)
@product.get('' , response_model=list[ProductS])
async def api_get_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = get_products(db,skip = skip,limit = limit)
    return products

@product.get("/{id}", response_model=ProductS)
async def read_product(id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id=id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@product.post("/", response_model=ProductS)
async def create_product_endpoint(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = create_product(db, product=product)
    return db_product