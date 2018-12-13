from flask import Flask
from db_server import db
from server import login_manager, book_vector

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# old database, deprecated
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://wgoclgfndpiece:175edbd766319631ba5a2c41bd3b1f428cfcdbab789263c1e882147c9a53ce0a@ec2-23-21-192-179.compute-1.amazonaws.com:5432/d138rvo7lslh7v'
# new database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://kodskjydvyhuha:cae75dee32c49de8f36aaae7c58ed1ec8cc813c0af9fabeec812f0f41a9aaa0f@ec2-184-72-239-186.compute-1.amazonaws.com:5432/d82ih0s4fvis4d'
app.config['SECRET_KEY'] = 'secret_key'
db.init_app(app)
login_manager.init_app(app)
book_vector.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
