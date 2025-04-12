from datetime import datetime

CURRENT_USER = "AkarshanGupta"
CURRENT_DATETIME = "2025-04-10 15:31:06"
DATABASE_URL = "sqlite+aiosqlite:///retail_inventory.db"

def get_datetime_obj():
    return datetime.strptime(CURRENT_DATETIME, "%Y-%m-%d %H:%M:%S")