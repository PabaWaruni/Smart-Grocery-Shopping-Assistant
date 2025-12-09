"""
Grocery Assistant - FastAPI Backend Server

Purpose: REST API for grocery list management with smart suggestions and reminders.

API Endpoints:
  GET /grocery-list             - Fetch all items in the grocery list
  POST /grocery-list            - Add a new item to the grocery list
  DELETE /grocery-list/{name}   - Remove an item by name
  
  GET /categories               - Fetch all categories with their items
  GET /categories/{category}    - Fetch items in a specific category
  
  GET /suggestions/missing      - Get suggestions for items purchased previously
  GET /suggestions/healthier    - Get healthier alternatives for current items
  GET /reminders/expiry         - Get items expiring soon
  POST /purchase                - Mark all items as purchased and clear the list

Runs on: http://127.0.0.1:8000
CORS: Enabled for all origins (safe for local development)

Data Storage: JSON files in the backend directory
  - grocery_list.json           - Current grocery items
  - purchase_history.json       - Purchase history for suggestions
  - categories.json             - Predefined categories and items
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models import Product
from assistant_logic import assistant
from chatbot_logic import chatbot
from typing import List, Dict

app = FastAPI(
    title="Grocery Assistant API",
    description="Smart grocery list manager with suggestions and reminders",
    version="1.0.0"
)

# CORS middleware - enables frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (safe for local development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

class Message(BaseModel):
    message: str

# ============ GROCERY LIST ENDPOINTS ============

@app.get("/grocery-list", response_model=List[Product])
def get_grocery_list():
    """Fetch all items in the current grocery list"""
    return assistant.get_grocery_list()

@app.post("/grocery-list", response_model=Product)
def add_item_to_list(item: Product):
    """Add a new item to the grocery list with name, unit, and optional category"""
    return assistant.add_item_to_list(item)

@app.delete("/grocery-list/{item_name}")
def remove_item_from_list(item_name: str):
    """Remove an item from the grocery list by name (case-insensitive)"""
    return assistant.remove_item_from_list(item_name)

# ============ CATEGORY BROWSING ENDPOINTS ============

@app.get("/categories", response_model=Dict[str, List[str]])
def get_categories():
    """Fetch all categories with their items for browsing"""
    return assistant.get_categories()

@app.get("/categories/{category}", response_model=List[str])
def get_category_items(category: str):
    """Fetch items in a specific category"""
    return assistant.get_category_items(category)

# ============ SMART SUGGESTIONS & REMINDERS ============

@app.get("/suggestions/missing")
def get_missing_item_suggestions():
    """Suggest items that were purchased before but are not in current list"""
    # Reload purchase history and grocery list to ensure suggestions use latest data
    assistant.purchase_history = assistant.load_purchase_history()
    assistant.load_grocery_list()
    return {"suggestions": assistant.suggest_missing_items()}

@app.get("/suggestions/healthier")
def get_healthier_alternative_suggestions():
    """Suggest healthier alternatives for items in the current list"""
    # Ensure grocery list is current before suggesting alternatives
    assistant.load_grocery_list()
    return {"suggestions": assistant.suggest_healthier_alternatives()}

@app.get("/reminders/expiry")
def get_expiry_reminders():
    """Get reminders for items expiring soon (within 3 days)"""
    # Ensure grocery list is current before computing expiry reminders
    assistant.load_grocery_list()
    return {"reminders": assistant.get_expiry_reminders()}

# ============ CHATBOT ENDPOINT ============

@app.post("/chatbot")
def chat(message: Message):
    """Process a user message from the chatbot and return a reply."""
    return chatbot.get_reply(message.message)

# ============ PURCHASE MANAGEMENT ============

@app.post("/purchase")
def mark_items_as_purchased():
    """Mark all items as purchased, update history, and clear the grocery list"""
    return assistant.mark_items_as_purchased()

if __name__ == "__main__":
    import uvicorn
    # Start the FastAPI server with automatic reload for development
    uvicorn.run(app, host="127.0.0.1", port=8002)