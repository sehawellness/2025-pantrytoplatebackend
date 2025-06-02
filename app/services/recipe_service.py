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
        
        if not self.api_key:
            raise Exception("OpenRouter API key not found in environment variables")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://pantrytoplate-api.onrender.com",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistralai/devstral-small:free",
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
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
                    error_detail = response.json() if response.content else response.text
                    raise Exception(f"API call failed with status {response.status_code}: {error_detail}")
        except Exception as e:
            raise Exception(f"Error calling OpenRouter API: {str(e)}")
    
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
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse API response as JSON: {str(e)}, Content: {content}")
        except Exception as e:
            raise Exception(f"Unexpected error parsing response: {str(e)}") 