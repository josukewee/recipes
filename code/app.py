from flask import Flask, request, render_template, url_for, redirect, flash, make_response
import pymongo 
from forms import Recipe
from bson import json_util, ObjectId
import os
import random
import string


myclient = pymongo.MongoClient("mongodb://admin:admin@mongodb:27017/")
db = myclient["mydatabase"]
recipes = db["recipes"]



# print(recipes.find_one({'name': 'Parek na sucho'}))

# sesradil jsem kolekce podle atributu "name", sestupne
# mydoc = recipes.find().sort("name", 1)
# print(mydoc, type(mydoc))

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/recipes")
def recipes_page():
    recipes_list = recipes.find()
    return render_template("recipes.html", recipes_list=recipes_list)
    
@app.route("/add_recipe", methods = ['POST', 'GET'])
def add_recipe():
    form = Recipe()
    if request.method == "POST":
        name = request.form.get('name')
        author = request.form.get('author')
        description = request.form.get('description')
        secret = ''.join(random.choices(string.ascii_lowercase + string.digits + string.punctuation, k=8))
        record = {'name': name, 'author': author, 'description': description, 'secret': secret}
        recipes.insert_one(record)
        flash(f"You have recorded your recipe successfully. Secret {secret}", "info")
        return redirect(url_for('add_recipe'))  
    else:
        return render_template("add_recipe.html", form = form)

@app.route('/api/recipe', methods=['POST'])
def api_post_recipe():
    name = request.args.get('name')
    author = request.args.get('author')
    description = request.args.get('description')
    secret = "".join(random.sample(string.ascii_letters + string.digits + string.punctuation, 8))
    record = {'name': name, 'author': author, 'description': description, "secret": secret}
    if recipes.find_one({'name': name, "author": author}) == None:
        recipes.insert_one(record)
        return make_response(json_util.dumps({'success': 'Recipe added', "secret": secret}), 200)
    else:
        return make_response(json_util.dumps({'error': 'Recipe already exists'}), 400)

@app.route('/api/recipe', methods=["GET"])
def api_get_recipe():
    result = recipes.find()
    if result == None:
        return make_response(json_util.dump({'fail': 'This recipes is not found'}), 400)
    else:
        return make_response(json_util.dumps(result), 200)

@app.route('/api/recipe/<id>', methods=["GET"])
def api_get_one_recipe(id):
    object_id = ObjectId(id)
    record = recipes.find_one({"_id": object_id})
    return make_response(json_util.dumps(record))

@app.route('/api/recipe/<id>', methods=["DELETE"])
def api_delete_recipe(id):
    object_id = ObjectId(id)
    record = recipes.find_one({"_id": object_id})
    secret = request.json.get('secret')
    if not record:
        return make_response(json_util.dumps({"error": "Record is not found"}), 400)
    else:
        recipes.delete_one({"_id": object_id, "secret": secret})
        return make_response(json_util.dumps({'success': 'Recipe is deleted'}), 200)
        
@app.route('/api/recipe/<id>', methods=["PUT"])
def api_update_recipe(id):
    object_id = ObjectId(id)
    record = recipes.find_one({"_id": object_id})
    if not record:
        return make_response(json_util.dumps({"error": "Record is not found"}), 400)
    else:
        name = request.json.get('name')
        author = request.json.get('author')
        description = request.json.get('description')
        if not (name and author and description):
            return make_response(json_util.dumps({"error": "Invalid request. Name, author, and description are required."}), 400)
        result = recipes.update_one({'_id': object_id}, {"$set": {'name': name, "author": author, "description": description}})
        if result.modified_count > 0:
            return make_response(json_util.dumps({'success': 'Recipe is changed'}), 200)
        else:
            return make_response(json_util.dumps({'fail': 'Recipe is not found or no changes were made'}), 404)


if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port=5000) 