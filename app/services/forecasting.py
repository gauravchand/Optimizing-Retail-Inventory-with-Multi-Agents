from langchain.llms import Ollama
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import SalesHistory, DemandForecast
from datetime import datetime, timedelta
import json

class ForecastingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm = Ollama(base_url="http://localhost:11434", model="mistral")

    async def generate_forecast(self, store_id: str, days: int = 7):
        # Get historical sales data
        query = select(SalesHistory).where(
            SalesHistory.store_id == store_id,
            SalesHistory.sale_date >= datetime.now() - timedelta(days=30)
        ).order_by(SalesHistory.sale_date.desc())
        
        result = await self.session.execute(query)
        historical_data = result.fetchall()

        # Prepare data for LLM
        sales_data = [
            {
                "product_id": sale.product_id,
                "quantity": sale.quantity,
                "date": sale.sale_date.isoformat()
            }
            for sale in historical_data
        ]

        prompt = f"""
        Based on this historical sales data:
        {json.dumps(sales_data)}
        
        Predict daily sales for the next {days} days considering:
        1. Historical patterns
        2. Seasonal trends
        3. Recent changes in demand
        
        Return the forecast as a JSON array with dates and predicted quantities.
        """

        response = await self.llm.agenerate([prompt])
        forecast_data = json.loads(response.generations[0].text)
        
        # Store forecasts in database
        for day_forecast in forecast_data:
            forecast = DemandForecast(
                store_id=store_id,
                product_id=day_forecast["product_id"],
                forecast_date=datetime.fromisoformat(day_forecast["date"]),
                predicted_demand=day_forecast["quantity"],
                confidence=day_forecast.get("confidence", 0.8)
            )
            self.session.add(forecast)
        
        await self.session.commit()
        return forecast_data