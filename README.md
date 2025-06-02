# PantryToPlate Backend

A FastAPI backend service that generates recipes, meal plans, and grocery lists based on available ingredients and dietary restrictions using the Mistral AI model via OpenRouter.

## Setup

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with:
```
OPENROUTER_API_KEY=your_api_key_here
```

## Local Development

Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /generate-recipe
Generate recipes, meal plans, and grocery lists based on ingredients and dietary restrictions.

Request body:
```json
{
    "ingredients": ["chicken", "rice", "tomatoes"],
    "dietary_restrictions": ["gluten-free"]
}
```

### GET /health
Health check endpoint.

## Deployment on Render

1. Sign up for Render (https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure the following:
   - Environment: Docker
   - Build Command: (leave empty, using Dockerfile)
   - Start Command: (leave empty, using Dockerfile)
5. Add Environment Variables:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - `PORT`: 8000

## Important Notes

- Get your OpenRouter API key from https://openrouter.ai/
- Update the HTTP-Referer in `app/services/recipe_service.py` with your Render domain
- The free tier of Render may have cold starts 