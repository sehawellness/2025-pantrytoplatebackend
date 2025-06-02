from fastapi import FastAPI, HTTPException
from .models import RecipeRequest, RecipeResponse, FavoriteRequest, FavoriteResponse
from .services.recipe_service import RecipeService
from .services.supabase_service import SupabaseService
from dotenv import load_dotenv
import os
import logging
import traceback
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="PantryToPlate API")
recipe_service = RecipeService()
supabase_service = SupabaseService()

@app.get("/test-supabase/{user_id}")
async def test_supabase(user_id: str):
    """Test endpoint to verify Supabase integration"""
    try:
        # Try to save a test recipe
        test_data = {
            "ingredients": ["test"],
            "dietary_restrictions": ["test"],
            "recipes": [{"name": "Test Recipe", "instructions": "Test Instructions"}],
            "meal_plan": {"Monday": "Test Recipe"},
            "grocery_list": ["test ingredient"]
        }
        
        # Save to history
        history_result = await supabase_service.save_recipe_history(user_id, test_data)
        logger.info(f"Saved test recipe to history: {history_result}")
        
        # Get history
        history = await supabase_service.get_recipe_history(user_id)
        logger.info(f"Retrieved recipe history: {history}")
        
        return {
            "status": "success",
            "saved_recipe": history_result,
            "history": history
        }
    except Exception as e:
        logger.error(f"Error testing Supabase: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-recipe", response_model=RecipeResponse)
async def generate_recipe(request: RecipeRequest):
    try:
        # Log the incoming request
        logger.info(f"Received request with ingredients: {request.ingredients} and restrictions: {request.dietary_restrictions}")
        
        # Check if API key exists
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            logger.error("OpenRouter API key not found in environment variables")
            raise HTTPException(status_code=500, detail="API key not configured")
        
        # Generate recipes
        result = await recipe_service.generate_recipes(
            request.ingredients,
            request.dietary_restrictions
        )

        # Save to history if user_id is provided
        if request.user_id:
            try:
                history_data = {
                    'ingredients': request.ingredients,
                    'dietary_restrictions': request.dietary_restrictions,
                    **result
                }
                await supabase_service.save_recipe_history(request.user_id, history_data)
            except Exception as e:
                logger.error(f"Failed to save recipe history: {str(e)}")
                # Don't fail the request if history saving fails
                
        return result
    except Exception as e:
        logger.error(f"Error in generate_recipe: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recipe-history/{user_id}")
async def get_recipe_history(user_id: str):
    try:
        return await supabase_service.get_recipe_history(user_id)
    except Exception as e:
        logger.error(f"Error fetching recipe history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/favorite-recipe", response_model=FavoriteResponse)
async def toggle_favorite_recipe(request: FavoriteRequest):
    try:
        return await supabase_service.toggle_favorite_recipe(
            request.user_id,
            request.recipe_id,
            request.recipe_data.dict()
        )
    except Exception as e:
        logger.error(f"Error toggling favorite recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/favorite-recipes/{user_id}")
async def get_favorite_recipes(user_id: str):
    try:
        return await supabase_service.get_favorite_recipes(user_id)
    except Exception as e:
        logger.error(f"Error fetching favorite recipes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/debug-env")
async def debug_env():
    """Debug endpoint to check environment variables (without exposing sensitive data)"""
    return {
        "api_key_exists": "OPENROUTER_API_KEY" in os.environ,
        "api_key_length": len(os.getenv("OPENROUTER_API_KEY", "")) if "OPENROUTER_API_KEY" in os.environ else 0,
        "supabase_url_exists": "SUPABASE_URL" in os.environ,
        "supabase_key_exists": "SUPABASE_KEY" in os.environ,
        "python_version": sys.version,
        "env_vars_available": list(os.environ.keys())
    } 