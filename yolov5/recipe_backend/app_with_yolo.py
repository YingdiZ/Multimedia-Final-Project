import json
import base64
from flask import Flask, request, jsonify
import io
import os
from api_spoonacular import SpoonacularAPI
from flask_cors import CORS
from flask import Flask, request, jsonify
from pathlib import Path
import sys

yolov5_dict = os.path.dirname(os.path.realpath(__file__))[:-15]
print(yolov5_dict)

sys.path.append(yolov5_dict)  # change to YOLOv5 root directory
print( sys.path)

from detect2 import run
# from pathlib import Path
# import sys
# yolov5_dict = 'D:\MSc_assignments\MultimediaSystem\final_project\FoodRec\yolov5'
# sys.path.append(yolov5_dict)  # change to YOLOv5 root directory


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    file = request.files.get('image')
    image_id = request.form.get('image_id')

    app.logger.info(f"image_id{image_id}")

    if file and image_id:
        file_extension = os.path.splitext(file.filename)[1]
        folder_path = os.path.join(yolov5_dict, r'recipe_backend\uploads\photos', f"{image_id}")
        file_path = folder_path + f"/{image_id}{file_extension}"
        result_folder_path = os.path.join(yolov5_dict, r'recipe_backend\results\photos', f"{image_id}")
        pt_path = os.path.join(yolov5_dict, 'best.pt')


        try:
            os.makedirs(folder_path, exist_ok=True)
            os.makedirs(result_folder_path, exist_ok=True)
            file.save(file_path)
            print(f"run(weights='{pt_path}', source='{folder_path}', project='{result_folder_path}')")
            app.logger.info('start run yolo best')
            run(weights=pt_path, source=folder_path, project=result_folder_path)  # best.pt is the trained model
            return jsonify({'message': 'success'}), 200
        except Exception as e:
            app.logger.info(f'exception:{e}')
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
    else:
        app.logger.info(f"image_id{image_id}")

        return jsonify({'error': 'Missing image or image_id'}), 400


@app.route('/api/get_ingredients_results', methods=['GET'])
def get_ingredients_results():
    image_id = request.args.get('image_id')
    app.logger.info(f'image_id:{image_id}')


    if not image_id:
        return jsonify({"error": "Missing 'image_id' in request."}), 400

    try:
        # load and return ingredients
        # with open('./results/ingredients.json', 'r') as f:
        ingredients_path = os.path.join(yolov5_dict, r"recipe_backend\results\ingredients.json")
        #3 ingredients_path2 = r"D:\MSc_assignments\MultimediaSystem\final_project\Multimedia_Final_Project\yolov5\recipe_backend\results\ingredients.json"
        app.logger.info(ingredients_path)
        # app.logger.info(ingredients_path2)
        with open(ingredients_path, 'r') as f:
            
            app.logger.info(ingredients_path)
            ingredients_all = json.load(f)

        if image_id not in ingredients_all:
            return jsonify({"error": f"Ingredients for image_id '{image_id}' not found."}), 404

        ingredients = ingredients_all[image_id]


        ingredients_new = list(set(ingredients))

        # load and return photo
        # photo_dir = os.path.join('./results/photos/', image_id, 'exp')
        # app.logger.info(f'photo_dir:{photo_dir}')
        # photo_dir = os.path.join(r"D:\MSc_assignments\MultimediaSystem\final_project\FoodRec\yolov5\recipe_backend\results\photos", image_id, 'exp')
        photo_dir = os.path.join(yolov5_dict, r"recipe_backend\results\photos", image_id, 'exp')
        app.logger.info(f"photo_dir:{photo_dir}")


        photo_file_path = None

        for file_name in os.listdir(photo_dir):
            app.logger.info(f'found image file')
            if os.path.splitext(file_name)[0] == image_id:
                app.logger.info(f'found image file 2')
                photo_file_path = os.path.join(photo_dir, file_name)
                break

        if not photo_file_path:
            app.logger.info(f'not found image file')
            return jsonify({"error": f"No file found in 'photo' directory for image_id '{image_id}'."}), 404

        with open(photo_file_path, 'rb') as photo_file:
            app.logger.info(f'open image file')
            photo_content = base64.b64encode(photo_file.read()).decode('utf-8')

    except FileNotFoundError:
        return jsonify({"error": "Ingredients file not found."}), 500

    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode ingredients JSON file."}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    rsp = {
        "message": "success",
        "ingredients": ingredients_new,
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
    app.logger.info(f'ingredients_list:{ingredients_list}')
    if not ingredients_list:
        return jsonify({"error": "Ingredients not provided."}), 400

    ingredients = ", ".join(ingredients_list)

    api_client = SpoonacularAPI(api_key="9d250a5f87a1466990729cb0f178ed69")

    recipes = api_client.find_by_ingredients(ingredients=ingredients, number=1)
    app.logger.info(f'recipes:{recipes}')


    if not recipes:
        return jsonify({"error": "Failed to retrieve recipes. Please check the ingredients and try again."}), 500

    try:
        recipe_one_id = recipes[0]["id"]
        
    except IndexError:
        return jsonify({"error": "No recipes found for the provided ingredients."}), 404

    try:
        recipe_info = api_client.get_recipe_information(recipe_one_id)
        app.logger.info(f'recipe_info:{recipe_info}')
    except Exception as e:
        app.logger.info(f'e:{e}')

    if not recipe_info:
        return jsonify({"error": "Failed to retrieve recipe information."}), 500

    ingredients_missed = [ingre['name'] for ingre in recipes[0].get('missedIngredients', [])]
    ingredients_used = [ingre['name'] for ingre in recipes[0].get('usedIngredients', [])]
    ingredients_unused = [ingre['name'] for ingre in recipes[0].get('unusedIngredients', [])]

    ingredients_results = ingredients_missed + ingredients_used
    app.logger.info(f'ingredients_results:{ingredients_results}')

    steps = recipe_info['analyzedInstructions'][0]['steps']
    if not steps:
        return jsonify({"error": "No cooking steps found for the recipe."}), 404

    recipe_rsp = [{
        'name': recipes[0].get('title', 'No title available'),
        'ingredients': ingredients_results,
        'steps': steps
    }]
    app.logger.info(f'recipe_rsp:{recipe_rsp}')
    return jsonify({"recipes":recipe_rsp}), 200


if __name__ == '__main__':
    app.run(debug=True)
