from flask_restplus import Resource, Namespace, Api
from db_server import db
from constant import *
import models
from flask import request, abort, Response
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
import ast, datetime

login_manager = LoginManager()
login_manager.login_view = "login"

api = Namespace('')
book_vector = Api(title='Book Vector')
book_vector.add_namespace(api)


# callback to reload the user object
@login_manager.user_loader
def load_user(username):
    return query_user_by_name(username)


def invalid_user(username):
    try:
        if current_user.username == username:
            return False
        return True
    except:
        return True


@api.route('/home')
class Home(Resource):
    def get(self):
        return "User Home: " + current_user.username


@api.route('/support')
class Home(Resource):
    def get(self):
        return "Please contact yu.jiah@husky.neu.edu; chen.xiany@husky.neu.edu", 200


@api.route('/book')
class Book(Resource):
    def post(self):
        body = request.get_json()
        new_book = models.Book()
        new_book.parse_body(body)
        db.session.add(new_book)
        db.session.commit()
        return new_book.serialize(), 201

    def get(self):
        books = db.session.query(models.Book)
        year = request.args.get('year')
        if year is not None:
            books = books.filter_by(year=year)

        category = request.args.get('category')
        if category is not None:
            books = books.filter_by(category=category)

        author = request.args.get('author')
        if author is not None:
            books = books.filter_by(author=author)

        out = []
        for book in books:
            out.append(book.serialize())
        return out, 201


def query_book_by_id(book_id):
    return db.session.query(models.Book).filter_by(id=book_id).first()


@api.route('/book/<book_id>')
@api.doc(params={'book_id': 'id of a book'})
class Book(Resource):
    def get(self, book_id):
        a_book = query_book_by_id(book_id)
        if a_book is None:
            return 'Book does not exit', 404
        return a_book.serialize(), 200

    def put(self, book_id):
        a_book = query_book_by_id(book_id)
        if a_book is None:
            return 'Book does not exit', 404
        body = request.get_json()
        a_book.parse_body(body)
        db.session.add(a_book)
        db.session.commit()
        return a_book.serialize(), 200

    def delete(self, book_id):
        a_book = query_book_by_id(book_id)
        if a_book is None:
            return 'Book does not exit', 404
        db.session.delete(a_book)
        db.session.commit()
        return "book has been deleted", 200


def query_user_by_name(username):
    return db.session.query(models.User).filter_by(username=username).first()


@api.route('/user/<username>')
@api.doc(params={'username': 'id of a user'})
class User(Resource):
    def get(self, username):
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        return user.serialize(), 200

    def put(self, username):
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        body = request.get_json()
        user.parse_body(body)
        db.session.add(user)
        db.session.commit()
        return user.serialize(), 200

    def delete(self, username):
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        db.session.delete(user)
        db.session.commit()
        return "user has been deleted", 200


def query_private_list_by_id(username, private_list_name):
    return db.session.query(models.PrivateList).filter_by(user=username, name=private_list_name).first()


@api.route('/user/<username>/privatelist')
@api.doc(params={'username': 'name of a user'})
class PrivateList(Resource):
    def post(self, username):
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        body = request.get_json()
        list = query_private_list_by_id(username, body.get('name'))
        if list is not None:
            return 'Private List already exist', 409

        if invalid_user(username):
            return 'Unauthorized User', 401

        for book_id in body.get('books'):
            if query_book_by_id(book_id) is None:
                return 'Book ID not found ' + str(book_id), 409

        new_list = models.PrivateList()
        new_list.parse_body(username, body)
        db.session.add(new_list)
        db.session.commit()
        return new_list.serialize(), 201

    def get(self, username):
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401

        out = []
        for copy in db.session.query(models.PrivateList).filter_by(user=username):
            out.append(copy.serialize())
        return out, 201


@api.route('/user/<username>/privatelist/<private_list_name>')
@api.doc(params={'username': 'id of a user',
                 'private_list_name': 'the private list name owned by the user'})
