import json
import base64
from flask import Flask, request, jsonify
import io
import os
from api_spoonacular import SpoonacularAPI
from flask_cors import CORS

import os
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    file = request.files.get('image')
    image_id = request.args.get('image_id')

    if file and image_id:
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join('./uploads/photos', f"{image_id}{file_extension}")

        try:
            file.save(file_path)
            return jsonify({'message': 'success'}), 200
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Missing image or image_id'}), 400


@app.route('/api/get_ingredients_results', methods=['GET'])
def get_ingredients_results():
    image_id = request.args.get('image_id')

    if not image_id:
        return jsonify({"error": "Missing 'image_id' in request."}), 400

    try:
        # load and return ingredients
        with open('./results/ingredients.json', 'r') as f:
            ingredients_all = json.load(f)

        if image_id not in ingredients_all:
            return jsonify({"error": f"Ingredients for image_id '{image_id}' not found."}), 404

        ingredients = ingredients_all[image_id]

        # load and return photo
        photo_dir = './results/photos/'
        photo_file_path = None

        for file_name in os.listdir(photo_dir):
            if os.path.splitext(file_name)[0] == image_id:
                photo_file_path = os.path.join(photo_dir, file_name)
                break

        if not photo_file_path:
            return jsonify({"error": f"No file found in 'photo' directory for image_id '{image_id}'."}), 404

        with open(photo_file_path, 'rb') as photo_file:
            photo_content = base64.b64encode(photo_file.read()).decode('utf-8')

    except FileNotFoundError:
        return jsonify({"error": "Ingredients file not found."}), 500

    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode ingredients JSON file."}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    rsp = {
        "message": "success",
        "ingredients": ingredients,
        "photo_file": photo_content
    }
    return jsonify(rsp), 200


@app.route('/api/get_recipe_results', methods=['POST'])
def get_recipe_results():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided."}), 400
    except Exception as e:
        return jsonify({"error": "Invalid JSON format."}), 400

    ingredients_list = data.get('ingredients', [])
    if not ingredients_list:
        return jsonify({"error": "Ingredients not provided."}), 400

    ingredients = ", ".join(ingredients_list)

    api_client = SpoonacularAPI(api_key="9d250a5f87a1466990729cb0f178ed69")

    recipes = api_client.find_by_ingredients(ingredients=ingredients, number=1)

    if not recipes:
        return jsonify({"error": "Failed to retrieve recipes. Please check the ingredients and try again."}), 500

    try:
        recipe_one_id = recipes[0]["id"]
    except IndexError:
        return jsonify({"error": "No recipes found for the provided ingredients."}), 404

    recipe_info = api_client.get_recipe_information(recipe_one_id)

    if not recipe_info:
        return jsonify({"error": "Failed to retrieve recipe information."}), 500

    ingredients_missed = [ingre['name'] for ingre in recipes[0].get('missedIngredients', [])]
    ingredients_used = [ingre['name'] for ingre in recipes[0].get('usedIngredients', [])]
    ingredients_unused = [ingre['name'] for ingre in recipes[0].get('unusedIngredients', [])]

    ingredients_results = ingredients_missed + ingredients_used

    steps = recipe_info['analyzedInstructions'][0]['steps']
    if not steps:
        return jsonify({"error": "No cooking steps found for the recipe."}), 404

    recipe_rsp = [{
        'name': recipes[0].get('title', 'No title available'),
        'ingredients': ingredients_results,
        'steps': steps
    }]

    return jsonify({"recipes":recipe_rsp}), 200


if __name__ == '__main__':
    app.run(debug=True)
