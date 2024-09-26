#Importação
from flask import Flask, request, jsonify #Importação do Flask em si, do "request", para que aceite e lide com entradas no formato .json; e "jsonify" que é usado para converter dados Python (como dicionários e listas) em JSON, que é um formato comum de resposta para APIs web.
from flask_sqlalchemy import SQLAlchemy #Extensão do Flask para integração com o banco de dados, nesse caso, SQLite
from flask_cors import CORS #Para permitir o uso de CORS (Cross-Origin Resource Sharing), útil para testar APIs em diferentes domínios, nesse caso, ele importou todas as rotas da aplicação para o Swagger
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user #Biblioteca importada para utilizar todas as ferramentas de rotas de login, autenticação e chave-secreta da aplicação


#Criando uma variável para receber uma instância da classe Flask
app = Flask(__name__)


#Chave-secreta da aplicação nescessária para autenticar o login dos usuários
app.config['SECRET_KEY'] = "minha_chave_123"
#Para definir o caminho do arquivo do nosso banco
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'


#Para gerenciar toda a parte de login e autenticação
login_manager = LoginManager()
#Para linkar nossa aplicação com o banco
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app) #Comando para importar suas rotas para o SWAGGER


#Modelagem
#User (id, username, password)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    cart = db.relationship('CartItem', backref='user', lazy=True)

#Produto (id, name, price, description)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

#Carrinho (id, userID, productID)
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

#Autenticação, juntamente com o login manager fazem todo o processo e retorna os dados de autenticação daquele user que está logado
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Rota criada para logar no sistema
@app.route('/login', methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(username=data.get("username")).first()

    if user and data.get("password") == user.password: 
            login_user(user)       
            return jsonify({"message": "Logged in succesfully!"})

    return jsonify({"message": "Unauthorized. Invalid credentials"}), 401

#Rota criada para deslogar do sistema
@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout succesfully"})        

#Rota criada para adição dos produtos no sistema
@app.route('/api/products/add', methods=["POST"])
@login_required
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product added succesfully!"})
    return jsonify({"message": "Invalid product data"}), 400

#Rota criada para deletar algum produto do sistema
@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
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
@login_required
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
    product_list = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        }
        product_list.append(product_data)
    return jsonify(product_list)

#Checkout
@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    #Preciso ter o usuário
    user = User.query.get(int(current_user.id))
    #Preciso ter o produto
    product = Product.query.get(product_id)

    if user and product:
        cart_item = CartItem(user_id=user.id, product_id=product_id)
        db.session.add(cart_item)
        db.session.commit()
        print(user)
        print(product)
        return jsonify({"message": "Item added to the cart succesfully"})
    return jsonify({"message": "Failed to add item to the cart"}), 400

@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
@login_required
def remove_from_cart(product_id):
    #Produto, Usuário - Item no carrinho
    cart_item = CartItem.query.filter_by(user_id=(int(current_user.id)),product_id=(int(product_id))).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Item removed from the cart successfully"})
    return jsonify({"message": "Failed to remove item from the cart"}), 400
	
@app.route('/api/cart', methods=['GET'])
@login_required
def view_cart():
    #Usuário
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    cart_content = []
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        cart_content.append({
            "id": cart_item.id,
            "user_id": cart_item.user_id,
            "product_id": cart_item.product_id,
            "product_name": product.name,
            "product_price": product.price,
            "product_description": product.description
        })
    return jsonify(cart_content)

@app.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    for cart_item in cart_items:
        db.session.delete(cart_item)
        db.session.commit()
    return jsonify({"message": "Checkout successful. Cart has been cleared."})

if __name__ == "__main__":
    app.run(debug=True)