from lab2 import app
from flask import Flask, request, jsonify
from faker import Faker
from datetime import datetime
import uuid




users = {}
categories = {}
records = {}


@app.route("/")
def start_page():
    return f"<a href='/healthcheck'>Lab2</a>"

@app.route("/healthcheck")
def healthcheck():
    otvet = jsonify(date=datetime.now(), status="OK")
    otvet.status_code = 200
    return otvet

@app.route('/user/<userID>', methods=['GET', 'DELETE'])
def get_n_delete_user(userID):
    if request.method == "GET":
        user = users.get(userID)
        if not user:
            return jsonify({"ERROR": "USER WITH THIS ID NOT FOUND"}), 404
        return jsonify(user)
    elif request.method == "DELETE":
        user = users.pop(userID, None)
        if not user:
            return jsonify({"ERROR": "USER WITH THIS ID NOT FOUND"}), 404
        return jsonify(user)

@app.route('/user', methods=['POST'])
def create_user():
    user_data = request.get_json()
    if "username" not in user_data:
        return jsonify({"ERROR": "username IS REQUIRED"}), 400
    userID = uuid.uuid4().hex
    user = {"id": userID, **user_data}
    users[userID] = user
    return jsonify(user)

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(list(users.values()))


@app.route('/category', methods=['GET', 'POST', 'DELETE'])
def get_n_post_n_delete_categories():
    if request.method == "GET":
        return jsonify(list(categories.values()))
    elif request.method == "POST":
        category_data = request.get_json()
        if "name" not in category_data:
            return jsonify({"ERROR": "name IS REQUIRED"}), 400
        categoryID = uuid.uuid4().hex
        category = {"id": categoryID, **category_data}
        categories[categoryID] = category
        return jsonify(category)
    elif request.method == "DELETE":
        categoryID = request.args.get('id')
        if categoryID:
            category = categories.pop(categoryID, None)
            if not category:
                return jsonify({"ERROR": f"CATEGORY ID - {categoryID} NOT FINDED"}), 404
            return jsonify(category)
        else:
            categories.clear()
            return jsonify({"MESSAGE": "ALL CATEGORIES DELETED"})


@app.route('/record/<recordID>', methods=['GET', 'DELETE'])
def get_n_delete_record(recordID):
    if request.method == "GET":
        record = records.get(recordID)
        if not record:
            return jsonify({"ERROR": "RECORD DONT EXIST"}), 404
        return jsonify(record)
    elif request.method == "DELETE":
        record = records.pop(recordID, None)
        if not record:
            return jsonify({"ERROR": "RECORD DONT EXIST"}), 404
        return jsonify(record)


@app.route('/record', methods=['POST', 'GET'])
def create_n_get_record():
    if request.method == "POST":
        record_data = request.get_json()
        userID = record_data.get('userID')
        categoryID = record_data.get('categoryID')

        if not userID or not categoryID:
            return jsonify({"ERROR": "USER_ID AND CATEGORY_ID ARE REQUIRE"}), 400
        if userID not in users:
            return jsonify({"ERROR": f"USER ID - {userID} NOT EXIST"}), 404
        if categoryID not in categories:
            return jsonify({"ERROR": f"CATEGORY ID - {categoryID} NOT EXIST"}), 404

        recordID = uuid.uuid4().hex
        record = {"id": recordID, **record_data}
        records[recordID] = record
        return jsonify(record)
    elif request.method == "GET":
        userID = request.args.get('userID')
        categoryID = request.args.get('categoryID')
        if not userID and not categoryID:
            return jsonify({"ERROR": "USER_ID AND CATEGORY_ID ARE REQUIRE"}), 400
        filtered_records = [
            r for r in records.values() if (not userID or r['userID'] == userID) or (not categoryID or r['categoryID'] == categoryID)
        ]
        return jsonify(filtered_records)

