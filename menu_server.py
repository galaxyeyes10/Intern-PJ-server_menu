from fastapi import FastAPI, Depends, Request, Body
from sqlalchemy.orm import Session
from model import ReviewTable, UserTable, StoreTable, MenuTable, OrderTable
from db import session
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
import uvicorn

menu = FastAPI()

menu.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

menu.add_middleware(SessionMiddleware, secret_key="your-secret-key")

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

#로그인 상태 확인, 로그인 중인 유저 아이디 반환
@menu.get("/check_login/")
async def check_login(request: Request):
    # 세션에서 사용자 정보 확인
    if "user_id" not in request.session:
        return False
    
    return {"user_id": f"{request.session['user_id']}"}

#가게 아이디로 가게의 모든 메뉴 아이디들을 반환
@menu.get("/menu_ids/{store_id}")
async def get_menu_ids(store_id: int, db: Session = Depends(get_db)):
    menu_ids = db.query(MenuTable.menu_id).filter(MenuTable.store_id == store_id).all()
    
    return {"menu_ids": [menu_id[0] for menu_id in menu_ids]}

#메뉴 이름, 메뉴 설명, 메뉴 사진 딕셔너리 반환(메인)
@menu.get("/main_menu/{menu_id}")
async def read_main_menu(menu_id: str, db: Session = Depends(get_db)):
    menus = db.query(MenuTable).filter(MenuTable.menu_id == menu_id).all()
    
    menu_info = [
        {
            "menu_name": menu.menu_name,
            "description": menu.description,
            "menu_img": menu.menu_img,
        }
        for menu in menus
    ]

    return menu_info

#메뉴 이름, 메뉴 가격 반환(사이드)
@menu.get("/side_menu/{menu_id}")
async def read_side_menu(menu_id: str, db: Session = Depends(get_db)):
    menus = db.query(MenuTable).filter(MenuTable.menu_id == menu_id).all()
    
    menu_info = [
        {
            "menu_name": menu.menu_name,
            "price": menu.price,
        }
        for menu in menus
    ]

    return menu_info

#확인 버튼 처리
@menu.post("/order/increase/")
async def increase_order_quantity(user_id: str = Body(...), menu_id: int = Body(...), store_id: int = Body(...), db: Session = Depends(get_db)):
    order = db.query(OrderTable).filter(OrderTable.user_id == user_id).first()
    
    if order:
        order.quantity += 1
        db.commit()
        db.refresh(order)
        return {"order_id": order.order_id}

    else:
        new_order = OrderTable(
            user_id=user_id,
            store_id = store_id,
            menu_id=menu_id,
            quantity=1,
            is_completed=False,
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return {"order_id": new_order.order_id}

if __name__ == "__menu__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)