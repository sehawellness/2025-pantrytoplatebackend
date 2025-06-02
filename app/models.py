from pydantic import BaseModel
from typing import List

class RecipeRequest(BaseModel):
    ingredients: List[str]
    dietary_restrictions: List[str]

class RecipeResponse(BaseModel):
    recipes: List[dict]
    meal_plan: dict
    grocery_list: List[str] 