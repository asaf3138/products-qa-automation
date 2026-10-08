import random
from services.product_service import ProductNotFoundServiceError, ProductServiceError

from flask import Flask, request, jsonify, render_template
from models.models import Product
from services import product_service
import db.init_db as db
import time

db.create_db()
db.create_table()
time.sleep(3)
app = Flask(__name__)


# http://127.0.0.1:5000
@app.route('/other/home')
def other_home():
    return render_template('/other_website/home.html')


@app.route('/other/next')
def other_next():
    return render_template('/other_website/nextpage.html')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/products', methods=['GET'])
def get_all():
    products = product_service.get_all_products()
    return jsonify([p.__dict__ for p in products])


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_one(product_id):
    try:
        product = product_service.get_product(product_id)
        return jsonify(product.__dict__)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except ProductNotFoundServiceError as e:
        err_message = str(e)
        return jsonify({"error": err_message}), 404


@app.route('/api/products', methods=['POST'])
def create():
    data = request.get_json()
    try:
        new_product = Product(
            product_id=0,
            name=data['name'],
            price=float(data['price']),
            image=data['image']
        )
        new_id = product_service.add_product(new_product)
        return jsonify({"message": "Product added", "id": new_id}), 201
    except (KeyError, ValueError, ProductServiceError) as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update(product_id):
    data = request.get_json()
    try:
        updated_product = Product(
            product_id=product_id,
            name=data['name'],
            price=float(data['price']),
            image=data['image']
        )
        product_service.update_product(updated_product)
        return jsonify({"message": "Product updated"})
    except ProductNotFoundServiceError as e:
        return jsonify({"error": str(e)}), 404
    except (KeyError, ValueError, ProductServiceError) as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete(product_id):
    try:
        product_service.delete_product(product_id)
        return jsonify({"message": "Product deleted"})
    except ProductNotFoundServiceError as e:
        return jsonify({"error": "Product not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
