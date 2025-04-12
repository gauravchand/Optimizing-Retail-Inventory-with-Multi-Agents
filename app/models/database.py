from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
from app.config.constants import CURRENT_USER, get_datetime_obj, DATABASE_URL
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    name = Column(String)
    category = Column(String)
    price = Column(Float)
    supplier_id = Column(String)
    created_by = Column(String, default=CURRENT_USER)
    created_at = Column(DateTime, default=get_datetime_obj())
    last_updated = Column(DateTime, default=get_datetime_obj())

class StoreInventory(Base):
    __tablename__ = "store_inventory"

    id = Column(Integer, primary_key=True)
    store_id = Column(String)
    product_id = Column(String, ForeignKey("products.id"))
    stock_level = Column(Integer)
    min_threshold = Column(Integer)
    last_updated_by = Column(String, default=CURRENT_USER)
    last_updated_at = Column(DateTime, default=get_datetime_obj())

class SalesHistory(Base):
    __tablename__ = "sales_history"

    id = Column(Integer, primary_key=True)
    store_id = Column(String)
    product_id = Column(String, ForeignKey("products.id"))
    quantity = Column(Integer)
    sale_date = Column(DateTime, default=get_datetime_obj())
    recorded_by = Column(String, default=CURRENT_USER)

async def init_db():
    try:
        logger.info(f"Initializing database as {CURRENT_USER}")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

async def get_session():
    try:
        async with async_session() as session:
            yield session
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise