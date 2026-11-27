
from flask import Flask, render_template, request, redirect, url_for, abort
from bson.objectid import ObjectId
from bson.errors import InvalidId

import database as dbase
from product import Product

app = Flask(__name__)

db = dbase.dbConnection()
products_collection = db["products"]
movies_collection = db["movies"]


# HU-05: listar el catálogo de películas
@app.route("/movies")
def list_movies():
    movies = list(
        movies_collection.find().sort([("title", 1), ("year", -1)])
    )
    return render_template("movies/index.html", movies=movies)


# Validar ID de MongoDB
def get_product(id):
    try:
        product = products_collection.find_one({
            "_id": ObjectId(id)
        })
        if product is None:
            abort(404)
        return product
    except InvalidId:
        abort(404)


# LISTAR PRODUCTOS Y APLICAR FILTROS
@app.route("/products")
def home():

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()

    query = {}

    # Búsqueda por nombre
    if search:
        query["name"] = {
            "$regex": search,
            "$options": "i"
        }

    # Filtro por categoría
    if category:
        query["category"] = category

    # Filtro por rango de precio
    price_filter = {}

    try:
        if min_price:
            price_filter["$gte"] = float(min_price)

        if max_price:
            price_filter["$lte"] = float(max_price)

        if price_filter:
            query["price"] = price_filter

    except ValueError:
        abort(400, description="El rango de precio no es válido")

    if min_price and max_price:
        if float(min_price) > float(max_price):
            abort(400, description="El precio mínimo no puede superar al máximo")

    products = products_collection.find(query)

    categories = products_collection.distinct("category")

    return render_template(
        "products/index.html",
        products=products,
        categories=categories,
        search=search,
        category=category,
        min_price=min_price,
        max_price=max_price
    )


# FORMULARIO PARA CREAR PRODUCTO
@app.route("/products/new")
def new_product():
    return render_template("products/create.html")


# CREAR PRODUCTO
@app.route("/products", methods=["POST"])
def add_product():

    try:
        product = Product(
            request.form["name"].strip(),
            request.form["description"].strip(),
            request.form["price"],
            request.form["stock"],
            request.form["category"].strip(),
            request.form["image"].strip()
        )

        if not product.name or not product.category:
            abort(400, description="Nombre y categoría son obligatorios")

        if product.price < 0 or product.stock < 0:
            abort(400, description="Precio y stock no pueden ser negativos")

        products_collection.insert_one(
            product.toDBCollection()
        )

        return redirect(url_for("home"))

    except (ValueError, KeyError):
        abort(400, description="Datos del producto no válidos")


# VER DETALLE DEL PRODUCTO
@app.route("/products/<id>")
def detail(id):

    product = get_product(id)

    return render_template(
        "products/detail.html",
        product=product
    )


# FORMULARIO PARA EDITAR
@app.route("/products/<id>/edit")
def edit_view(id):

    product = get_product(id)

    return render_template(
        "products/edit.html",
        product=product
    )


# ACTUALIZAR PRODUCTO
@app.route("/products/<id>/edit", methods=["POST"])
def update_product(id):

    get_product(id)

    try:
        name = request.form["name"].strip()
        description = request.form["description"].strip()
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        category = request.form["category"].strip()
        image = request.form["image"].strip()

        if not name or not category:
            abort(400, description="Nombre y categoría son obligatorios")

        if price < 0 or stock < 0:
            abort(400, description="Precio y stock no pueden ser negativos")

        products_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "name": name,
                    "description": description,
                    "price": price,
                    "stock": stock,
                    "category": category,
                    "image": image
                }
            }
        )

        return redirect(url_for("home"))

    except (ValueError, KeyError):
        abort(400, description="Datos del producto no válidos")


# CONFIRMAR ELIMINACIÓN
@app.route("/products/<id>/delete")
def delete_view(id):

    product = get_product(id)

    return render_template(
        "products/delete.html",
        product=product
    )


# ELIMINAR PRODUCTO
@app.route("/products/<id>/delete", methods=["POST"])
def delete_product(id):

    get_product(id)

    products_collection.delete_one({
        "_id": ObjectId(id)
    })

    return redirect(url_for("home"))


#errores
@app.errorhandler(404)
def not_found(error):
    return render_template(
        "404.html",
        message="Producto o página no encontrada"
    ), 404


if __name__ == "__main__":
    app.run(debug=True, port=4000)
