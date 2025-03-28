import requests
import json
import logging
from config import api_config


def search_recipes(ingredients, cuisine=None, diet=None):
    """
    Searches for recipes based on ingredients and filters.

    ingredients (str): Ingredients to search for (e.g., "chicken, pasta").
    cuisine (str, optional): Cuisine type (e.g., "Italian", "Mexican"). Defaults to None.
    diet (str, optional): Dietary restriction (e.g., "vegetarian", "vegan"). Defaults to None.

    """
    try:
        base_url = api_config.BASE_URL  
        api_key = api_config.API_KEY    

        url = f"{base_url}/recipes/complexSearch?apiKey={api_key}&ingredients={ingredients}"

        # Add optional parameters
        if cuisine:
            url += f"&cuisine={cuisine}"
        if diet:
            url += f"&diet={diet}"

        logging.info(f"API request: {url}")  # Log the API request

        response = requests.get(url)
        response.raise_for_status()  # Raising exception for bad ststus code

        data = response.json()
        logging.info(f"API response: {data}")  # Log the API response

        return data

    except requests.exceptions.RequestException as e:
        logging.error(f"API request error: {e}")
        return None  

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        return None

def get_recipe_details(recipe_id):
    """
    Retrieves detailed information for a specific recipe.

    recipe_id : The ID of the recipe to retrieve.

    """
    try:
        base_url = api_config.BASE_URL  
        api_key = api_config.API_KEY  

        url = f"{base_url}/recipes/{recipe_id}/information?apiKey={api_key}"

        logging.info(f"API request: {url}")

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        logging.info(f"API response: {data}")
        return data

    except requests.exceptions.RequestException as e:
        logging.error(f"API request error: {e}")
        return None

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        return None


if __name__ == '__main__':
    recipes = search_recipes(ingredients="pasta, tomatoes", cuisine="Italian")
    if recipes and recipes['results']:
        first_recipe_id = recipes['results'][0]['id']
        recipe_details = get_recipe_details(first_recipe_id)
        if recipe_details:
            print(json.dumps(recipe_details, indent=4))  # Pretty print for readability
