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

book_vector = Api(title='Book Vector', description="A book library service")
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


book_api = Namespace("book", description="Book operations")
book_vector.add_namespace(book_api)


@book_api.route('')
class Book(Resource):
    def post(self):
        """Add a book to the library"""
        body = request.get_json()
        new_book = models.Book()
        new_book.parse_body(body)
        db.session.add(new_book)
        db.session.commit()
        return new_book.serialize(), 201

    def get(self):
        """search a book information by year/category/author or combination search"""
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


@book_api.route('/<book_id>')
@book_api.doc(params={'book_id': 'id of a book'})
class Book(Resource):
    def get(self, book_id):
        """Get a book by given an ID"""
        a_book = query_book_by_id(book_id)
        if a_book is None:
            return 'Book does not exit', 404
        return a_book.serialize(), 200

    def put(self, book_id):
        """Update a book by provide the id and information of the book"""
        a_book = query_book_by_id(book_id)
        if a_book is None:
            return 'Book does not exit', 404
        body = request.get_json()
        a_book.parse_body(body)
        db.session.add(a_book)
        db.session.commit()
        return a_book.serialize(), 200

    def delete(self, book_id):
        """Delete a book by given an book id"""
        a_book = query_book_by_id(book_id)
        if a_book is None:
            return 'Book does not exit', 404
        db.session.delete(a_book)
        db.session.commit()
        return "book has been deleted", 200


def query_user_by_name(username):
    return db.session.query(models.User).filter_by(username=username).first()


user_api = Namespace('user', description="User operations")
book_vector.add_namespace(user_api)


@user_api.route('/<username>')
@user_api.doc(params={'username': 'id of a user'})
class User(Resource):
    def get(self, username):
        """Get a user's information"""
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        return user.serialize(), 200

    def put(self, username):
        """"Update a user information by providing json info"""
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
        """Delete a user by providing a user name"""
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


@user_api.route('/<username>/privatelist')
@user_api.doc(params={'username': 'name of a user'})
class PrivateList(Resource):
    def post(self, username):
        """Add a private book list to a user"""
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
        """Get all private list of books for a user"""
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401

        out = []
        for copy in db.session.query(models.PrivateList).filter_by(user=username):
            out.append(copy.serialize())
        return out, 201


@user_api.route('/<username>/privatelist/<private_list_name>')
@user_api.doc(params={'username': 'id of a user',
                      'private_list_name': 'the private list name owned by the user'})
class PrivateList(Resource):
    def delete(self, username, private_list_name):
        """Delete a user's private list"""
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
        """Get a private list of books for a user"""
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        list = query_private_list_by_id(username, private_list_name)
        if list is None:
            return 'Private List does not exit', 404
        return list.serialize(), 200


@user_api.route('/<username>/privatelist/<private_list_name>/addbooks')
@user_api.doc(params={'username': "name of a user",
                      'private_list_name': 'the private list name owned by the user'})
class PrivateList(Resource):
    def post(self, username, private_list_name):
        """Add books to a private lsit of books owned by a user"""
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


@user_api.route('/<username>/privatelist/<private_list_name>/removebooks')
@user_api.doc(params={'username': "name of a user",
                      'private_list_name': 'the private list name owned by the user'})
class PrivateList(Resource):
    def post(self, username, private_list_name):
        """Remove books from a private list owned by a user"""
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


copy_api = Namespace('copy', description="copy operations")
book_vector.add_namespace(copy_api)


@copy_api.route('')
class Copy(Resource):
    def post(self):
        """add copy of a book to a user"""
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
        """Get all books/copies owned by a user"""
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


@copy_api.route('/<copy_id>')
@copy_api.doc(params={'copy_id': 'id of a copy'})
class Copy(Resource):
    def get(self, copy_id):
        """Get the book/copy information of a book"""
        copy = db.session.query(models.Copy).filter_by(id=copy_id).first()
        if copy is None:
            return 'copy is not found', 404
        return copy.serialize(), 200

    def delete(self, copy_id):
        """Delete a copy of books"""
        copy = db.session.query(models.Copy).filter_by(id=copy_id).first()
        if copy is None:
            return 'copy is not found', 404
        if invalid_user(copy.user):
            return 'Unauthorized User', 401
        db.session.delete(copy)
        db.session.commit()
        return "copy has been deleted", 200


@copy_api.route('/<copy_id>/updatestatus')
@copy_api.doc(params={'copy_id': 'id of a copy'})
class Copy(Resource):
    def put(self, copy_id):
        """Update the status of a copy of book"""
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


