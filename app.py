#Importação
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#Para criar nossa aplicação
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

#Definir uma rota raiz (página inicial) e a função que será executada ao requisitar
@app.route('/')
def hello_world():
    return 'Hello World'

if __name__ == "__main__":
    app.run(debug=True)