import os
from supabase import create_client, Client
from typing import Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        # Temporary hardcoded values for testing
        self.supabase_url = "https://jycfwicekxqhrrkjkxpl.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp5Y2Z3aWNla3hxaHJya2preHBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4ODU5OTgsImV4cCI6MjA2NDQ2MTk5OH0.JAlEgPHUA269ICaH-IgqbZRUhRrVTv4GmqEWMI03ics"
        
        logger.info(f"Initializing Supabase client with URL: {self.supabase_url}")
        logger.info(f"API key exists: {bool(self.supabase_key)}")
        logger.info(f"API key length: {len(self.supabase_key) if self.supabase_key else 0}")
        
        try:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Successfully created Supabase client")
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {str(e)}")
            raise Exception(f"Failed to initialize Supabase client: {str(e)}")

    async def save_recipe_history(self, user_id: str, recipe_data: Dict) -> Dict:
        try:
            logger.info(f"Attempting to save recipe history for user: {user_id}")
            logger.info(f"Recipe data: {json.dumps(recipe_data)}")
            
            data_to_insert = {
                'user_id': user_id,
                'ingredients': recipe_data.get('ingredients', []),
                'dietary_restrictions': recipe_data.get('dietary_restrictions', []),
                'recipes': recipe_data.get('recipes', []),
                'meal_plan': recipe_data.get('meal_plan', {}),
                'grocery_list': recipe_data.get('grocery_list', [])
            }
            
            logger.info(f"Formatted data for insert: {json.dumps(data_to_insert)}")
            
            response = self.client.table('recipe_history').insert(data_to_insert).execute()
            logger.info(f"Successfully saved recipe history. Response: {json.dumps(response.data)}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Error saving recipe history: {str(e)}")
            logger.error(f"User ID: {user_id}")
            logger.error(f"Data attempted to save: {json.dumps(recipe_data)}")
            raise Exception(f"Failed to save recipe history: {str(e)}")

    async def get_recipe_history(self, user_id: str) -> List[Dict]:
        try:
            logger.info(f"Fetching recipe history for user: {user_id}")
            response = self.client.table('recipe_history').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            logger.info(f"Successfully retrieved recipe history. Count: {len(response.data)}")
            return response.data
        except Exception as e:
            logger.error(f"Error fetching recipe history: {str(e)}")
            logger.error(f"User ID: {user_id}")
            raise Exception(f"Failed to fetch recipe history: {str(e)}")

    async def toggle_favorite_recipe(self, user_id: str, recipe_id: str, recipe_data: Dict) -> Dict:
        try:
            logger.info(f"Toggling favorite recipe for user: {user_id}, recipe: {recipe_id}")
            # Check if recipe is already favorited
            existing = self.client.table('favorite_recipes').select('*').eq('user_id', user_id).eq('recipe_id', recipe_id).execute()
            logger.info(f"Found existing favorites: {len(existing.data)}")
            
            if existing.data:
                # Remove from favorites
                logger.info(f"Removing recipe {recipe_id} from favorites")
                self.client.table('favorite_recipes').delete().eq('id', existing.data[0]['id']).execute()
                return {'status': 'removed', 'recipe_id': recipe_id}
            else:
                # Add to favorites
                logger.info(f"Adding recipe {recipe_id} to favorites")
                response = self.client.table('favorite_recipes').insert({
                    'user_id': user_id,
                    'recipe_id': recipe_id,
                    'recipe_name': recipe_data.get('name'),
                    'recipe_instructions': recipe_data.get('instructions')
                }).execute()
                logger.info(f"Successfully added to favorites. Response: {json.dumps(response.data)}")
                return {'status': 'added', 'recipe': response.data[0]}
        except Exception as e:
            logger.error(f"Error toggling favorite recipe: {str(e)}")
            logger.error(f"User ID: {user_id}, Recipe ID: {recipe_id}")
            logger.error(f"Recipe data: {json.dumps(recipe_data)}")
            raise Exception(f"Failed to toggle favorite recipe: {str(e)}")

    async def get_favorite_recipes(self, user_id: str) -> List[Dict]:
        try:
            logger.info(f"Fetching favorite recipes for user: {user_id}")
            response = self.client.table('favorite_recipes').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            logger.info(f"Successfully retrieved favorite recipes. Count: {len(response.data)}")
            return response.data
        except Exception as e:
            logger.error(f"Error fetching favorite recipes: {str(e)}")
            logger.error(f"User ID: {user_id}")
            raise Exception(f"Failed to fetch favorite recipes: {str(e)}") 