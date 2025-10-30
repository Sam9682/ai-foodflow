import cv2
import pytesseract
from PIL import Image
import re
from typing import List, Dict, Any
import openai
import os
import json

class MenuScanner:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def scan_menu_image(self, image_path: str) -> Dict[str, Any]:
        """Extract text from menu image using OCR"""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhance image for better OCR
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Extract text
            text = pytesseract.image_to_string(gray, lang='fra+eng')
            
            return {"success": True, "text": text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def parse_menu_with_ai(self, menu_text: str) -> List[Dict[str, Any]]:
        """Parse menu text into structured data using OpenAI"""
        prompt = f"""
        Parse this menu text into JSON format with the following structure:
        [
          {{
            "name": "item name",
            "description": "item description",
            "price": 12.50,
            "category": "category name",
            "allergens": ["allergen1", "allergen2"]
          }}
        ]
        
        Menu text:
        {menu_text}
        
        Return only valid JSON array, no additional text.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            menu_items = json.loads(response.choices[0].message.content)
            return menu_items
        except Exception as e:
            return []
    
    def scan_and_parse_menu(self, image_path: str) -> Dict[str, Any]:
        """Complete menu scanning and parsing pipeline"""
        # Extract text from image
        ocr_result = self.scan_menu_image(image_path)
        if not ocr_result["success"]:
            return ocr_result
        
        # Parse with AI
        menu_items = self.parse_menu_with_ai(ocr_result["text"])
        
        return {
            "success": True,
            "raw_text": ocr_result["text"],
            "menu_items": menu_items,
            "count": len(menu_items)
        }