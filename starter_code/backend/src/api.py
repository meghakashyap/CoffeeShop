import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db, db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
# from models import db, db_drop_and_create_all, setup_db, Drink

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"/*": {"origins": "*"}})


#  uncomment the following line to initialize the datbase
# with app.app_context():
#     db_drop_and_create_all()

# ROUTES

# This endpoint will get the list of drinks
@app.route("/drinks", methods=["GET"])
def get_drinks():
    try:
        drinks = Drink.query.all()
        drinks_short = [drink.short() for drink in drinks] 
        return jsonify(
            {"success": True, "drinks": drinks_short}
            ,200)
    except Exception as e:
        print(f"Error fetching drinks: {e}")
        abort(500)
    


# This endpoint  will show the drinks details
@requires_auth('get:drinks-detail')
@app.route("/drinks-detail",methods=["GET"])
def get_drinks_detail():
    try:
        drinks = Drink.query.all()
        drinks_long = [drink.long() for drink in drinks] 
        return jsonify (
            {"success": True, "drinks": drinks_long}
            ,200)
    except Exception as e:
        print(f"Error fetching drinks: {e}")
        abort(500)
    
        

# An endpoint to add a new drink
@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def add_drinks(payload):
    body = request.get_json()
    
    if not body:
        abort(400, description=" Request doesn't contain required json body")
    
    new_title = body.get('title')
    new_recipe = body.get('recipe')
    
    if  'title' not in body or 'recipe' not in body:
        abort(400, description="Title and recipe are required fields !")
    try:
        drink= Drink(
            title = new_title,
            recipe = json.dumps([new_recipe])
        )
        drink.insert()
        
        return jsonify(
            {"success": True, "drinks": [drink.long()]}
        ,200)
        
    except Exception as e:
        print(f"Error creating drink: {e}")
        abort(500, description="An error occurred while creating the drink")

# An endpoint to update a specific drink
@app.route("/drinks/<int:id>",methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drinks(payload, id):
    body = request.get_json()
   
    if 'title' not in  body:
        abort(404, description="Title is missing")
    
    if not body:
        abort(400, description=" Request doesn't contain required json body")
   
    try:
        new_title = body.get('title')
        recipe = body.get('recipe')
        drink = Drink.query.filter(Drink.id==id).one_or_none()
        drink.title = new_title
        drink.update()
      
    except Exception as e:
        print(e)
        abort(404)

    return jsonify({"success": True, "drinks": [drink.long()]})


# An endpoint to delete the drinks
@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id==id).one_or_none()
    
    if id is None or drink is None:
        abort(404, description=" Request doesn't contain required drink id")
    
    try:
        drink.delete()
        
        return jsonify({
                "success":True,
                "id": id
            },200)
        
    except Exception as e:
        print(f"Error deleting drink: {e}")
        abort(500, description="An error occurred deleting creating the drink")
        
    

# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(400)
def bad_request(error):
        return ( 
            jsonify({
            "success":False,
            "error": 400,
            "message":"Bad Request",
        }),400,
        )
        
@app.errorhandler(401)
def not_found(error):
    return (
        jsonify({
            "success": False, 
            "error": 401,
            "message": "Not authorized"
            }),401,
    )        

@app.errorhandler(404)
def not_found(error):
        return ( 
            jsonify({
            "success":False,
            "error": 404,
            "message":"Not Found",
        }),404,
        )
        
@app.errorhandler(500)
def internal_server_error(error):
    return ( 
        jsonify({
        "success":False,
        "error": 500,
        "message":"Internal Server Error ",
    }),500,
    )       
    
    
@app.errorhandler(AuthError)
def auth_error(e):
    return (
        jsonify({
            "success": False,
            "error": e.status_code, 
            "message": e.error}),
        e.status_code,
    )
    
if __name__ == "__main__":
    app.run( debug=True)