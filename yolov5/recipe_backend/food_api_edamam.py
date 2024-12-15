import requests

# cooking steps only in url, not in response
# only allow vague
url = "https://api.edamam.com/api/recipes/v2"
ingredients = "chicken, fish"
count = len(ingredients.split(','))
count_range = str(count) + '-' + str(count+1)
params = {
    "type": "public",
    "app_id": "4868bc46",
    "app_key": "b2e9b8dd1ce3927798b17d3ff547df6d",
    "q": ingredients,
    "ingr": count_range,  # "5-6"
    "imageSize": ["SMALL", "REGULAR"],
    "excluded": ["beef"],
    "random": False,
    "time": "10-40",
    "imageSize": "SMALL",
    "random": "false",
    "field": ["ingredients", "totalTime"]
}
headers = {
    "accept": "application/json",
    "Accept-Language": "en"
}

response = requests.get(url, headers=headers, params=params)

# Output the response, e.g., print the JSON content if response is successful
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Error:", response.status_code, response.text)