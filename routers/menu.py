from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from deps import require_admin
from models import Menu
from schemas import MenuCreate, MenuOut, MenuUpdate

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("", response_model=list[MenuOut])
def list_menu(category: str | None = None, search: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Menu)
    if category:
        query = query.filter(Menu.category.ilike(category))
    if search:
        query = query.filter(Menu.name.ilike(f"%{search}%"))
    return query.order_by(Menu.name.asc()).all()


@router.post("", response_model=MenuOut)
def create_menu_item(payload: MenuCreate, _: dict = Depends(require_admin), db: Session = Depends(get_db)):
    item = Menu(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=MenuOut)
def update_menu_item(item_id: int, payload: MenuUpdate, _: dict = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.query(Menu).filter(Menu.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_menu_item(item_id: int, _: dict = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.query(Menu).filter(Menu.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()
    return {"message": "Menu item deleted"}
