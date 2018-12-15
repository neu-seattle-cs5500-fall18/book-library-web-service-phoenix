from db_server import db
from constant import *
import datetime


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=True)
    author = db.Column(db.String, nullable=True)
    year = db.Column(db.Integer, nullable=True)

    def parse_body(self, body):
        self.title = body.get('title')
        self.category = body.get('category') or None
        self.author = body.get('author') or None
        self.year = body.get('year') or None

    def __repr__(self):
        return '<Book %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'author': self.author,
            'year': self.year
        }


class User(db.Model):
    username = db.Column(db.String, primary_key=True, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    authenticated = db.Column(db.Boolean, nullable=True, default=False)

    def get_id(self):
        return self.username

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return

    def __repr__(self):
        return '<User %r>' % self.username

    def parse_body(self, body):
        # self.username = body.get('username')
        self.password = body.get('password')
        self.email = body.get('email') or None
        self.first_name = body.get('first_name') or None
        self.last_name = body.get('last_name') or None
        self.phone = body.get('phone') or None

    def serialize(self):
        return {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone
        }


class PrivateList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    name = db.Column(db.String, nullable=False)
    books = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<PrivateList %r>' % self.id

    def parse_body(self, user_id, body):
        self.user = user_id
        self.name = body.get('name') or None
        self.books = str(" ".join(body.get('books').split())) or None

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user,
            'name': self.name,
            'books': self.books,
        }


class Copy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    book = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Copy %r>' % self.id

    def parse_body(self, body):
        self.user = body.get('user') or None
        self.book = body.get('book_id') or None

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user,
            'book': self.book,
            'status': self.status,
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copy = db.Column(db.Integer, db.ForeignKey('copy.id'), nullable=False)
    copy_owner = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    borrower = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=ORDER_STATUS_REQUESTED)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    modified = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    expire = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Copy %r>' % self.id

    def parse_body(self, body):
        self.copy = body.get('copy_id') or None
        self.borrower = body.get('borrower') or None
        self.copy_owner = body.get('copy_owner') or None
        self.expire = body.get('return_date') or None

    def parse_body_status(self, body):
        self.copy = body.get('copy_id') or None
        self.borrower = body.get('borrower') or None
        self.copy_owner = body.get('copy_owner') or None
        self.expire = body.get('return_date') or None
        self.status = body.get('order_status') or None

    def serialize(self):
        return {
            'id': self.id,
            'copy': self.copy,
            'copy_owner': self.copy_owner,
            'borrower': self.borrower,
            'status': self.status,
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S"),
            'modified': self.modified.strftime("%Y-%m-%d %H:%M:%S"),
            'expire': self.expire.strftime("%Y-%m-%d %H:%M:%S"),
        }


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copy_id = db.Column(db.Integer, db.ForeignKey(Copy.id), nullable=False)
    note = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<notes %r>' % self.id

    def parse_body(self, body):
        self.note = body.get('note') or None
        self.copy_id = body.get('copy_id') or None

    def serialize(self):
        return {
            'id': self.id,
            'copy_id': self.copy_id,
            'note': self.note
        }
