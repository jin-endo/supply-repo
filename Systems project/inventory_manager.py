import json
import os
from typing import List, Dict, Optional

class InventoryManager:
    def __init__(self, filename: str = "inventory.json"):
        self.filename = filename
        self._initialize_file()   #create json if it doesnt exist
    
    def _initialize_file(self):
        """Create empty JSON file if it doesn't exist"""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)
    
    def _load_data(self) -> List[Dict]:
        """Load inventory data safely"""
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_data(self, data: List[Dict]):
        """Save data with atomic write""" # used this to prevent partial file no crashes
        temp_file = f"{self.filename}.tmp"
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2) #put this in a nice format
        os.replace(temp_file, self.filename) #atomic file replace
    
    def add_item(self, item: Dict) -> int:
        """Add a new item to inventory, returns new item ID"""
        data = self._load_data()
        new_id = max([i.get('id', 0) for i in data] or [0]) + 1
        item['id'] = new_id
        data.append(item)
        self._save_data(data)# adding ids here
        return new_id
    
    def get_all_items(self) -> List[Dict]:
        """Return all inventory items"""
        return self._load_data()
    
    def get_item(self, item_id: int) -> Optional[Dict]:
        """Get single item by ID"""
        for item in self._load_data():
            if item.get('id') == item_id:
                return item
        return None
    
    def update_item(self, item_id: int, updates: Dict) -> bool:
        """Update existing item, returns True if successful"""
        data = self._load_data()
        updated = False
        #start of updating items
        for item in data:
            if item.get('id') == item_id:
                item.update(updates)
                updated = True
                break
                
        if updated:
            self._save_data(data)#only for changes
        return updated
    
    def delete_item(self, item_id: int) -> bool:
        """Remove item by ID, returns True if successful"""
        data = [i for i in self._load_data() if i.get('id') != item_id]
        self._save_data(data)
        return len(data) != len(self._load_data())  # Check if item was removed
    
    def search_items(self, search_term: str) -> List[Dict]:
        """Search items by name or category"""
        search_term = search_term.lower()
        return [
            item for item in self._load_data()
            if search_term in item.get('name', '').lower() or 
               search_term in item.get('category', '').lower()
        ]