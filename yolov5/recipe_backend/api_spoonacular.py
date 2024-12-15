import requests


class SpoonacularAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.spoonacular.com/recipes"

    def find_by_ingredients(self, ingredients, number=1):
        """
        Finds recipes based on ingredients.
        """
        url = f"{self.base_url}/findByIngredients"
        params = {
            "apiKey": self.api_key,
            "ingredients": ingredients,
            "number": number
        }
        headers = {"Content-Type": "application/json"}

        # Make the GET request
        response = requests.get(url, headers=headers, params=params)

        # Check the response status
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch recipes: {response.status_code}, {response.text}")

    def get_recipe_information(self, recipe_id, include_nutrition=False, add_wine_pairing=False, add_taste_data=True):
        """
        Fetches detailed recipe information by recipe ID.
        """
        url = f"{self.base_url}/{recipe_id}/information"
        params = {
            "apiKey": self.api_key,
            "includeNutrition": include_nutrition,
            "addWinePairing": add_wine_pairing,
            "addTasteData": add_taste_data
        }
        headers = {"Content-Type": "application/json"}

        # Make the GET request
        response = requests.get(url, headers=headers, params=params)

        # Check the response status
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch recipe information: {response.status_code}, {response.text}")