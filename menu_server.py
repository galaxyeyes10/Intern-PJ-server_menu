from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from model import ReviewTable, UserTable, StoreTable, MenuTable
from db import session
from fastapi.middleware.cors import CORSMiddleware
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


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

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
if __name__ == "__menu__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)