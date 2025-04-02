import requests
import json
import logging
import pandas as pd
from config import API_KEY, BASE_URL  

logging.basicConfig(level=logging.INFO, filename='/workspace/Projects/recipe_finder/logs/app.log', format='%(asctime)s - %(levelname)s - %(message)s')

def search_recipes(ingredients, cuisine=None, diet=None):
    """
    Searches for recipes based on ingredients and filters.
        ingredients (str): Ingredients to search for.
        cuisine (str, optional): Cuisine type.
        diet (str, optional): Dietary restriction.
    """
    try:
        url = f"{BASE_URL}/recipes/complexSearch?apiKey={API_KEY}&ingredients={ingredients}"
        if cuisine:
            url += f"&cuisine={cuisine}"
        if diet:
            url += f"&diet={diet}"

        logging.info(f"API request: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"API request error: {e}")
        return None

def get_recipe_details(recipe_id):
    """
    Retrieves detailed information for a specific recipe.
        recipe_id (int): The ID of the recipe.
    """
    try:
        url = f"{BASE_URL}/recipes/{recipe_id}/information?apiKey={API_KEY}"
        logging.info(f"API request: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"API request error: {e}")
        return None

def analyze_nutrition(recipe_details):
    """
    Analyzes the nutritional information from recipe details.
        recipe_details (dict): Recipe details from the API.
    """
    try:
        if not recipe_details or 'nutrition' not in recipe_details:
            logging.warning("Nutritional information not available.")
            return None

        nutrition_data = recipe_details['nutrition']['nutrients']
        df_nutrition = pd.DataFrame(nutrition_data)
        return df_nutrition

    except KeyError as e:
        logging.error(f"Error extracting nutrition data: {e}")
        return None

if __name__ == '__main__':
    recipes = search_recipes(ingredients="chicken,rice", cuisine="Indian")
    if recipes and recipes['results']:
        recipe_id = recipes['results'][0]['id']
        recipe_details = get_recipe_details(recipe_id)
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