from app import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=True)
    author = db.Column(db.DateTime, nullable=True)
    year = db.Column(db.Integer, nullable=True)

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
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    firstName = db.Column(db.String, nullable=True)
    lastName = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)

    def __repr__(self):
        return '<Model %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'phone': self.phone
        }


class Copy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Copy %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user,
            'book': self.book,
            'status': self.status
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copy = db.Column(db.Integer, db.ForeignKey('copy.id'), nullable=False)
    borrowerId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Copy %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'copy': self.copy,
            'borrowerId': self.borrowerId,
            'status': self.status
        }


class PrivateList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    books = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Copy %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user,
            'name': self.name,
            'books': self.books,
        }