@copy_api.route('/<copy_id>/note')
@copy_api.doc(params={'copy_id': 'id of a copy'})
class Copy(Resource):
    def get(self, copy_id):
        """Get all notes for a copy of a book"""
        checkCopyValidity(copy_id)
        copy_notes = db.session.query(models.Notes).filter_by(copy_id=copy_id)
        if copy_notes is None:
            return 'note is not found', 404

        return [copy.note for copy in copy_notes], 200

    def post(self, copy_id):
        """Add a note to a copy of a book"""
        checkCopyValidity(copy_id)
        note_body = request.get_json()
        new_note = models.Notes()
        new_note.parse_body(note_body)
        new_note.copy_id = copy_id
        db.session.add(new_note)
        db.session.commit()
        return 'A note \"{}\" has been added to book copy of {}'.format(new_note.note, copy_id), 200

    def put(self, copy_id):
        """Update a note for a book"""
        checkCopyValidity(copy_id)
        note_body = request.get_json()
        note_id = note_body.get('note_id')
        copy_note = db.session.query(models.Notes).filter_by(id=note_id).first()
        if copy_note is None:
            return 'Copy of the note not found', 404
        copy_note.parse_body(note_body)
        db.session.commit()
        return 'Node for copy book of {} has been updated'.format(copy_id)

    def delete(self, copy_id):
        """Remove a note or all notes for a book"""
        checkCopyValidity(copy_id)
        note_body = request.get_json()
        note_id = note_body.get('note_id')
        if note_id is None:
            notes = db.session.query(models.Notes).filter_by(copy_id=copy_id)
            db.session.delete(notes)
            db.session.commit()
            return 'Notes for book copy of {} has been all removed'.format(copy_id)
        note = db.session.query(models.Notes).filter_by(id=note_id).filter_by(copy_id=copy_id)
        db.session.delete(note)
        db.session.commit()
        return 'Note id of {} for copy of book has been removed.'.format(note_id)


def checkCopyValidity(copy_id):
    copy = db.session.query(models.Copy).filter_by(id=copy_id).first()
    if copy is None:
        return 'copy is not found', 404
    if invalid_user(copy.user):
        return 'Unauthorized User', 401


order_api = Namespace('order', description="Order operations")
book_vector.add_namespace(order_api)


@order_api.route('')
class Order(Resource):
    def post(self):
        """Make an order of book"""
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
        if copy.status == BOOK_COPY_STATUS_UNAVAILABLE:
            return 'The copy of the book is not available', 400
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
        """Get all information about orders"""
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

        status = request.args.get('status')
        if status is not None:
            orders = orders.filter_by(status=status)

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


@order_api.route('/<order_id>/accept')
@order_api.doc(params={'order_id': 'id of an order'})
class Order(Resource):
    def put(self, order_id):
        """Accept an order"""
        order = change_order_status(order_id, ORDER_STATUS_ACCPETED)
        if order is None:
            return 'Order ID not found ' + str(order_id), 409
        elif invalid_user(order.copy_owner):
            return 'Unauthorized User', 401
        copy = db.session.query(models.Copy).filter_by(id=order.copy).first()
        copy.status = BOOK_COPY_STATUS_UNAVAILABLE
        db.session.commit()
        return order.serialize(), 201


@order_api.route('/<order_id>/decline')
@order_api.doc(params={'order_id': 'id of an order'})
class Order(Resource):
    def put(self, order_id):
        """Decline an order"""
        order = change_order_status(order_id, ORDER_STATUS_DECLINED)
        if order is None:
            return 'Order ID not found ' + str(order_id), 409
        elif invalid_user(order.copy_owner):
            return 'Unauthorized User', 401
        copy = db.session.query(models.Copy).filter_by(id=order.copy).first()
        copy.status = BOOK_COPY_STATUS_AVAILABLE
        db.session.commit()
        return order.serialize(), 201


@order_api.route('/<order_id>')
@order_api.doc(params={'order_id': 'id of an order'})
class Order(Resource):
    def get(self, order_id):
        """Get information about an order"""
        order = db.session.query(models.Order).filter_by(id=order_id).first()
        if order is None:
            return 'Order does not exit', 404
        return order.serialize(), 200


@order_api.route('/return')
class Order(Resource):
    def post(self):
        """Return a book to complete an order, by providing an order id or copy id"""
        order = None
        order_id = request.args.get('order_id')
        copy_id = request.args.get('copy_id')
        if order_id is not None and copy_id is not None:
            return 'Only one parameter is needed', 400
        if order_id is not None:
            order = db.session.query(models.Order).filter_by(id=order_id).first()
        if copy_id is not None:
            order = db.session.query(models.Order).filter_by(copy=copy_id).first()
        if order is None:
            return 'Please provide a correct order_id or copy_id for the book', 404
        copy = db.session.query(models.Copy).filter_by(id=order.copy).first()
        if copy is None:
            return 'Copy of the book does not exit', 404
        order = change_order_status(order.id, ORDER_STATUS_COMPLETED)
        copy.status = BOOK_COPY_STATUS_AVAILABLE
        db.session.commit()
        return order.serialize(), 200


login_api = Namespace('login', description="Login operations")
book_vector.add_namespace(login_api)


@login_api.route('')
class Login(Resource):
    def post(self):
        """Login as a user"""
        if request.form:
            username = request.form['username']
            password = request.form['password']
        else:
            username = request.args.get('username')  # form['username']
            password = request.args.get('password')  # form['password']

        return self.try_login(username, password)

    def get(self):
        """Get the login form"""
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


register_api = Namespace('register', "Register operations")
book_vector.add_namespace(register_api)


@register_api.route('/')
class Register(Resource):
    def post(self):
        """Register as a user"""
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
        """Get user registration form"""
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


logout_api = Namespace('logout', description="Logout operations")
book_vector.add_namespace(logout_api)


@logout_api.route('/')
class Logout(Resource):
    def post(self):
        """Current user logout"""
        logout_user()
        return Response("Logout Successfully")

    def get(self):
        """Current user logout"""
        logout_user()
        return Response("Logout Successfully")


reminder_api = Namespace('reminder', description="Send reminder operations")
book_vector.add_namespace(reminder_api)


@reminder_api.route('/')
class Reminder(Resource):
    def get(self):
        return "Sent reminders", 201
