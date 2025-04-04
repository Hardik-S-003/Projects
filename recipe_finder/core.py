# core.py

import requests
import json
import logging
import pandas as pd
from config import API_KEY, BASE_URL

logging.basicConfig(level=logging.INFO, filename='logs/app.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')


def search_recipes(ingredients, cuisine=None, diet=None):
    """
    Searches for recipes based on ingredients and filters.

    Args:
        ingredients (str): Ingredients to search for.
        cuisine (str, optional): Cuisine type.
        diet (str, optional): Dietary restriction.

    Returns:
        dict: API response as a dictionary, or None on error.
    """
    try:
        url = f"{BASE_URL}/recipes/complexSearch?apiKey={API_KEY}&query={ingredients}"
        if cuisine:
            url += f"&cuisine={cuisine}"
        if diet:
            url += f"&diet={diet.lower().replace(' ', '%20')}"

        logging.info(f"API request: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"API request error: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return None


def get_recipe_details_with_nutrition(recipe_id):
    """
    Retrieves detailed information for a specific recipe, including comprehensive nutrition details.

    Args:
        recipe_id (int): The ID of the recipe.

    Returns:
        dict: API response with recipe details and detailed nutrition, or None on error.
    """
    try:
        url = f"{BASE_URL}/recipes/{recipe_id}/information?apiKey={API_KEY}&includeNutrition=true"  # Get detailed nutrition
        logging.info(f"API request: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"API request error: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return None


def analyze_nutrition(recipe_details):
    """
    Analyzes the nutritional information from recipe details.

    Args:
        recipe_details (dict): Recipe details from the API.

    Returns:
        pandas.DataFrame: DataFrame with nutritional information, or None on error.
    """
    try:
        if not recipe_details or 'nutrition' not in recipe_details or not recipe_details['nutrition']['nutrients']:
            logging.warning("Nutritional information not available or incomplete.")
            return None

        nutrition_data = recipe_details['nutrition']['nutrients']
        df_nutrition = pd.DataFrame(nutrition_data)
        return df_nutrition

    except KeyError as e:
        logging.error(f"Error extracting nutrition data: {e}")
        return None
    except TypeError as e:
        logging.error(f"Type error processing nutrition data: {e}")
        return None


if __name__ == '__main__':
    # Example usage and testing
    recipes = search_recipes(ingredients="chicken,rice", cuisine="Indian", diet="vegetarian")
    if recipes and recipes['results']:
        recipe_id = recipes['results'][0]['id']
        recipe_details = get_recipe_details_with_nutrition(recipe_id)  # Get detailed nutrition
        if recipe_details:
            nutrition_df = analyze_nutrition(recipe_details)
            if nutrition_df is not None:
                print(nutrition_df.head())
            else:
                print("Nutrition analysis failed or data not available.")
        else:
            print("Failed to fetch recipe details.")
    else:
        print("No recipes found.")