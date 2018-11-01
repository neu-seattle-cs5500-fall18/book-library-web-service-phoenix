from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:[password]@localhost:3306/bookvector"
db = SQLAlchemy(app)
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
