#!/usr/bin/env python3
"""Initialize Le Bouzou restaurant data"""

from sqlalchemy.orm import Session
from src.app.core.database import SessionLocal, create_tables
from src.app.models.restaurant import Restaurant, MenuItem

def init_le_bouzou_data():
    """Initialize Le Bouzou restaurant with sample menu items"""
    create_tables()
    db = SessionLocal()
    
    try:
        # Create Le Bouzou restaurant
        restaurant = Restaurant(
            name="Le Bouzou",
            location="Montpellier/Castelnau-le-Lez",
            cuisine_type="French",
            phone="+33 4 67 XX XX XX",
            email="contact@lebouzou.fr",
            address="123 Rue de la République, 34170 Castelnau-le-Lez",
            opening_hours={
                "monday": {"open": "11:30", "close": "14:30"},
                "tuesday": {"open": "11:30", "close": "14:30"},
                "wednesday": {"open": "11:30", "close": "14:30"},
                "thursday": {"open": "11:30", "close": "14:30"},
                "friday": {"open": "11:30", "close": "14:30"},
                "saturday": {"open": "18:00", "close": "22:30"},
                "sunday": {"closed": True}
            }
        )
        
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
        
        # Sample menu items
        menu_items = [
            {
                "name": "Burger Le Bouzou",
                "description": "Burger signature avec steak haché, fromage, salade, tomate",
                "price": 14.50,
                "category": "Burgers",
                "is_available": True,
                "allergens": ["gluten", "lactose"]
            },
            {
                "name": "Salade César",
                "description": "Salade verte, poulet grillé, parmesan, croûtons, sauce césar",
                "price": 12.90,
                "category": "Salades",
                "is_available": True,
                "allergens": ["gluten", "lactose", "œufs"]
            },
            {
                "name": "Pizza Margherita",
                "description": "Base tomate, mozzarella, basilic frais",
                "price": 11.50,
                "category": "Pizzas",
                "is_available": True,
                "allergens": ["gluten", "lactose"]
            },
            {
                "name": "Tiramisu",
                "description": "Dessert italien traditionnel au café",
                "price": 6.50,
                "category": "Desserts",
                "is_available": True,
                "allergens": ["gluten", "lactose", "œufs"]
            },
            {
                "name": "Coca-Cola",
                "description": "Boisson gazeuse 33cl",
                "price": 2.50,
                "category": "Boissons",
                "is_available": True,
                "allergens": []
            }
        ]
        
        for item_data in menu_items:
            menu_item = MenuItem(
                restaurant_id=restaurant.id,
                **item_data
            )
            db.add(menu_item)
        
        db.commit()
        print(f"✅ Le Bouzou restaurant created with ID: {restaurant.id}")
        print(f"✅ {len(menu_items)} menu items added")
        
    except Exception as e:
        print(f"❌ Error initializing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_le_bouzou_data()