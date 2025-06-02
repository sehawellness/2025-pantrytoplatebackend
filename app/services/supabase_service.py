import os
from supabase import create_client, Client
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise Exception("Supabase credentials not found in environment variables")
        self.client: Client = create_client(supabase_url, supabase_key)

    async def save_recipe_history(self, user_id: str, recipe_data: Dict) -> Dict:
        try:
            response = self.client.table('recipe_history').insert({
                'user_id': user_id,
                'ingredients': recipe_data.get('ingredients', []),
                'dietary_restrictions': recipe_data.get('dietary_restrictions', []),
                'recipes': recipe_data.get('recipes', []),
                'meal_plan': recipe_data.get('meal_plan', {}),
                'grocery_list': recipe_data.get('grocery_list', [])
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error saving recipe history: {str(e)}")
            raise Exception(f"Failed to save recipe history: {str(e)}")

    async def get_recipe_history(self, user_id: str) -> List[Dict]:
        try:
            response = self.client.table('recipe_history').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching recipe history: {str(e)}")
            raise Exception(f"Failed to fetch recipe history: {str(e)}")

    async def toggle_favorite_recipe(self, user_id: str, recipe_id: str, recipe_data: Dict) -> Dict:
        try:
            # Check if recipe is already favorited
            existing = self.client.table('favorite_recipes').select('*').eq('user_id', user_id).eq('recipe_id', recipe_id).execute()
            
            if existing.data:
                # Remove from favorites
                self.client.table('favorite_recipes').delete().eq('id', existing.data[0]['id']).execute()
                return {'status': 'removed', 'recipe_id': recipe_id}
            else:
                # Add to favorites
                response = self.client.table('favorite_recipes').insert({
                    'user_id': user_id,
                    'recipe_id': recipe_id,
                    'recipe_name': recipe_data.get('name'),
                    'recipe_instructions': recipe_data.get('instructions')
                }).execute()
                return {'status': 'added', 'recipe': response.data[0]}
        except Exception as e:
            logger.error(f"Error toggling favorite recipe: {str(e)}")
            raise Exception(f"Failed to toggle favorite recipe: {str(e)}")

    async def get_favorite_recipes(self, user_id: str) -> List[Dict]:
        try:
            response = self.client.table('favorite_recipes').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching favorite recipes: {str(e)}")
            raise Exception(f"Failed to fetch favorite recipes: {str(e)}") 