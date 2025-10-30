from abc import ABC, abstractmethod
from typing import Dict, List, Any
import requests
import json
from app.models.restaurant import MenuItem

class PlatformAdapter(ABC):
    @abstractmethod
    def authenticate(self) -> bool:
        pass
    
    @abstractmethod
    def sync_menu_items(self, items: List[MenuItem]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def update_restaurant_info(self, restaurant_data: Dict) -> Dict[str, Any]:
        pass

class UberEatsAdapter(PlatformAdapter):
    def __init__(self, client_id: str, client_secret: str, store_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.store_id = store_id
        self.base_url = "https://api.uber.com/v1/eats"
        self.access_token = None
    
    def authenticate(self) -> bool:
        auth_url = "https://login.uber.com/oauth/v2/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "eats.store"
        }
        
        try:
            response = requests.post(auth_url, data=data)
            if response.status_code == 200:
                self.access_token = response.json()["access_token"]
                return True
        except Exception as e:
            print(f"Uber Eats auth error: {e}")
        return False
    
    def sync_menu_items(self, items: List[MenuItem]) -> Dict[str, Any]:
        if not self.access_token:
            return {"success": False, "error": "Not authenticated"}
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        menu_data = {
            "menus": [{
                "menu_id": "main_menu",
                "categories": self._format_menu_items(items)
            }]
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/stores/{self.store_id}/menus",
                headers=headers,
                json=menu_data
            )
            return {"success": response.status_code == 200, "response": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_menu_items(self, items: List[MenuItem]) -> List[Dict]:
        categories = {}
        for item in items:
            if item.category not in categories:
                categories[item.category] = []
            
            categories[item.category].append({
                "id": str(item.id),
                "title": item.name,
                "description": item.description,
                "price": int(item.price * 100),  # Convert to cents
                "available": item.is_available,
                "image_url": item.image_url
            })
        
        return [{"title": cat, "items": items} for cat, items in categories.items()]
    
    def update_restaurant_info(self, restaurant_data: Dict) -> Dict[str, Any]:
        if not self.access_token:
            return {"success": False, "error": "Not authenticated"}
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            response = requests.put(
                f"{self.base_url}/stores/{self.store_id}",
                headers=headers,
                json=restaurant_data
            )
            return {"success": response.status_code == 200, "response": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}

class DeliverooAdapter(PlatformAdapter):
    def __init__(self, api_key: str, restaurant_id: str):
        self.api_key = api_key
        self.restaurant_id = restaurant_id
        self.base_url = "https://api.deliveroo.com/v1"
    
    def authenticate(self) -> bool:
        return bool(self.api_key)
    
    def sync_menu_items(self, items: List[MenuItem]) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        menu_data = {"menu": self._format_menu_items(items)}
        
        try:
            response = requests.put(
                f"{self.base_url}/restaurants/{self.restaurant_id}/menu",
                headers=headers,
                json=menu_data
            )
            return {"success": response.status_code == 200, "response": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_menu_items(self, items: List[MenuItem]) -> Dict:
        categories = {}
        for item in items:
            if item.category not in categories:
                categories[item.category] = []
            
            categories[item.category].append({
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "available": item.is_available,
                "image": item.image_url
            })
        
        return {"categories": [{"name": cat, "items": items} for cat, items in categories.items()]}
    
    def update_restaurant_info(self, restaurant_data: Dict) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.put(
                f"{self.base_url}/restaurants/{self.restaurant_id}",
                headers=headers,
                json=restaurant_data
            )
            return {"success": response.status_code == 200, "response": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}

class JustEatAdapter(PlatformAdapter):
    def __init__(self, api_key: str, tenant_id: str):
        self.api_key = api_key
        self.tenant_id = tenant_id
        self.base_url = "https://api.just-eat.com/v1"
    
    def authenticate(self) -> bool:
        return bool(self.api_key)
    
    def sync_menu_items(self, items: List[MenuItem]) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        menu_data = self._format_menu_items(items)
        
        try:
            response = requests.put(
                f"{self.base_url}/tenants/{self.tenant_id}/menu",
                headers=headers,
                json=menu_data
            )
            return {"success": response.status_code == 200, "response": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_menu_items(self, items: List[MenuItem]) -> Dict:
        categories = {}
        for item in items:
            if item.category not in categories:
                categories[item.category] = []
            
            categories[item.category].append({
                "productId": item.id,
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "available": item.is_available,
                "imageUrl": item.image_url
            })
        
        return {"categories": [{"name": cat, "products": items} for cat, items in categories.items()]}
    
    def update_restaurant_info(self, restaurant_data: Dict) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.put(
                f"{self.base_url}/tenants/{self.tenant_id}/restaurant",
                headers=headers,
                json=restaurant_data
            )
            return {"success": response.status_code == 200, "response": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}