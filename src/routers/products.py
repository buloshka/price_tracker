from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from src.storage.database import get_async_session
from src.storage.models import Products, Users
from src.storage.schemas import ProductCreate, ProductResponse
from src.routers.dependencies import get_current_user
from src.services.parser import PriceParser

router = APIRouter(prefix="/products", tags=["Products"])

@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить товар для отслеживания"
)
async def add_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user) # Защита эндпоинта!
):
    """Добавляет новую ссылку в список отслеживания текущего пользователя."""
    new_product = Products(
        user_id=current_user.id,
        url=str(product_data.url),
        target_price=product_data.target_price
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


@router.get(
    "/",
    response_model=List[ProductResponse],
    summary="Получить список всех моих товаров"
)
async def get_my_products(
    db: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user)
):
    """Возвращает только те товары, которые добавил авторизованный пользователь."""
    query = select(Products).where(Products.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/test-parse", summary="Тест парсера (вручную)")
async def test_parse(url: str):
    """Отправляет тестовый запрос парсеру и возвращает то, что он смог собрать."""
    title, price = await PriceParser.parse_product(url)
    return {
        "url": url,
        "parsed_title": title,
        "parsed_price": price
    }
