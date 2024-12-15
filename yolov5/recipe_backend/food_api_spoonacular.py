import requests

# https://spoonacular.com/food-api/docs#Get-Recipe-Information
# cooking steps: in instructions
# return missedIngredients
url = "https://api.spoonacular.com/recipes/findByIngredients"
params = {
    "apiKey": "9d250a5f87a1466990729cb0f178ed69",
    "ingredients": "chicken, tomato",
    "number": 2
}

# Set the headers
headers = {
    "Content-Type": "application/json"
}

# Make the GET request
response = requests.get(url, headers=headers, params=params)

# Check the response status
if response.status_code == 200:
    recipes = response.json()  # Parse JSON response
    recipe_one_id = recipes[0]["id"]
    print(recipes)  # Print or process the recipes as needed
else:
    print(f"Request failed with status code {response.status_code}")


print("-"*30)

url = f"https://api.spoonacular.com/recipes/{recipe_one_id}/information"
params = {
    "apiKey": "9d250a5f87a1466990729cb0f178ed69",
    "includeNutrition": False,
    "addWinePairing": False,
    "addTasteData": True
}

# Set the headers
headers = {
    "Content-Type": "application/json"
}

# Make the GET request
response = requests.get(url, headers=headers, params=params)

# Check the response status
if response.status_code == 200:
    recipes = response.json()  # Parse JSON response
    print(recipes)  # Print or process the recipes as needed
else:
    print(f"Request failed with status code {response.status_code}")