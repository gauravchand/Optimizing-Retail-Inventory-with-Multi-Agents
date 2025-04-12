import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.database import Base, Product, StoreInventory, SalesHistory
from app.config.constants import DATABASE_URL, CURRENT_USER, get_datetime_obj
import random


async def setup_database():
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    try:
        # First, create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        print("Tables created successfully!")

        # Create sample products
        products_data = [
            {
                "id": "P001",
                "name": "T-Shirt",
                "category": "Clothing",
                "price": 19.99,
                "supplier_id": "S001",
                "created_by": CURRENT_USER,
                "created_at": get_datetime_obj(),
                "last_updated": get_datetime_obj()
            },
            {
                "id": "P002",
                "name": "Jeans",
                "category": "Clothing",
                "price": 49.99,
                "supplier_id": "S001",
                "created_by": CURRENT_USER,
                "created_at": get_datetime_obj(),
                "last_updated": get_datetime_obj()
            },
            {
                "id": "P003",
                "name": "Sneakers",
                "category": "Footwear",
                "price": 79.99,
                "supplier_id": "S002",
                "created_by": CURRENT_USER,
                "created_at": get_datetime_obj(),
                "last_updated": get_datetime_obj()
            }
        ]

        async with async_session() as session:
            # Add products
            session.add_all([Product(**data) for data in products_data])
            await session.commit()
            print("Products added successfully!")

            # Initialize inventory for each store
            stores = ["store1", "store2", "store3"]
            inventory_items = []

            for store in stores:
                for product_data in products_data:
                    inventory_items.append(
                        StoreInventory(
                            store_id=store,
                            product_id=product_data["id"],
                            stock_level=random.randint(5, 100),
                            min_threshold=20,
                            last_updated_by=CURRENT_USER,
                            last_updated_at=get_datetime_obj()
                        )
                    )

            session.add_all(inventory_items)
            await session.commit()
            print("Inventory initialized successfully!")

            # Add sample sales history
            sales_history = []
            for _ in range(50):
                sales_history.append(
                    SalesHistory(
                        store_id=random.choice(stores),
                        product_id=random.choice([p["id"] for p in products_data]),
                        quantity=random.randint(1, 10),
                        sale_date=get_datetime_obj(),
                        recorded_by=CURRENT_USER
                    )
                )

            session.add_all(sales_history)
            await session.commit()
            print("Sales history added successfully!")

        print(f"Database initialized successfully by {CURRENT_USER}!")

    except Exception as e:
        print(f"Error during database initialization: {str(e)}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(setup_database())