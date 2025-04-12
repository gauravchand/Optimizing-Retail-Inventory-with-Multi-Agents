from langchain.llms import Ollama
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import StoreInventory, Product, SalesHistory
from app.config.settings import get_settings
import json

settings = get_settings()

class StoreAgent:
    def __init__(self, store_id: str, session: AsyncSession):
        self.store_id = store_id
        self.session = session
        self.llm = Ollama(base_url="http://localhost:11434", model="mistral")
        self.current_user = settings.current_user
        self.current_time = settings.datetime_obj

    async def check_inventory(self):
        query = select(StoreInventory, Product).join(Product).where(
            StoreInventory.store_id == self.store_id
        )
        result = await self.session.execute(query)
        inventory = result.fetchall()

        inventory_data = [
            {
                "product_id": inv.Product.id,
                "name": inv.Product.name,
                "current_stock": inv.StoreInventory.stock_level,
                "min_threshold": inv.StoreInventory.min_threshold,
                "last_updated_by": inv.StoreInventory.last_updated_by,
                "last_updated_at": inv.StoreInventory.last_updated_at.isoformat()
            }
            for inv in inventory
        ]

        prompt = f"""
        Analyze the following inventory data:
        {json.dumps(inventory_data)}
        
        Consider:
        1. Current stock levels vs minimum threshold
        2. Last update time and user
        3. Current time: {self.current_time.isoformat()}
        4. Current user: {self.current_user}
        
        Return a JSON list of products that need restocking.
        """
        
        response = await self.llm.agenerate([prompt])
        return json.loads(response.generations[0].text)

    async def update_inventory(self, product_id: str, quantity: int):
        query = select(StoreInventory).where(
            StoreInventory.store_id == self.store_id,
            StoreInventory.product_id == product_id
        )
        result = await self.session.execute(query)
        inventory = result.scalar_one_or_none()
        
        if inventory:
            inventory.stock_level += quantity
            inventory.last_updated_by = self.current_user
            inventory.last_updated_at = self.current_time
            await self.session.commit()
            return True
        return False