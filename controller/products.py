from sqlalchemy.orm import Session
from models.models import Product as ProductM
from schemas.products import ProductCreate

def create_product(db: Session, product: ProductCreate):
    db_product = ProductM(
        name = product.name,
        description = product.description,
        price = product.price,
        stock_quantity = product.stock_quantity

    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int):
    return db.query(ProductM).filter(ProductM.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(ProductM).offset(skip).limit(limit).all()