from lab3 import app, db
from flask import Flask, request, jsonify, abort
from datetime import datetime
from lab3.schem import user_schema, category_schema, record_schema, currency_schema
from lab3.model import User, Category, Record, Currency
import uuid
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError


with app.app_context():
    db.create_all()
    db.session.commit()


@app.route("/")
def start_page():
    return f"<a href='/healthcheck'>Lab3</a>"

@app.route("/healthcheck")
def healthcheck():
    otvet = jsonify(date=datetime.now(), status="OK")
    otvet.status_code = 200
    return otvet



@app.route('/user/<int:user_id>', methods=['GET', 'DELETE'])
def get_n_delete_user(user_id):
    with app.app_context():
        ch_user = User.query.get(user_id)

        if not ch_user:
            return jsonify({'ERROR': f'USER ID - {user_id} DONT EXIST'}), 404

        if request.method == "GET":
            user_dt = {
                'ID': ch_user.id,
                'USERNAME': ch_user.username,
                'CURRENCY': ch_user.currency_id_df
            }
            return jsonify(user_dt), 200

        elif request.method == "DELETE":
            db.session.delete(ch_user)
            db.session.commit()
            return jsonify({'MESSAGE': f'USER WITH ID - {user_id} DELETED'}), 200

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    userSchema = user_schema()
    try:
        user_dt = userSchema.load(data)
    except ValidationError as err:
        return jsonify({'ERROR': err.messages}), 400

    currency_id_df = data.get("currency_id_df")
    currency_df = Currency.query.filter_by(id=currency_id_df).first()

    if currency_id_df is None:
        currency_df = Currency.query.filter_by(name="DEFAULT CURR").first()
        if not currency_df:
            currency_df = Currency(name="DEFAULT CURR", symbol="GRIVNA")
            db.session.add(currency_df)
            db.session.commit()
            currency_df = Currency.query.filter_by(name="DEFAULT CURR").first()

    new_user = User(
        username=user_dt["username"],
        currency_id_df=currency_df.id
    )
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()

        user_resp = {
            'ID': new_user.id,
            'USERNAME': new_user.username,
            'CURRENCY': new_user.currency_df.symbol if new_user.currency_df else None
        }

        return jsonify(user_resp), 200

@app.route('/users', methods=['GET'])
def get_users():
    with app.app_context():
        users_dt = {
            user.id: {"USERNAME": user.username,
                      "CURRENCY": user.currency_id_df} for user in User.query.all()
        }
        return jsonify(users_dt)

@app.route('/category', methods=['POST', 'GET'])
def post_n_get_category():
    if request.method == 'GET':
        with app.app_context():
            category_dt = {
                category.id: {"NAME": category.name} for category in Category.query.all()
            }
            return jsonify(category_dt)

    elif request.method == 'POST':
        category_dt_req = request.get_json()
        category_sch = category_schema()
        try:
            category_dt = category_sch.load(category_dt_req)
        except ValidationError as err:
            return jsonify({'ERROR': err.messages}), 400

        new_category = Category(name=category_dt["name"])
        with app.app_context():
            db.session.add(new_category)
            db.session.commit()

            category_resp = {
                "ID": new_category.id,
                "NAME": new_category.name
            }

            return jsonify(category_resp), 200

