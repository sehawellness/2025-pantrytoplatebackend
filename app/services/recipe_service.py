import os
import httpx
import json
from typing import List, Dict

class RecipeService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
    async def generate_recipes(self, ingredients: List[str], dietary_restrictions: List[str]) -> Dict:
        prompt = self._create_prompt(ingredients, dietary_restrictions)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://pantrytoplate-api.onrender.com",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistralai/devstral-small:free",
            "messages": [{"role": "user", "content": prompt}]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_response(result['choices'][0]['message']['content'])
            else:
                raise Exception(f"API call failed: {response.text}")
    
    def _create_prompt(self, ingredients: List[str], dietary_restrictions: List[str]) -> str:
        return f"""Given these ingredients: {', '.join(ingredients)}
        and dietary restrictions: {', '.join(dietary_restrictions)},
        please provide:
        1. 3 possible recipes that can be made
        2. A weekly meal plan
        3. A grocery shopping list
        Format the response as a JSON with keys: 'recipes', 'meal_plan', 'grocery_list'"""
    
    def _parse_response(self, content: str) -> Dict:
        try:
            return json.loads(content)
        except:
            # Fallback in case the LLM doesn't return valid JSON
            return {
                "recipes": [],
                "meal_plan": {},
                "grocery_list": []
            } 