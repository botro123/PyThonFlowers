import os
from fastapi import (
    APIRouter, Depends, HTTPException, status,
    UploadFile, File, Form
)
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import logging
import pandas as pd
import base64
# Import các module cần thiết
import controller.flowers as crud
import schemas.flowers as schemas
from config.db import FLOWER_TYPE_DIRS, get_db
from utils.paginator import paginate_dataframe

# Cấu hình logger
logger = logging.getLogger(__name__)

# Khởi tạo router
router = APIRouter(prefix="/flowers", tags=["Flowers"])

# --- Endpoint CREATE ---
@router.post("/", response_model=schemas.Flower, status_code=status.HTTP_201_CREATED)
def create_flower(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: Decimal = Form(...),
    stock_quantity: int = Form(...),
    flower_type: str = Form(...), 
    image_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    if flower_type not in FLOWER_TYPE_DIRS:
        raise HTTPException(status_code=400, detail=f"Invalid flower type: {flower_type}")

    flower_data = schemas.FlowerCreate(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        flower_type=flower_type
    )
    return crud.create_flower(db=db, flower_data=flower_data, image_file=image_file)

@router.get("/", summary="Get a paginated list of all flowers")
def handle_read_flowers(page: int = 1, per_page: int = 10, db: Session = Depends(get_db)):
    """
    Retrieves a paginated list of flowers with images encoded in Base64.
    """
    flowers = crud.get_flowers(db)

    flowers_data = []
    for flower in flowers:
        flower_dict = flower.__dict__.copy()

        # Đọc file ảnh và mã hóa Base64
        image_path = os.path.join(FLOWER_TYPE_DIRS[flower.flower_type], os.path.basename(flower.image_url)) if flower.image_url else None
        if image_path and os.path.isfile(image_path):
            with open(image_path, "rb") as image_file:
                flower_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
        else:
            flower_dict["image_base64"] = None

        flowers_data.append(flower_dict)

    df = pd.DataFrame(flowers_data)

    # Phân trang dữ liệu
    paginated_result = paginate_dataframe(df, page=page, per_page=per_page)

    return {
        "data": paginated_result["data"],
        "total_records": paginated_result["total_record"],
        "page": paginated_result["page"],
        "per_page": paginated_result["per_page"]
    }
# --- Endpoint GET ONE ---
@router.get("/{flower_id}", response_model=schemas.Flower, summary="Get a specific flower by ID")
def handle_read_flower(flower_id: int, db: Session = Depends(get_db)):
    """
    Retrieves details for a specific flower with its image encoded in Base64.
    """
    db_flower = crud.get_flower(db, flower_id=flower_id)
    if db_flower is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flower not found")

    flower_dict = db_flower.__dict__.copy()

    # Đọc file ảnh và mã hóa Base64
    image_path = os.path.join(FLOWER_TYPE_DIRS[db_flower.flower_type], os.path.basename(db_flower.image_url)) if db_flower.image_url else None
    if image_path and os.path.isfile(image_path):
        with open(image_path, "rb") as image_file:
            flower_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
    else:
        flower_dict["image_base64"] = None

    return flower_dict

@router.put(
    "/{flower_id}",
    response_model=schemas.Flower,
    summary="Update a flower with optional new image"
)
def handle_update_flower(
    flower_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[Decimal] = Form(None),
    stock_quantity: Optional[int] = Form(None),
    flower_type: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None, description="New flower image file (optional)"),
    db: Session = Depends(get_db)
):
    """
    Updates an existing flower. Provide fields to update as form data.
    Optionally upload a new image file to replace the existing one.
    """
    update_data_dict = {}
    if name is not None: update_data_dict['name'] = name
    if description is not None: update_data_dict['description'] = description
    if price is not None: update_data_dict['price'] = price
    if stock_quantity is not None: update_data_dict['stock_quantity'] = stock_quantity
    if flower_type is not None: update_data_dict['flower_type'] = flower_type

    if not update_data_dict and not image_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data or image provided."
        )

    flower_update_schema = schemas.FlowerUpdate(**update_data_dict)

    try:
        updated_flower = crud.update_flower(
            db=db,
            flower_id=flower_id,
            flower_data=flower_update_schema,
            image_file=image_file
        )
        if updated_flower is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flower not found")
        return updated_flower
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating flower {flower_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error updating flower.")

@router.delete(
    "/{flower_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a flower and its associated image"
)
def handle_delete_flower(flower_id: int, db: Session = Depends(get_db)):
    """
    Deletes a flower record and its corresponding image file from the server.
    """
    try:
        deleted_flower_id = crud.delete_flower(db=db, flower_id=flower_id)
        if deleted_flower_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flower not found")
        return {"message": "Flower deleted successfully", "deleted_id": deleted_flower_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting flower {flower_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error deleting flower.")

