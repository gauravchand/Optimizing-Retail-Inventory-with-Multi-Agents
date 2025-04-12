import asyncio
from app.models.database import async_session, Product, StoreInventory, SalesHistory
from app.config.constants import CURRENT_USER, get_datetime_obj
import random

async def initialize_database():
    async with async_session() as session:
        try:
            # Create sample products
            products = [
                Product(
                    id="P001",
                    name="T-Shirt",
                    category="Clothing",
                    price=19.99,
                    supplier_id="S001"
                ),
                Product(
                    id="P002",
                    name="Jeans",
                    category="Clothing",
                    price=49.99,
                    supplier_id="S001"
                ),
                Product(
                    id="P003",
                    name="Sneakers",
                    category="Footwear",
                    price=79.99,
                    supplier_id="S002"
                )
            ]
            
            # Add products
            for product in products:
                session.add(product)
            await session.commit()
            print("Products added successfully!")

            # Initialize inventory for each store
            stores = ["store1", "store2", "store3"]
            for store in stores:
                for product in products:
                    inventory = StoreInventory(
                        store_id=store,
                        product_id=product.id,
                        stock_level=random.randint(5, 100),
                        min_threshold=20,
                        last_updated_by=CURRENT_USER,
                        last_updated_at=get_datetime_obj()
                    )
                    session.add(inventory)
            await session.commit()
            print("Store inventory initialized successfully!")

            # Add sample sales history
            for _ in range(50):
                sale = SalesHistory(
                    store_id=random.choice(stores),
                    product_id=random.choice([p.id for p in products]),
                    quantity=random.randint(1, 10),
                    sale_date=get_datetime_obj(),
                    recorded_by=CURRENT_USER
                )
                session.add(sale)
            await session.commit()
            print("Sales history added successfully!")

            print("Database initialization complete!")

        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(initialize_database())