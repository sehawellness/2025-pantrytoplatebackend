from fastapi import FastAPI, HTTPException
from .models import RecipeRequest, RecipeResponse
from .services.recipe_service import RecipeService
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PantryToPlate API")
recipe_service = RecipeService()

@app.post("/generate-recipe", response_model=RecipeResponse)
async def generate_recipe(request: RecipeRequest):
    try:
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