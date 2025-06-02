from fastapi import FastAPI, HTTPException
from .models import RecipeRequest, RecipeResponse
from .services.recipe_service import RecipeService
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
        
        # Log API key presence (not the actual key)
        logger.info(f"API key exists and length: {len(api_key)}")
        
        result = await recipe_service.generate_recipes(
            request.ingredients,
            request.dietary_restrictions
        )
        return result
    except Exception as e:
        # Log the full error with traceback
        logger.error(f"Error in generate_recipe: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
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
        "python_version": sys.version,
        "env_vars_available": list(os.environ.keys())
    } 