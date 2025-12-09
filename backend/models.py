"""
Data Models for Grocery Assistant

Defines the Product model used for API requests/responses and data validation.
Built with Pydantic for automatic JSON serialization and type validation.
"""

from pydantic import BaseModel
from datetime import date
from typing import Optional


class Product(BaseModel):
    """
    Represents a grocery item in the system.
    
    Fields:
    - name (str): Item name (required) - e.g., "Apple", "Milk"
    - quantity (str, optional): Quantity of the item - e.g., "5", "2.5" (rarely used)
    - unit (str, optional): Unit of measurement - e.g., "kg", "liters", "pieces"
    - category (str, optional): Category the item belongs to - e.g., "Fruits & Vegetables"
    - purchase_date (date, optional): When the item was purchased - for future features
    - expiry_date (date, optional): When the item expires - for expiry reminders
    
    Example usage:
      Product(name="Apple", unit="kg", category="Fruits & Vegetables")
      Product(name="Milk", unit="liters", category="Dairy & Eggs", expiry_date=date(2025, 12, 31))
    """
    name: str
    quantity: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
