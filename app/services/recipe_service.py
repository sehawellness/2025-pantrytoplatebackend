import os
import httpx
import json
import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class RecipeService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://104.22.48.189/api/v1/chat/completions"
        
    async def generate_recipes(self, ingredients: List[str], dietary_restrictions: List[str]) -> Dict:
        if not self.api_key:
            logger.error("OpenRouter API key not found in environment variables")
            raise Exception("OpenRouter API key not found in environment variables")
            
        prompt = self._create_prompt(ingredients, dietary_restrictions)
        logger.info(f"Created prompt for ingredients: {ingredients}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://pantrytoplate-api.onrender.com",
            "Content-Type": "application/json",
            "Host": "openrouter.ai"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful cooking assistant that creates recipes and meal plans. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            logger.info(f"Making request to OpenRouter API")
            logger.info(f"URL: {self.api_url}")
            logger.info(f"Headers: {json.dumps({k: v for k, v in headers.items() if k != 'Authorization'})}")
            logger.info(f"Payload: {json.dumps(payload)}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        follow_redirects=True
                    )
                    
                    logger.info(f"Response status code: {response.status_code}")
                    logger.info(f"Response headers: {dict(response.headers)}")
                    
                    response_text = response.text
                    logger.info(f"Raw response text: {response_text}")
                    
                    if not response_text:
                        logger.error("Empty response received from API")
                        raise Exception("Empty response received from API")
                        
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            logger.info(f"Parsed response JSON: {json.dumps(result)}")
                            
                            # Extract the content from the API response
                            content = result['choices'][0]['message']['content']
                            logger.info(f"Extracted content: {content}")
                            
                            # Parse the content as JSON
                            try:
                                recipes_data = json.loads(content)
                                logger.info(f"Successfully parsed recipe data: {json.dumps(recipes_data)}")
                                return recipes_data
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse recipe content as JSON: {str(e)}")
                                # Try to extract JSON from the content if it's wrapped in markdown
                                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                                if json_match:
                                    return json.loads(json_match.group(1))
                                raise Exception(f"Failed to parse recipe data as JSON")
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse successful response as JSON: {str(e)}")
                            logger.error(f"Response content: {response_text}")
                            raise Exception(f"Invalid JSON in successful response: {str(e)}")
                    else:
                        try:
                            error_detail = response.json() if response.content else response.text
                            logger.error(f"API call failed with status {response.status_code}: {error_detail}")
                            raise Exception(f"API call failed with status {response.status_code}: {error_detail}")
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse error response. Status: {response.status_code}, Content: {response.text}")
                            raise Exception(f"API call failed with status {response.status_code} and unparseable response")
                            
                except httpx.RequestError as e:
                    logger.error(f"Request failed: {str(e)}")
                    raise Exception(f"Request failed: {str(e)}")
                    
        except httpx.TimeoutException:
            logger.error("Request to OpenRouter API timed out")
            raise Exception("Request to OpenRouter API timed out")
        except Exception as e:
            logger.error(f"Unexpected error calling OpenRouter API: {str(e)}")
            raise Exception(f"Error calling OpenRouter API: {str(e)}")
    
    def _create_prompt(self, ingredients: List[str], dietary_restrictions: List[str]) -> str:
        return f"""Given these ingredients: {', '.join(ingredients)}
        and dietary restrictions: {', '.join(dietary_restrictions)},
        please provide:
        1. 3 possible recipes that can be made
        2. A weekly meal plan
        3. A grocery shopping list
        
        Respond with ONLY a JSON object containing these keys:
        - recipes: array of objects, each with 'name' and 'instructions'
        - meal_plan: object with days of the week as keys
        - grocery_list: array of strings
        
        Example format:
        {{
            "recipes": [
                {{
                    "name": "Recipe Name",
                    "instructions": "Step by step instructions"
                }}
            ],
            "meal_plan": {{
                "Monday": "Recipe Name",
                "Tuesday": "Another Recipe"
            }},
            "grocery_list": ["item 1", "item 2"]
        }}
        
        Ensure the response is a valid JSON object without any markdown formatting or code blocks."""
    
    def _parse_response(self, content: str) -> Dict:
        try:
            # First, try to parse as-is
            logger.info("Attempting to parse API response as JSON")
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                logger.info("Initial JSON parsing failed, trying to extract JSON from response")
                # Try to extract JSON from markdown code blocks
                json_match = re.search(r'```(?:json)?\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    logger.info("Found JSON in code block")
                    return json.loads(json_match.group(1))
                
                # If no code blocks, try to find just the JSON object
                json_match = re.search(r'({.*})', content, re.DOTALL)
                if json_match:
                    logger.info("Found JSON object in content")
                    return json.loads(json_match.group(1))
                
                logger.error("Could not find valid JSON in response")
                raise Exception("Could not find valid JSON in response")
            except Exception as e:
                logger.error(f"Failed to parse API response: {str(e)}")
                logger.error(f"Raw content: {content}")
                raise Exception(f"Failed to parse API response: {str(e)}, Content: {content}") 