import datetime

class Product:
    def __init__(self, name, category, purchase_date, expiry_date):
        self.name = name
        self.category = category
        self.purchase_date = purchase_date
        self.expiry_date = expiry_date

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "purchase_date": self.purchase_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
        }

    @classmethod
    def from_dict(cls, data):
        purchase_date = datetime.datetime.strptime(data["purchase_date"], '%Y-%m-%d').date()
        expiry_date = datetime.datetime.strptime(data["expiry_date"], '%Y-%m-%d').date() if data["expiry_date"] else None
        return cls(data["name"], data["category"], purchase_date, expiry_date)

    def __str__(self):
        return f"{self.name} (Category: {self.category}, Purchased: {self.purchase_date}, Expires: {self.expiry_date})"
