"""
Chatbot Logic Module for Grocery Assistant

Handles natural language queries from the user and translates them into
actions for the GroceryAssistant.
"""


import re
from assistant_logic import assistant, Product

class Chatbot:
    """A simple chatbot to interact with the Grocery Assistant."""

    def __init__(self, assistant):
        """Initialize the chatbot with a GroceryAssistant instance."""
        self.assistant = assistant

    def get_reply(self, message: str) -> dict:
        """
        Process a user message and return a reply and whether the grocery list
        needs to be refreshed.
        """
        message = message.lower()
        reply = "Sorry, I don't understand."
        refresh = False

        if "add" in message:
            reply, refresh = self._handle_add(message)
        elif "remove" in message:
            reply, refresh = self._handle_remove(message)
        elif "expiring" in message:
            reply, refresh = self._handle_expiring(message)
        elif "suggestions" in message:
            reply, refresh = self._handle_suggestions(message)
        elif "list" in message or "show list" in message:
            reply, refresh = self._handle_list(message)
        elif "clear list" in message:
            reply, refresh = self._handle_clear(message)
        elif "purchase" in message:
            reply, refresh = self._handle_purchase(message)
        elif "hello" in message or "hi" in message:
            reply = "Hello! How can I help you with your groceries today?"

        return {"reply": reply, "refresh": refresh}

    def _handle_add(self, message: str) -> (str, bool):
        """Handle adding an item to the grocery list."""
        # Regex to capture "add [quantity] [unit] of [item name] to [category]"
        match = re.search(r"add\s+((?P<quantity>\d+(\.\d+)?)\s+)?(?P<unit>\w+)?(\s+of)?\s+(?P<name>[\w\s]+?)(\s+to\s+(?P<category>\w+))?$", message)

        if not match:
            return "I'm sorry, I couldn't figure out what to add. Please use the format: 'add [quantity] [unit] of [item name] to [category]'", False

        item_name = match.group("name").strip()
        unit = match.group("unit") or "pcs"
        category = match.group("category")

        product = Product(name=item_name, unit=unit, category=category)
        self.assistant.add_item_to_list(product)
        
        return f"I've added {item_name} to your list.", True

    def _handle_remove(self, message: str) -> (str, bool):
        """Handle removing an item from the grocery list."""
        match = re.search(r"remove\s+(?P<name>[\w\s]+)", message)
        if not match:
            return "I'm sorry, I couldn't figure out what to remove. Please use the format: 'remove [item name]'", False

        item_name = match.group("name").strip()
        if self.assistant.remove_item_from_list(item_name):
            return f"I've removed {item_name} from your list.", True
        else:
            return f"I couldn't find {item_name} in your list.", False

    def _handle_expiring(self, message: str) -> (str, bool):
        """Handle getting expiry reminders."""
        reminders = self.assistant.get_expiry_reminders()
        if reminders:
            return "Here are the items that are expiring soon:\n" + "\n".join(reminders), False
        else:
            return "You have no items expiring soon.", False

    def _handle_suggestions(self, message: str) -> (str, bool):
        """Handle getting suggestions."""
        missing = self.assistant.suggest_missing_items()
        healthier = self.assistant.suggest_healthier_alternatives()
        
        suggestions = []
        if missing:
            suggestions.append("Missing items:\n" + "\n".join(missing))
        if healthier:
            suggestions.append("Healthier alternatives:\n" + "\n".join(healthier))

        if suggestions:
            return "\n\n".join(suggestions), False
        else:
            return "I have no suggestions for you right now.", False

    def _handle_list(self, message: str) -> (str, bool):
        """Handle displaying the current grocery list."""
        return self._get_list(), False

    def _handle_clear(self, message: str) -> (str, bool):
        """Handle clearing the grocery list."""
        self.assistant.mark_items_as_purchased()
        return "I've cleared your grocery list and updated your purchase history.", True

    def _handle_purchase(self, message: str) -> (str, bool):
        """Handle marking all items as purchased."""
        self.assistant.mark_items_as_purchased()
        return "I've marked all items as purchased and updated your purchase history.", True

    def _get_list(self) -> str:
        """Get the current grocery list as a formatted string."""
        if not self.assistant.items:
            return "Your grocery list is empty."

        list_str = "Here's your grocery list:\n"
        for item in self.assistant.items:
            list_str += f"- {item.name} ({item.unit}"
            if item.category:
                list_str += f", {item.category}"
            list_str += ")\n"
        return list_str

# Initialize the global chatbot instance
chatbot = Chatbot(assistant)

