"""
Grocery Assistant Logic Module

Core business logic for:
  - Managing grocery list (add, remove, retrieve items)
  - Category browsing (load and retrieve categories)
  - Smart suggestions (missing items, healthier alternatives)
  - Expiry reminders (items expiring soon)
  - Purchase history tracking

Data Persistence: JSON files
  - grocery_list.json: Current items in the grocery list
  - purchase_history.json: Historical purchase data for suggestions
  - categories.json: Predefined categories with items for browsing

Class: GroceryAssistant
  Handles all grocery management operations with automatic persistence.
"""

import datetime
import json
from typing import List, Dict
from models import Product

class GroceryAssistant:
    """Main class for managing grocery list and providing smart suggestions"""
    
    def __init__(self, purchase_history_file: str, grocery_list_file: str, categories_file: str = "categories.json"):
        """Initialize the assistant with file paths for data persistence"""
        self.items: List[Product] = []
        self.purchase_history_file = purchase_history_file
        self.grocery_list_file = grocery_list_file
        self.categories_file = categories_file
        self.purchase_history = self.load_purchase_history()
        self.categories = self.load_categories()
        self.load_grocery_list()

    def load_purchase_history(self) -> Dict:
        """Load purchase history from JSON file for generating suggestions"""
        try:
            with open(self.purchase_history_file, 'r') as f:
                history = json.load(f)
                
            normalized_history = {}
            for key, value in history.items():
                lower_key = key.lower()
                if lower_key in normalized_history:
                    existing_date = datetime.datetime.strptime(normalized_history[lower_key]['last_purchase_date'], '%Y-%m-%d').date()
                    new_date = datetime.datetime.strptime(value['last_purchase_date'], '%Y-%m-%d').date()
                    if new_date > existing_date:
                        normalized_history[lower_key]['last_purchase_date'] = value['last_purchase_date']
                else:
                    normalized_history[lower_key] = value
            
            # Overwrite the file with the cleaned history
            with open(self.purchase_history_file, 'w') as f:
                json.dump(normalized_history, f, indent=4)
                
            return normalized_history
            
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def load_categories(self) -> Dict[str, List[str]]:
        """Load predefined categories with items for the category browser"""
        try:
            with open(self.categories_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def load_grocery_list(self):
        """Load the current grocery list from JSON file"""
        try:
            with open(self.grocery_list_file, 'r') as f:
                data = json.load(f)
                self.items = [Product(**item_data) for item_data in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.items = []

    def save_grocery_list(self):
        """Save the current grocery list to JSON file"""
        with open(self.grocery_list_file, 'w') as f:
            json.dump([item.dict() for item in self.items], f, indent=4, default=str)

    # ============ GROCERY LIST OPERATIONS ============

    def add_item_to_list(self, item: Product) -> Product:
        """Add a new item to the grocery list and save to file"""
        self.items.append(item)
        self.save_grocery_list()
        return item

    def remove_item_from_list(self, item_name: str) -> bool:
        """Remove item from grocery list by name (case-insensitive)"""
        initial_count = len(self.items)
        self.items = [item for item in self.items if item.name.lower() != item_name.lower()]
        if len(self.items) < initial_count:
            self.save_grocery_list()
            return True
        return False

    def get_grocery_list(self) -> List[Product]:
        """Get all items in the current grocery list"""
        return self.items

    # ============ CATEGORY BROWSING ============

    def get_categories(self) -> Dict[str, List[str]]:
        """Get all categories with their items for the category browser"""
        return self.categories

    def get_category_items(self, category: str) -> List[str]:
        """Get items in a specific category"""
        return self.categories.get(category, [])

    # ============ SMART SUGGESTIONS ============

    def suggest_missing_items(self) -> List[str]:
        """
        Suggest items that were purchased before but not in current list.
        Items purchased more than 14 days ago are suggested.
        """
        suggestions = []
        current_list_lower = {item.name.lower() for item in self.items}
        
        processed_items = set()

        for item_name, data in self.purchase_history.items():
            item_name_lower = item_name.lower()
            if item_name_lower in processed_items:
                continue
            
            processed_items.add(item_name_lower)

            if item_name_lower not in current_list_lower:
                last_purchase_date = datetime.datetime.strptime(data['last_purchase_date'], '%Y-%m-%d').date()
                if (datetime.date.today() - last_purchase_date).days > 7:
                    suggestions.append(f"You bought {item_name} a last week, consider adding it.")
        return suggestions

    def suggest_healthier_alternatives(self) -> List[str]:
        """
        Suggest healthier alternatives for items in the current list.
        E.g., brown bread instead of white bread, water instead of soda.
        """
        suggestions = []
        healthier_alternatives = {
            "white bread": "brown bread",
            "soda": "water",
            "chips": "nuts",
            "white rice": "brown rice",
            "regular milk": "almond milk",
            "butter": "olive oil",
            "ice cream": "greek yogurt",
            "cookies": "whole grain oats",
            "candy": "fresh fruit"
        }
        for item in self.items:
            if item.name.lower() in healthier_alternatives:
                suggestion = healthier_alternatives[item.name.lower()]
                suggestions.append(f"Instead of {item.name}, consider {suggestion} as a healthier alternative.")
        return suggestions

    def get_expiry_reminders(self) -> List[str]:
        """Get reminders for items expiring within 5 days (1-5 day window)"""
        reminders = []
        today = datetime.date.today()
        for item in self.items:
            if item.expiry_date:
                time_to_expiry = (item.expiry_date - today).days
                if 1 <= time_to_expiry <= 5:
                    reminders.append(f"Reminder: {item.name} is expiring in {time_to_expiry} days.")
        return reminders

    # ============ PURCHASE MANAGEMENT ============

    def mark_items_as_purchased(self) -> Dict:
        """
        Mark all items as purchased:
        1. Update purchase history with today's date for each item
        2. Clear the grocery list
        """
        today_str = datetime.date.today().isoformat()
        for item in self.items:
            self.purchase_history[item.name.lower()] = {"last_purchase_date": today_str}

        with open(self.purchase_history_file, 'w') as f:
            json.dump(self.purchase_history, f, indent=4)
        
        self.items = []
        self.save_grocery_list()
        return {"message": "Purchase history updated and grocery list cleared."}


# Initialize the global assistant instance
assistant = GroceryAssistant(purchase_history_file="purchase_history.json", grocery_list_file="grocery_list.json")