class PrivateList(Resource):
    def delete(self, username, private_list_name):
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        list = query_private_list_by_id(username, private_list_name)
        if list is None:
            return 'Private List does not exit', 404
        db.session.delete(list)
        db.session.commit()
        return "PrivateList has been deleted", 200

    def get(self, username, private_list_name):
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        list = query_private_list_by_id(username, private_list_name)
        if list is None:
            return 'Private List does not exit', 404
        return list.serialize(), 200


@api.route('/user/<username>/privatelist/<private_list_name>/addbooks')
class PrivateList(Resource):
    def post(self, username, private_list_name):
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        list = query_private_list_by_id(username, private_list_name)
        if list is None:
            return 'Private List does not exit', 404

        body = request.get_json()

        for book_id in body.get('books'):
            if query_book_by_id(book_id) is None:
                return 'Book ID not found ' + str(book_id), 409

        old_list = ast.literal_eval(list.books)
        if old_list is not None:
            list.books = str(old_list.union(body.get('books')))
        else:
            list.books = body.get('books')
        db.session.commit()
        return list.serialize(), 200


@api.route('/user/<username>/privatelist/<private_list_name>/removebooks')
class PrivateList(Resource):
    def post(self, username, private_list_name):
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        list = query_private_list_by_id(username, private_list_name)
        if list is None:
            return 'Private List does not exit', 404

        body = request.get_json()
        existing_books = ast.literal_eval(list.books)
        for book in body.get('books'):
            existing_books.remove(book)
        list.books = str(existing_books)
        db.session.commit()
        return list.serialize(), 200


@api.route('/copy')
class Copy(Resource):
    def post(self):
        body = request.get_json()
        username = body.get('user')
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        book_id = body.get('book')
        if query_book_by_id(book_id) is None:
            return 'Book ID not found ' + str(book_id), 409
        new_copy = models.Copy()
        new_copy.parse_body(body)
        new_copy.status = BOOK_COPY_STATUS_AVAILABLE
        db.session.add(new_copy)
        db.session.commit()
        return new_copy.serialize(), 201

    def get(self):
        copies = db.session.query(models.Copy)
        book_id = request.args.get('book')
        if book_id is not None:
            copies = copies.filter_by(book=book_id)

        username = request.args.get('user')
        if username is not None:
            copies = copies.filter_by(user=username)
        status = request.args.get("status")
        if status is not None:
            copies = copies.filter_by(status=status)
        out = []
        for copy in copies:
            out.append(copy.serialize())
        return out, 201


@api.route('/copy/<copy_id>')
@api.doc(params={'copy_id': 'id of a copy'})
class Copy(Resource):
    def get(self, copy_id):
        copy = db.session.query(models.Copy).filter_by(id=copy_id).first()
        if copy is None:
            return 'copy is not found', 404
        return copy.serialize(), 200

    def delete(self, copy_id):
        copy = db.session.query(models.Copy).filter_by(id=copy_id).first()
        if copy is None:
            return 'copy is not found', 404
        if invalid_user(copy.user):
            return 'Unauthorized User', 401
        db.session.delete(copy)
        db.session.commit()
        return "copy has been deleted", 200


@api.route('/copy/<copy_id>/updatestatus')
class Copy(Resource):
    def put(self, copy_id):
        body = request.get_json()
        copy = db.session.query(models.Copy).filter_by(id=copy_id).first()
        if copy is None:
            return 'copy is not found', 404
        if invalid_user(copy.user):
            return 'Unauthorized User', 401
        copy.status = body.get('status')
        db.session.add(copy)
        db.session.commit()
        return copy.serialize(), 200


