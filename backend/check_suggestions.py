import json
from assistant_logic import assistant

# Reload data
assistant.purchase_history = assistant.load_purchase_history()
assistant.load_grocery_list()

print('MISSING:')
print(json.dumps(assistant.suggest_missing_items(), ensure_ascii=False, indent=2))
print('\nHEALTHIER:')
print(json.dumps(assistant.suggest_healthier_alternatives(), ensure_ascii=False, indent=2))
print('\nEXPIRY:')
print(json.dumps(assistant.get_expiry_reminders(), ensure_ascii=False, indent=2))
