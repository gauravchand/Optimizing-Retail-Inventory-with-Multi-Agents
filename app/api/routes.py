from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import get_session, Product, StoreInventory, SalesHistory
from app.models.schemas import InventoryUpdate, PriceUpdate, InventoryResponse, ForecastItem, AlertItem
from app.config.constants import CURRENT_USER, CURRENT_DATETIME, get_datetime_obj
from datetime import datetime, timedelta
from typing import List
import numpy as np

router = APIRouter()


@router.get("/inventory/{store_id}")
async def get_store_inventory(store_id: str, session: AsyncSession = Depends(get_session)):
    try:
        query = select(StoreInventory, Product).join(
            Product, StoreInventory.product_id == Product.id
        ).where(StoreInventory.store_id == store_id)

        result = await session.execute(query)
        items = result.all()

        if not items:
            raise HTTPException(status_code=404, detail=f"No inventory found for store {store_id}")

        inventory_data = []
        for item in items:
            inventory_data.append(InventoryResponse(
                product_id=item.Product.id,
                name=item.Product.name,
                category=item.Product.category,
                current_stock=item.StoreInventory.stock_level,
                min_threshold=item.StoreInventory.min_threshold,
                price=item.Product.price,
                last_updated=item.StoreInventory.last_updated_at.isoformat() if item.StoreInventory.last_updated_at else None
            ))

        return {
            "store_id": store_id,
            "inventory": [item.dict() for item in inventory_data],
            "checked_by": CURRENT_USER,
            "checked_at": CURRENT_DATETIME
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inventory/update")
async def update_inventory(update_data: InventoryUpdate, session: AsyncSession = Depends(get_session)):
    try:
        query = select(StoreInventory).where(
            StoreInventory.store_id == update_data.store_id,
            StoreInventory.product_id == update_data.product_id
        )
        result = await session.execute(query)
        inventory_item = result.scalar_one_or_none()

        if not inventory_item:
            raise HTTPException(status_code=404, detail="Product not found in store inventory")

        inventory_item.stock_level += update_data.quantity
        inventory_item.last_updated_by = CURRENT_USER
        inventory_item.last_updated_at = get_datetime_obj()

        await session.commit()

        return {
            "message": "Inventory updated successfully",
            "store_id": update_data.store_id,
            "product_id": update_data.product_id,
            "new_stock_level": inventory_item.stock_level,
            "updated_by": CURRENT_USER,
            "updated_at": CURRENT_DATETIME
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/{store_id}")
async def get_forecast(store_id: str, session: AsyncSession = Depends(get_session)):
    try:
        query = select(StoreInventory, Product).join(
            Product, StoreInventory.product_id == Product.id
        ).where(StoreInventory.store_id == store_id)

        result = await session.execute(query)
        items = result.all()

        if not items:
            raise HTTPException(status_code=404, detail=f"No inventory found for store {store_id}")

        forecast_data = []
        for item in items:
            forecast_data.append(ForecastItem(
                product_id=item.Product.id,
                product_name=item.Product.name,
                current_stock=item.StoreInventory.stock_level,
                predicted_demand=int(item.StoreInventory.stock_level * (1 + np.random.uniform(-0.2, 0.4))),
                confidence=round(0.85 + np.random.random() * 0.1, 2)
            ))

        return {
            "store_id": store_id,
            "forecast": [item.dict() for item in forecast_data],
            "generated_by": CURRENT_USER,
            "generated_at": CURRENT_DATETIME
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory-alerts/{store_id}")
async def get_inventory_alerts(store_id: str, session: AsyncSession = Depends(get_session)):
    try:
        query = select(StoreInventory, Product).join(
            Product, StoreInventory.product_id == Product.id
        ).where(
            StoreInventory.store_id == store_id,
            StoreInventory.stock_level < StoreInventory.min_threshold
        )

        result = await session.execute(query)
        items = result.all()

        alerts = []
        for item in items:
            alerts.append(AlertItem(
                product_id=item.Product.id,
                product_name=item.Product.name,
                current_stock=item.StoreInventory.stock_level,
                min_threshold=item.StoreInventory.min_threshold,
                urgency="HIGH" if item.StoreInventory.stock_level < (
                            item.StoreInventory.min_threshold / 2) else "MEDIUM",
                suggested_order=item.StoreInventory.min_threshold - item.StoreInventory.stock_level + 10
            ))

        return {
            "store_id": store_id,
            "alerts": [alert.dict() for alert in alerts],
            "generated_by": CURRENT_USER,
            "generated_at": CURRENT_DATETIME
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price-optimization/{store_id}")
async def optimize_prices(store_id: str, session: AsyncSession = Depends(get_session)):
    try:
        query = select(StoreInventory, Product).join(
            Product, StoreInventory.product_id == Product.id
        ).where(StoreInventory.store_id == store_id)

        result = await session.execute(query)
        items = result.all()

        if not items:
            raise HTTPException(status_code=404, detail=f"No inventory found for store {store_id}")

        optimized_prices = []
        for item in items:
            current_price = item.Product.price
            stock_level = item.StoreInventory.stock_level

            # Price optimization logic
            if stock_level > 100:
                suggested_price = current_price * 0.9  # 10% discount
            elif stock_level < 20:
                suggested_price = current_price * 1.1  # 10% markup
            else:
                suggested_price = current_price * (1 + np.random.uniform(-0.05, 0.05))

            potential_profit = (suggested_price - current_price) * stock_level

            optimized_prices.append({
                "product_id": item.Product.id,
                "product_name": item.Product.name,
                "current_price": current_price,
                "suggested_price": round(suggested_price, 2),
                "stock_level": stock_level,
                "potential_profit_increase": round(potential_profit, 2),
                "expected_demand_change": f"{-10 if suggested_price > current_price else 10}%"
            })

        return {
            "store_id": store_id,
            "optimized_prices": optimized_prices,
            "generated_by": CURRENT_USER,
            "generated_at": CURRENT_DATETIME
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-price")
async def update_price(update_data: PriceUpdate, session: AsyncSession = Depends(get_session)):
    try:
        query = select(Product).where(Product.id == update_data.product_id)
        result = await session.execute(query)
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product.price = update_data.new_price
        product.last_updated = get_datetime_obj()
        await session.commit()

        return {
            "message": "Price updated successfully",
            "store_id": update_data.store_id,
            "product_id": update_data.product_id,
            "new_price": update_data.new_price,
            "updated_by": CURRENT_USER,
            "updated_at": CURRENT_DATETIME
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))