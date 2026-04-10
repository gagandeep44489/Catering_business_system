from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database import get_db
from deps import get_current_user, require_admin
from models import Menu, Order, OrderItem, User
from schemas import OrderCreate, OrderItemOut, OrderOut, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


def serialize_order(order: Order) -> OrderOut:
    items = [
        OrderItemOut(
            id=i.id,
            menu_id=i.menu_id,
            quantity=i.quantity,
            menu_name=i.menu.name,
            menu_price=i.menu.price,
            line_total=i.menu.price * i.quantity,
        )
        for i in order.items
    ]
    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        customer_name=order.user.name,
        total_price=order.total_price,
        status=order.status,
        event_type=order.event_type,
        guests=order.guests,
        event_date=order.event_date,
        created_at=order.created_at,
        items=items,
    )


@router.post("", response_model=OrderOut)
def create_order(payload: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="At least one item is required")

    menu_ids = [item.menu_id for item in payload.items]
    menu_map = {m.id: m for m in db.query(Menu).filter(Menu.id.in_(menu_ids)).all()}
    if len(menu_map) != len(set(menu_ids)):
        raise HTTPException(status_code=404, detail="One or more menu items not found")

    total = sum(menu_map[item.menu_id].price * item.quantity for item in payload.items)

    order = Order(
        user_id=current_user.id,
        total_price=total,
        status="Pending",
        event_type=payload.event_type,
        guests=payload.guests,
        event_date=payload.event_date,
    )
    db.add(order)
    db.flush()

    for item in payload.items:
        db.add(OrderItem(order_id=order.id, menu_id=item.menu_id, quantity=item.quantity))

    db.commit()
    order = db.query(Order).options(joinedload(Order.items).joinedload(OrderItem.menu), joinedload(Order.user)).get(order.id)
    return serialize_order(order)


@router.get("", response_model=list[OrderOut])
def list_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Order).options(joinedload(Order.items).joinedload(OrderItem.menu), joinedload(Order.user))
    if current_user.role != "admin":
        query = query.filter(Order.user_id == current_user.id)
    orders = query.order_by(Order.created_at.desc()).all()
    return [serialize_order(o) for o in orders]


@router.put("/{order_id}", response_model=OrderOut)
def update_order_status(order_id: int, payload: OrderStatusUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    db.commit()
    order = db.query(Order).options(joinedload(Order.items).joinedload(OrderItem.menu), joinedload(Order.user)).get(order.id)
    return serialize_order(order)


@router.get("/{order_id}/invoice")
def get_invoice(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).options(joinedload(Order.items).joinedload(OrderItem.menu), joinedload(Order.user)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "admin" and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return {
        "invoice_no": f"INV-{order.id:05d}",
        "customer": order.user.name,
        "event_type": order.event_type,
        "event_date": order.event_date,
        "status": order.status,
        "items": [
            {
                "name": i.menu.name,
                "price": i.menu.price,
                "quantity": i.quantity,
                "line_total": i.menu.price * i.quantity,
            }
            for i in order.items
        ],
        "total": order.total_price,
    }
