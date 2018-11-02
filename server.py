
from flask_restplus import Resource, fields
from flask_sqlalchemy import SQLAlchemy
import app
import models


book = app.api.models('Book', {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
    'email': fields.String,
    'firsName': fields.String,
    'lastName': fields.String,
    'phone': fields.String
})

def query_book_by_id(book_id):
    return app.db.session.query(models.Book).filter_by(id=book_id).first()

@app.api.resources()
@app.api.route()
@app.api.doc()
class Book(Resource) :

    @app.api.resources()
    def get(self, book_id):
        a_book = query_book_by_id(book_id)
        if a_book is None:
            return 'Book does not exit', 404
        return a_book.serialize(), 200



class User(Resource):



class Copy(Resource):



class Order(Resource):


class PrivateList(Resource):
