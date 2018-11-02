from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Namespace, Api

app = Flask(__name__)
book_vector = Api(title='Book Vector')
api = Namespace('Book Vector')
book_vector.init_app(app)
book_vector.add_namespace(api)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:[password]@localhost:3306/bookvector"
db = SQLAlchemy(app)

# create project database if not exist
with app.app_context():
    db.create_all()


@app.route('/')
def start_service():
    return "Welcome to BookVector", 200


# @app.route('/v2')
# def swagger_api():
#     return render_template("")


@app.route('/support')
def support():
    return "Please contact yu.jiah@husky.neu.edu; chen.xiany@husky.neu.edu", 200


if __name__ == '__main__':
    app.run(debug=True)
