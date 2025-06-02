from pydantic import BaseModel
from typing import List, Dict, Optional

class RecipeRequest(BaseModel):
    ingredients: List[str]
    dietary_restrictions: List[str]
    user_id: Optional[str] = None

class Recipe(BaseModel):
    name: str
    instructions: str

class RecipeResponse(BaseModel):
    recipes: List[Recipe]
    meal_plan: Dict[str, str]
    grocery_list: List[str]

class FavoriteRequest(BaseModel):
    user_id: str
    recipe_id: str
    recipe_data: Recipe

class FavoriteResponse(BaseModel):
    status: str
    recipe: Optional[Dict] = None
    recipe_id: Optional[str] = None 