@api.route('/order')
class Order(Resource):
    def post(self):
        body = request.get_json()
        borrower = body.get('borrower')
        borrower = query_user_by_name(borrower)
        if borrower is None:
            return 'User does not exit', 404
        if invalid_user(borrower.username):
            return 'Unauthorized User', 401
        copy_id = body.get('copy')
        copy = db.session.query(models.Copy).filter_by(id=copy_id).first()
        if copy is None:
            return 'Copy ID not found ' + str(copy_id), 409

        copy_owner = body.get('copy_owner')
        owner = query_user_by_name(copy_owner)
        if owner is None:
            return 'Copy owner not found ' + copy_owner, 409

        new_order = models.Order()
        new_order.parse_body(body)
        new_order.status = ORDER_STATUS_REQUESTED
        db.session.add(new_order)
        db.session.commit()
        return new_order.serialize(), 201

    def get(self):
        orders = db.session.query(models.Order)
        copy = request.args.get('copy')
        if copy is not None:
            orders = orders.filter_by(copy=copy)

        borrower = request.args.get('borrower')
        if borrower is not None:
            orders = orders.filter_by(borrower=borrower)

        copy_owner = request.args.get('copy_owner')
        if copy_owner is not None:
            orders = orders.filter_by(copy_owner=copy_owner)

        out = []
        for order in orders:
            out.append(order.serialize())
        return out, 201

def change_order_status(order_id, status):
    order = db.session.query(models.Order).filter_by(id=order_id).first()
    if order is not None:
        order.status = status
        order.modified = datetime.datetime.utcnow()
        db.session.add(order)
        db.session.commit()
    return order


@api.route('/order/<order_id>/accept')
@api.doc(params={'order_id': 'id of an order'})
class Order(Resource):
    def put(self, order_id):
        order = change_order_status(order_id, ORDER_STATUS_ACCPETED)
        if order is None:
            return 'Order ID not found ' + str(order_id), 409
        elif invalid_user(order.copy_owner):
            return 'Unauthorized User', 401

        return order.serialize(), 201


@api.route('/order/<order_id>/decline')
@api.doc(params={'order_id': 'id of an order'})
class Order(Resource):
    def put(self, order_id):
        order = change_order_status(order_id, ORDER_STATUS_DECLINED)
        if order is None:
            return 'Order ID not found ' + str(order_id), 409
        elif invalid_user(order.copy_owner):
            return 'Unauthorized User', 401
        return order.serialize(), 201


@api.route('/order/<order_id>')
@api.doc(params={'order_id': 'id of an order'})
class Order(Resource):
    def get(self, order_id):
        order = db.session.query(models.Order).filter_by(id=order_id).first()
        if order is None:
            return 'Order does not exit', 404
        return order.serialize(), 200


@api.route('/login')
class Login(Resource):
    def post(self):
        if request.form:
            username = request.form['username']
            password = request.form['password']
        else:
            username = request.args.get('username')  # form['username']
            password = request.args.get('password')  # form['password']

        return self.try_login(username, password)

    def get(self):
        return Response('''
            <form action="" method="post">
                <p><input type=text name=username>
                <p><input type=password name=password>
                <p><input type=submit value=Login>
            </form>
        ''')

    def try_login(self, username, password):
        registeredUser = load_user(username)
        if registeredUser != None and registeredUser.password == password:
            registeredUser.authenticated = True
            login_user(registeredUser)
            return "Login Successfully: " + current_user.username
        else:
            return abort(401)


@api.route('/register')
class Register(Resource):
    def post(self):
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']

        if query_user_by_name(username) is not None:
            return 'User already exist', 409
        new_user = models.User(username=username,
                               password=password,
                               email=email or None,
                               first_name=first_name or None,
                               last_name=last_name or None,
                               phone=phone or None)
        db.session.add(new_user)
        db.session.commit()
        return Response("Registered Successfully")

    def get(self):
        return Response('''
            <form action="" method="post">
            <p><input type=text name=username placeholder="Enter username">
            <p><input type=text name=password placeholder="Enter password">
            <p><input type=text name=email placeholder="Enter email">
            <p><input type=text name=first_name placeholder="Enter first_name">
            <p><input type=text name=last_name placeholder="Enter last_name">
            <p><input type=text name=phone placeholder="Enter phone">
            <p><input type=submit value=Create>
            </form>
        ''')


@api.route('/logout')
class Logout(Resource):
    def post(self):
        logout_user()
        return Response("Logout Successfully")

    def get(self):
        logout_user()
        return Response("Logout Successfully")
