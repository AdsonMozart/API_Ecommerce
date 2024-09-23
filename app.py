#Importação
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

#Criando uma variável para receber uma instância da classe Flask
app = Flask(__name__)

#Para definir o caminho do arquivo do nosso banco
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

#Para linkar nossa aplicação com o banco
db = SQLAlchemy(app)

#Modelagem
#Produto (id, name, price, description)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

@app.route('/api/products/add', methods=["POST"])
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product added succesfully!"})
    return jsonify({"message": "Invalid product data"}), 400


@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):
    # Recuperar o produto da base de dados
    # Verificar se o produto existe
    # Se existe, apaga da base de dados
    # Se não existe, retornar o 404 not found

    # Recuperando o id do produto na base de dados
    product = Product.query.get(product_id)
    # Verificando se o produto existe ou não, você possui duas formas (if product != None:) ou (if product)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted succesfully!"})
    return jsonify({"message": "Product not found"}), 404


@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
    # Recuperando o id do produto na base de dados
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        })
    return jsonify({"message": "Product not found"}), 404


@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    data = request.json
    if 'name' in data:
        product.name = data['name']
    
    if 'price' in data:
        product.price = data['price']

    if 'description' in data:
        product.description = data['description']

    db.session.commit()
    return jsonify({"message": "Product updated successfully"})

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    print(products)
    for product in products:
        print(product)
        
    return jsonify({"message": "test"})





#Definir uma rota raiz (página inicial) e a função que será executada ao requisitar
@app.route('/')
def hello_world():
    return 'Hello World'

if __name__ == "__main__":
    app.run(debug=True)