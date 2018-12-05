from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Namespace, Api

app = Flask(__name__)
book_vector = Api(title='Book Vector')
book_vector.init_app(app)
api = Namespace('')
book_vector.add_namespace(api)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://wgoclgfndpiece:175edbd766319631ba5a2c41bd3b1f428cfcdbab789263c1e882147c9a53ce0a@ec2-23-21-192-179.compute-1.amazonaws.com:5432/d138rvo7lslh7v'
app.config['SECRET_KEY'] = 'secret_key'

db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)
