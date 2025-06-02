from fastapi import FastAPI, HTTPException
from .models import RecipeRequest, RecipeResponse
from .services.recipe_service import RecipeService
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="PantryToPlate API")
recipe_service = RecipeService()

@app.post("/generate-recipe", response_model=RecipeResponse)
async def generate_recipe(request: RecipeRequest):
    try:
        # Debug: Print API key presence (not the actual key)
        api_key_exists = "OPENROUTER_API_KEY" in os.environ
        print(f"API key exists: {api_key_exists}")
        
        result = await recipe_service.generate_recipes(
            request.ingredients,
            request.dietary_restrictions
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/debug-env")
async def debug_env():
    """Debug endpoint to check environment variables (without exposing sensitive data)"""
    return {
        "api_key_exists": "OPENROUTER_API_KEY" in os.environ,
        "api_key_length": len(os.getenv("OPENROUTER_API_KEY", "")) if "OPENROUTER_API_KEY" in os.environ else 0
    } 