@app.route('/category/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    with app.app_context():
        category_dt_req = Category.query.get(category_id)

        if not category_dt_req:
            return jsonify({'ERROR': f'CATEGORY ID - {category_id} DONT EXIST'}), 404

        db.session.delete(category_dt_req)
        db.session.commit()
        return jsonify({'MESSAGE': f'CATEGORY ID - {category_id} DELETED'}), 200

@app.route('/records', methods=['GET'])
def get_records():
    with app.app_context():
        record_dt = {
            "RECORD": [
                {
                    "ID": record.id,
                    "USER ID": record.user_id,
                    "CATEGORY ID": record.category_id,
                    "CURRENCY ID": record.currency_id,
                    "AMOUNT": record.amount,
                    "CREATED": record.created
                } for record in Record.query.all()
            ]
        }
        return jsonify(record_dt)


@app.route('/record', methods=['GET', 'POST'])
def get_n_post_records():
    if request.method == 'GET':
        user_id_req = request.args.get('user_id')
        category_id = request.args.get('category_id')
        if not user_id_req and not category_id:
            return jsonify({'ERROR': 'USER ID AND CATEGORY ID ARE REQUIREMENT'}), 400

        query = Record.query
        if user_id_req:
            query = query.filter_by(user_id=user_id_req)
        if category_id:
            query = query.filter_by(category_id=category_id)

        need_rec = query.all()
        print(need_rec)
        records_data = {
            record.id: {
                "USER ID": record.user_id,
                "CATEGORY ID": record.category_id,
                "CURRENCY ID": record.currency_id,
                "AMOUNT": record.amount,
                "CREATED": record.created
            } for record in need_rec
        }
        return jsonify(records_data)

    elif request.method == 'POST':
        record_dt_req = request.get_json()
        recordSchema = record_schema()
        try:
            record_data = recordSchema.load(record_dt_req)
        except ValidationError as err:
            return jsonify({'ERROR': err.messages}), 400

        user_id = record_data['user_id']
        user = User.query.get(user_id)

        if not user:
            return jsonify({'ERROR': 'USER NOT EXIST'}), 404
        currency_id = user.currency_id_df
        new_record = Record(
            user_id=user_id,
            category_id=record_data['category_id'],
            amount=record_data['amount'],
            currency_id=currency_id
        )
        with app.app_context():
            db.session.add(new_record)
            db.session.commit()

            record_response = {
                "ID": new_record.id,
                "USER ID": new_record.user_id,
                "CATEGORY ID": new_record.category_id,
                "CURRENCY ID": new_record.currency_id,
                "AMOUNT": new_record.amount
            }

            return jsonify(record_response), 200

@app.route('/record/<int:record_id>', methods=['GET', 'DELETE'])
def get_n_delete_record(record_id):
    with app.app_context():
        record_dt_req = Record.query.get(record_id)

        if not record_dt_req:
            return jsonify({"ERROR": f"RECORD ID - {record_id} DONT EXIST"}), 404

        if request.method == "GET":
            record_data = {
                "ID": record_dt_req.id,
                "USER ID": record_dt_req.user_id,
                "CATEGORY ID": record_dt_req.category_id,
                "CURRENCY ID": record_dt_req.currency_id,
                "AMOUNT": record_dt_req.amount,
                "CREATED": record_dt_req.created
            }
            return jsonify(record_data), 200

        elif request.method == "DELETE":
            db.session.delete(record_dt_req)
            db.session.commit()
            return jsonify({'MESSAGE': f'RECORD ID - {record_id} DELETED'}), 200

@app.route('/currency', methods=['POST', 'GET'])
def post_n_get_currency():
    if request.method == 'GET':
        with app.app_context():
            currencies_data = {
                currency.id: {"NAME": currency.name,
                              "SYMBOL": currency.symbol}
                for currency in Currency.query.all()
            }
            return jsonify(currencies_data)

    elif request.method == 'POST':
        currency_dt_req = request.get_json()
        currencySchema = currency_schema()
        try:
            currency_dt = currencySchema.load(currency_dt_req)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400

        new_currency = Currency(name=currency_dt["name"], symbol=currency_dt["symbol"])
        with app.app_context():
            db.session.add(new_currency)
            db.session.commit()

            currency_resp = {
                "ID": new_currency.id,
                "NAME": new_currency.name,
                "SYMBOL": new_currency.symbol
            }

            return jsonify(currency_resp), 200

@app.route('/currency/<int:currency_id>', methods=['DELETE'])
def delete_currency(currency_id):
    with app.app_context():
        currency_data_req = Currency.query.filter_by(id=currency_id).first()
        if currency_data_req:
            db.session.delete(currency_data_req)
            db.session.commit()
            return jsonify({'MESSAGE': f'CURRENCY ID - {currency_id} DELETED'}), 200
        else:
            return jsonify({'ERROR': f'CURRENCY ID - {currency_id} DONT EXIST'}), 404
