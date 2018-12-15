from flask_restplus import Resource, Namespace, Api, fields, reqparse
from db_server import db
from constant import *
import models
from flask import request, abort, Response
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
import ast
from datetime import datetime, timedelta, date
from send_email import EmailSender

login_manager = LoginManager()
login_manager.login_view = "login"
api = Namespace('')
book_vector = Api(title='Book Vector', version='2.0', description="A book library service by Team Phoenix")
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
        if current_user is None:
            return 'Home: no user login yet', 200
        return "User Home: " + current_user.username, 200


@api.route('/support')
class Home(Resource):
    def get(self):
        return "Please contact yu.jiah@husky.neu.edu; chen.xiany@husky.neu.edu", 200


book_api = Namespace("book", description="Book operations")
book_vector.add_namespace(book_api)

book_marshaller = book_api.model('Book_Query', {
    'title': fields.String(),
    'category': fields.String(),
    'author': fields.String(),
    'year': fields.Integer()
})

new_book_marshaller = book_api.model('Full_Book', {
    'id': fields.Integer(),
    'title': fields.String(),
    'category': fields.String(),
    'author': fields.String(),
    'year': fields.Integer()
})

query_parser = reqparse.RequestParser()
query_parser.add_argument('title', type=str, required=False)
query_parser.add_argument('category', type=str, required=False)
query_parser.add_argument('author', type=str, required=False)
query_parser.add_argument('year', type=int, required=False)
query_parser.add_argument('year1', type=int, required=False)
query_parser.add_argument('year2', type=int, required=False)


@book_api.route('')
@book_api.response(400, 'Bad request')
class Book(Resource):
    @book_api.response(201, 'Created')
    @book_api.marshal_with(new_book_marshaller, code=201)
    @book_api.expect(book_marshaller, validate=True)
    def post(self):
        '''
        Add a book to the library
        :return: A Json format of new book
        '''
        body = request.get_json()
        new_book = models.Book()
        new_book.parse_body(body)
        db.session.add(new_book)
        db.session.commit()
        return new_book.serialize(), 201

    @book_api.response(200, 'success')
    def get(self):
        """get information for all books"""
        books = db.session.query(models.Book)
        return [book.serialize() for book in books], 200


@book_api.route('/search')
@book_api.response(200, 'success')
@book_api.response(404, 'info not found')
@book_api.response(416, 'request range required')
class Book(Resource):
    @book_api.doc(body=query_parser)
    def get(self):
        '''
        Search a book by title/year/category/author or combination search
        if no query params provided, return all books
        :return: Json list of books that matched query parameters
        '''
        books = db.session.query(models.Book)
        args = query_parser.parse_args()
        title = args['title']
        if title is not None:
            books = books.filter_by(title=title)
        year = args['year']
        if year is not None:
            books = books.filter_by(year=year)

        category = args['category']
        if category is not None:
            books = books.filter_by(category=category)

        author = args['author']
        if author is not None:
            books = books.filter_by(author=author)
        year1 = args['year1']
        year2 = args['year2']
        if year1 is None and year2 is not None or (year2 is None and year1 is not None):
            return 'Search between years should provide year1 and year2', 416
        if year1 is not None and year2 is not None:
            books = books.filter(models.Book.year >= year1, models.Book.year <= year2)
        return [book.serialize() for book in books], 200


def query_book_by_id(book_id):
    return db.session.query(models.Book).filter_by(id=book_id).first()


@book_api.route('/<book_id>')
@book_api.doc(params={'book_id': 'id of a book'})
@book_api.response(200, 'success')
@book_api.response(404, 'Id not found')
class Book(Resource):
    def get(self, book_id):
        '''
        Get a book by given an ID
        :param book_id: id of the book
        :return: a book in Json format
        '''
        a_book = query_book_by_id(book_id)
        if a_book is None:
            return 'Book does not exit', 404
        return a_book.serialize(), 200

    @book_api.marshal_with(new_book_marshaller, code=200)
    @book_api.expect(book_marshaller, validate=True)
    def put(self, book_id):
        """
        Update a book by provide the id and information of the book
        :param book_id: book id
        :return: an updated Json format of book
        """
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

user_marshaller = user_api.model('User', {
    'password': fields.String(),
    'email': fields.String(),
    'first_name': fields.String(),
    'last_name': fields.String(),
    'phone': fields.String()
})


@user_api.route('/<username>')
@user_api.doc(params={'username': 'username for a user'})
@user_api.response(404, 'User not exist')
class User(Resource):
    def get(self, username):
        """
        Get a user's information
        :return: Json format of user information
        """
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exist', 404
        return user.serialize(), 200

    @user_api.response(401, 'Unauthorized user')
    @user_api.expect(user_marshaller, validate=True)
    def put(self, username):
        """"Update a user's information"""
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

    @user_api.response(401, 'Unauthorized user')
    def delete(self, username):
        """Delete a user"""
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


list_marshaller = user_api.model('List', {
    'name': fields.String(),
    'books': fields.String()
})


@user_api.route('/<username>/privatelist')
@user_api.doc(params={'username': 'name of a user'})
@user_api.response(404, 'User does not exist')
@user_api.response(401, 'Unauthorized User')
class PrivateList(Resource):
    @user_api.response(409, 'List name already exists')
    @user_api.response(404, 'Book id not found')
    @user_api.response(201, 'Post successful')
    @user_api.expect(list_marshaller, validate=True)
    def post(self, username):
        """
        Add a private book list to a user"
        :return: Json format of a private list for a user
        """""
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exist', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        body = request.get_json()
        lst = query_private_list_by_id(username, body.get('name'))
        if lst is not None:
            return 'Private List already exist', 409

        if invalid_user(username):
            return 'Unauthorized User', 401

        for book_id in body.get('books').split():
            if query_book_by_id(book_id) is None:
                return 'Book ID not found ' + str(book_id), 404

        new_list = models.PrivateList()
        new_list.parse_body(username, body)
        db.session.add(new_list)
        db.session.commit()
        return new_list.serialize(), 201

    @user_api.response(200, 'Successful')
    def get(self, username):
        """
        Get all private list of books for a user
        :return: Json lists of books for a user
        """
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        lists = db.session.query(models.PrivateList).filter_by(user=username)
        return [l.serialize() for l in lists], 200


@user_api.route('/<username>/privatelist/<private_list_name>')
@user_api.doc(params={'username': 'id of a user',
                      'private_list_name': 'the private list name owned by the user'})
@user_api.response(200, 'success')
@user_api.response(404, 'User does not exist or list name does not exist')
@user_api.response(401, 'Unauthorized user')
class PrivateList(Resource):
    def delete(self, username, private_list_name):
        """Delete a user's private list"""
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        lst = query_private_list_by_id(username, private_list_name)
        if lst is None:
            return 'Private List does not exist', 404
        db.session.delete(lst)
        db.session.commit()
        return "PrivateList has been deleted", 200

    def get(self, username, private_list_name):
        """Get a private list of books for a user"""
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exist', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        lst = query_private_list_by_id(username, private_list_name)
        if lst is None:
            return 'Private List does not exist', 404
        return lst.serialize(), 200


add_remove_books_marshaller = user_api.model('Books', {
    'book_ids': fields.String()
})


@user_api.route('/<username>/privatelist/<private_list_name>/addbooks')
@user_api.doc(params={'username': "name of a user",
                      'private_list_name': 'the private list name owned by the user'})
@user_api.response(201, 'success')
@user_api.response(404, 'User does not exist or list name does not exist')
@user_api.response(401, 'Unauthorized user')
@user_api.response(409, 'Book id not found')
class PrivateList(Resource):
    @user_api.expect(add_remove_books_marshaller, validate=True)
    def post(self, username, private_list_name):
        """Add books to a private lsit of books owned by a user"""
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        lst = query_private_list_by_id(username, private_list_name)
        if lst is None:
            return 'Private List does not exit', 404

        body = request.get_json()
        added = body.get('book_ids').split()
        for book_id in added:
            if query_book_by_id(book_id) is None:
                return 'Book ID not found ' + str(book_id), 409

        if lst.books is not None:
            lst.books = lst.books + " " + " ".join(added)
        else:
            lst.books = " ".join(added)
        db.session.commit()
        return lst.serialize(), 201


@user_api.route('/<username>/privatelist/<private_list_name>/removebooks')
@user_api.doc(params={'username': "name of a user",
                      'private_list_name': 'the private list name owned by the user'})
@user_api.response(200, 'success')
@user_api.response(404, 'User does not exist or list name does not exist')
@user_api.response(400, 'Book id not in the list')
@user_api.response(401, 'Unauthorized user')
class PrivateList(Resource):
    @user_api.expect(add_remove_books_marshaller, validate=True)
    def put(self, username, private_list_name):
        """Remove books from a private list owned by a user"""
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exit', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        lst = query_private_list_by_id(username, private_list_name)
        if lst is None:
            return 'Private List does not exit', 404

        body = request.get_json()
        existing_books = lst.books.split()
        for book in body.get('book_ids').split():
            if not existing_books.__contains__(book):
                return 'Book {} is not in the list'.format(book), 400
            existing_books.remove(book)
        lst.books = str(" ".join(existing_books))
        db.session.commit()
        return lst.serialize(), 200


def query_copy_by_id(copy_id):
    return db.session.query(models.Copy).filter_by(id=copy_id).first()


copy_api = Namespace('copy', description="copy operations")
book_vector.add_namespace(copy_api)

copy_marshaller = copy_api.model('Copy', {
    'user': fields.String(),
    'book_id': fields.Integer(),
})


@copy_api.route('')
@copy_api.response(404, 'User does not exist')
@copy_api.response(401, 'Unauthorized user')
class Copy(Resource):
    @copy_api.response(201, 'success')
    @copy_api.expect(copy_marshaller, validate=True)
    def post(self):
        """
        Add copy of a book to a user
        :return: Json format of a copy
        """
        body = request.get_json()
        username = body.get('user')
        user = query_user_by_name(username)
        if user is None:
            return 'User does not exist', 404
        if invalid_user(username):
            return 'Unauthorized User', 401
        book_id = body.get('book_id')
        if query_book_by_id(book_id) is None:
            return 'Book ID not found ' + str(book_id), 409
        new_copy = models.Copy()
        new_copy.parse_body(body)
        new_copy.status = BOOK_COPY_STATUS_AVAILABLE
        db.session.add(new_copy)
        db.session.commit()
        return new_copy.serialize(), 201

    @copy_api.response(200, 'success')
    def get(self):
        """Get all information of all book copies"""
        copies = db.session.query(models.Copy)
        return [copy.serialize() for copy in copies], 200


copy_query_parser = reqparse.RequestParser()
copy_query_parser.add_argument('copy_id', type=int, required=False)
copy_query_parser.add_argument('book_id', type=int, required=False)
copy_query_parser.add_argument('user', type=str, required=False)
copy_query_parser.add_argument('status', type=int, required=False)


@copy_api.route('/search')
@copy_api.response(200, 'success')
@copy_api.response(400, 'Parameters required')
class Copy(Resource):
    @copy_api.doc(body=copy_query_parser)
    def get(self):
        """
        Search copies of books by copy_id/book_id/username/status or combination search
        if no query params provided, return all copies
        :return:
        """
        copies = db.session.query(models.Copy)
        args = copy_query_parser.parse_args()
        copy_id = args['copy_id']
        if copy_id is not None:
            copies = copies.filter_by(id=copy_id)
        book_id = args['book_id']
        if book_id is not None:
            copies = copies.filter_by(book=book_id)

        username = args['user']
        if username is not None:
            copies = copies.filter_by(user=username)
        status = args["status"]
        if status is not None:
            copies = copies.filter_by(status=status)
        if copy_id is None and book_id is None and username is None and status is None:
            return 'Please proved searching parameter', 400
        return [copy.serialize() for copy in copies], 200


@copy_api.route('/<copy_id>')
@copy_api.doc(params={'copy_id': 'id of a copy'})
@copy_api.response(404, 'Copy of book not found')
@copy_api.response(200, 'success')
class Copy(Resource):

    @copy_api.response(401, 'Unauthorized user')
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


status_marshaller = copy_api.model('Status', {
    'status': fields.Integer()
})


@copy_api.route('/<copy_id>/updatestatus')
@copy_api.doc(params={'copy_id': 'id of a copy'})
@copy_api.response(404, 'Copy of book not found')
@copy_api.response(200, 'Success')
@copy_api.response(401, 'Unauthorized user')
class Copy(Resource):
    @copy_api.expect(status_marshaller, validate=True)
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


note_marshaller = copy_api.model('Note', {
    'note': fields.String()
})

note_marshaller_update = copy_api.model('Note_Update', {
    'note_id': fields.Integer(),
    'note': fields.String()
})


@copy_api.route('/<copy_id>/note')
@copy_api.doc(params={'copy_id': 'id of a copy'})
@copy_api.response(404, 'Copy of book not found')
@copy_api.response(401, 'Unauthorized user')
class Copy(Resource):
    @copy_api.response(200, 'Success')
    def get(self, copy_id):
        """Get all notes for a copy of a book"""
        checkCopyValidity(copy_id)
        copy_notes = db.session.query(models.Notes).filter_by(copy_id=copy_id)
        return [note.serialize() for note in copy_notes], 200

    @copy_api.response(201, 'Note successfully added ')
    @copy_api.expect(note_marshaller, validate=True)
    def post(self, copy_id):
        """Add a note to a copy of a book"""
        checkCopyValidity(copy_id)
        note_body = request.get_json()
        new_note = models.Notes()
        new_note.parse_body(note_body)
        new_note.copy_id = copy_id
        db.session.add(new_note)
        db.session.commit()
        return 'A note \"{}\" has been added to book copy of {}'.format(new_note.note, copy_id), 201

    @copy_api.response(200, 'Note updated successfully')
    @copy_api.response(400, 'Wrong note id input')
    @copy_api.expect(note_marshaller_update, validate=True)
    def put(self, copy_id):
        """Update a note for a book"""
        checkCopyValidity(copy_id)
        body = request.get_json()
        note_id = body.get('note_id')
        copy_note = db.session.query(models.Notes).filter_by(id=note_id).first()
        if copy_note is None:
            return 'Copy of the note not found', 404
        if str(copy_note.copy_id) != copy_id:
            return 'The note id does not belong to copy id of {}'.format(copy_id), 400
        copy_note.note = body.get('note')
        db.session.commit()
        return 'Note for copy book of {} has been updated'.format(copy_id)

    @copy_api.response(200, 'Note deleted successfully')
    def delete(self, copy_id):
        """Remove all notes for a copy of book"""
        checkCopyValidity(copy_id)
        # note_body = request.get_json()
        # note_id = note_body.get('note_id')
        # if note_id is None:
        #     notes = db.session.query(models.Notes).filter_by(copy_id=copy_id)
        #     db.session.delete(notes)
        #     db.session.commit()
        #     return 'Notes for book copy of {} has been all removed'.format(copy_id)
        notes = db.session.query(models.Notes).filter_by(copy_id=copy_id)
        if notes is None:
            return 'No notes found', 404
        notes.delete()
        db.session.commit()
        return 'Notes for book copy id {} has been removed.'.format(copy_id), 200


def checkCopyValidity(copy_id):
    copy = db.session.query(models.Copy).filter_by(id=copy_id).first()
    if copy is None:
        return 'copy is not found', 404
    if invalid_user(copy.user):
        return 'Unauthorized User', 401


order_api = Namespace('order', description="Order operations")
book_vector.add_namespace(order_api)

order_marshaller = order_api.model("Order", {
    'copy_id': fields.Integer(),
    'borrower': fields.String(),
    'copy_owner': fields.String(),
    'return_date': fields.DateTime(dt_format='iso8601')
})

order_query_parser = reqparse.RequestParser()
order_query_parser.add_argument('order_id', type=int, required=False)
order_query_parser.add_argument('copy_id', type=int, required=False)
order_query_parser.add_argument('borrower', type=str, required=False)
order_query_parser.add_argument('copy_owner', type=str, required=False)
order_query_parser.add_argument('order_status', type=int, required=False)
order_query_parser.add_argument('return_date', type=datetime, required=False)


@order_api.route('')
class Order(Resource):
    @order_api.response(200, 'Success')
    def get(self):
        """Get information about all orders"""
        orders = db.session.query(models.Order)
        return [order.serialize() for order in orders], 200

    @order_api.response(404, 'User not exist')
    @order_api.response(401, 'Unauthorized user')
    @order_api.response(409, 'Copy of id not found')
    @order_api.response(400, "Copy of book not available")
    @order_api.response(201, 'Order successfully posted')
    @order_api.expect(order_marshaller, validate=True)
    def post(self):
        """Make an order for a copy of book"""
        body = request.get_json()
        borrower = body.get('borrower')
        borrower = query_user_by_name(borrower)
        if borrower is None:
            return 'User does not exit', 404
        if invalid_user(borrower.username):
            return 'Unauthorized user, please login as a user/borrower', 401
        copy_id = body.get('copy_id')
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


@order_api.route('/search')
@order_api.response(200, 'Success')
@order_api.response(400, 'Searching parameters required')
class Order(Resource):
    @order_api.doc(body=order_query_parser)
    def get(self):
        """Search an order by id/copy_owner/borrower/order_status or combination search"""
        orders = db.session.query(models.Order)
        args = order_query_parser.parse_args()
        order_id = args['order_id']
        if order_id is not None:
            orders = orders.filter_by(id=order_id)
        copy = args['copy_id']
        if copy is not None:
            orders = orders.filter_by(copy=copy)
        borrower = args['borrower']
        if borrower is not None:
            orders = orders.filter_by(borrower=borrower)

        copy_owner = args['copy_owner']
        if copy_owner is not None:
            orders = orders.filter_by(copy_owner=copy_owner)

        status = args['order_status']
        if status is not None:
            orders = orders.filter_by(status=status)
        date = args['return_date']
        if date is not None:
            orders = orders.filter_by(expire=date)
        if id is None and copy is None and borrower is None and copy_owner is None and status is None:
            return 'Please provide searching parameters', 400

        return [order.serialize() for order in orders], 200


def change_order_status(order_id, status):
    order = db.session.query(models.Order).filter_by(id=order_id).first()
    if order is not None:
        order.status = status
        order.modified = datetime.utcnow()
        db.session.add(order)
        db.session.commit()
    return order


order_status_marshaller = order_api.model('OrderWithStatus', {
    'copy_id': fields.Integer(),
    'borrower': fields.String(),
    'copy_owner': fields.String(),
    'order_status': fields.Integer(),
    'return_date': fields.DateTime(dt_format='iso8601')
})


@order_api.route('/<order_id>/update')
class Order(Resource):
    @order_api.response(200, 'Order updated successfully')
    @order_api.response(404, 'Borrower not exist')
    # @order_api.response(401, 'Unauthorized user')
    @order_api.response(409, 'Copy of id not found')
    @order_api.response(400, "Copy of book not available")
    @order_api.response(400, 'Return date wrong')
    @order_api.expect(order_status_marshaller, validate=True)
    def put(self, order_id):
        """
        Update information of an order
        :return: Json format of an order
        """
        body = request.get_json()
        order = db.session.query(models.Order).filter_by(id=order_id).first()
        if order is None:
            return 'Order id not found', 400
        borrower = body.get('borrower')
        borrower = query_user_by_name(borrower)
        if borrower is None:
            return 'User does not exit in the system', 404
        # if invalid_user(borrower.username):
        #     return 'Unauthorized user, please login as a user/borrower', 401
        copy_id = body.get('copy_id')
        print(body)
        print(copy_id)
        copy = db.session.query(models.Copy).filter_by(id=copy_id).first()
        if copy is None:
            return 'Copy ID {} not found in system'.format(copy_id), 409
        elif copy.id != copy_id and copy.status == BOOK_COPY_STATUS_UNAVAILABLE:
            return 'The copy of the book is not available', 400
        copy_owner = body.get('copy_owner')
        owner = query_user_by_name(copy_owner)
        if owner is None:
            return 'Copy owner not found in the system'.format(copy_owner), 409
        # return_date = body.get('return_date')
        # if  datetime.strptime(return_date.isoformat()) < datetime.strptime(datetime.utcnow().isoformat()):
        #     return 'Return date should be later than today', 400
        status = body.get('order_status')
        if status is not None and status < 0 or status > 4:
            return 'Status should between 0-4', 400
        order.parse_body_status(body)
        copy = db.session.query(models.Copy).filter_by(id=order.copy).first()
        if order.status == ORDER_STATUS_COMPLETED or order.status == ORDER_STATUS_DECLINED:
            copy.status = BOOK_COPY_STATUS_AVAILABLE
        else:
            copy.status = BOOK_COPY_STATUS_UNAVAILABLE
        db.session.commit()
        return order.serialize(), 200


@order_api.route('/<order_id>/accept')
@order_api.doc(params={'order_id': 'id of an order'})
@order_api.response(404, 'Copy ID not found')
@order_api.response(401, 'Unauthorized user')
@order_api.response(201, 'Success')
class Order(Resource):
    def put(self, order_id):
        """Accept an order"""
        order = change_order_status(order_id, ORDER_STATUS_ACCPETED)
        if order is None:
            return 'Order ID not found ' + str(order_id), 404
        elif invalid_user(order.copy_owner):
            return 'Unauthorized User', 401
        copy = db.session.query(models.Copy).filter_by(id=order.copy).first()
        copy.status = BOOK_COPY_STATUS_UNAVAILABLE
        db.session.commit()
        return order.serialize(), 201


@order_api.route('/<order_id>/decline')
@order_api.doc(params={'order_id': 'id of an order'})
@order_api.response(404, 'Copy ID not found')
@order_api.response(401, 'Unauthorized user')
@order_api.response(201, 'Success')
class Order(Resource):
    def put(self, order_id):
        """Decline an order"""
        order = change_order_status(order_id, ORDER_STATUS_DECLINED)
        if order is None:
            return 'Order ID not found ' + str(order_id), 404
        elif invalid_user(order.copy_owner):
            return 'Unauthorized User', 401
        copy = db.session.query(models.Copy).filter_by(id=order.copy).first()
        copy.status = BOOK_COPY_STATUS_AVAILABLE
        db.session.commit()
        return order.serialize(), 201


@order_api.route('/<order_id>')
@order_api.doc(params={'order_id': 'id of an order'})
@order_api.response(404, 'Copy ID not found')
@order_api.response(200, 'Success')
class Order(Resource):
    def get(self, order_id):
        """Get information about an order"""
        order = db.session.query(models.Order).filter_by(id=order_id).first()
        if order is None:
            return 'Order does not exist', 404
        return order.serialize(), 200


book_return_parser = reqparse.RequestParser()
book_return_parser.add_argument('order_id', type=int, required=False)
book_return_parser.add_argument('copy_id', type=int, required=False)


@order_api.route('/return')
@order_api.response(200, 'Success')
@order_api.response(400, 'Too many parameters')
@order_api.response(404, 'copy id or order id not found')
class Order(Resource):
    @order_api.doc(body=book_return_parser)
    def post(self):
        """Return a book to complete an order, by providing an order id or copy id"""
        order = None
        args = book_return_parser.parse_args()
        order_id = args['order_id']
        copy_id = args['copy_id']
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
            return 'Copy of the book does not exist', 404
        order = change_order_status(order.id, ORDER_STATUS_COMPLETED)
        copy.status = BOOK_COPY_STATUS_AVAILABLE
        db.session.commit()
        return {'order': order.serialize(),
                'message': 'Book returned, Order completed!'}, 200


login_api = Namespace('login', description="Login operations")
book_vector.add_namespace(login_api)

login_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str, required=True, location='form')
login_parser.add_argument('password', type=str, required=True, location='form')

@login_api.route('')
@login_api.response(200, 'Success')
@login_api.response(404, 'Username not found')
@login_api.response(400, 'password wrong')
class Login(Resource):
    @login_api.doc(body=login_parser)
    def post(self):
        """Login as a user"""
        args = login_parser.parse_args()
        if request.form:
            username = request.form['username']
            password = request.form['password']
        else:
            username = args['username'] # form['username']
            password = args['password'] # form['password']

        return self.try_login(username, password)

    @login_api.response(200, 'successfully get login form')
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
        if registeredUser is None:
            return 'User not exist', 404
        if registeredUser.password != password:
            return 'Password not correct', 400
        if registeredUser is not None and registeredUser.password == password:
            registeredUser.authenticated = True
            login_user(registeredUser)
            return "Login Successfully: " + current_user.username, 200
        else:
            return abort(401)


register_api = Namespace('register', "Register operations")
book_vector.add_namespace(register_api)

reg_parser = reqparse.RequestParser()
reg_parser.add_argument('username', type=str, required=True, location='form')
reg_parser.add_argument('password', type=str, required=True, location='form')
reg_parser.add_argument('email', type=str, required=True, location='form')
reg_parser.add_argument('first_name', type=str, required=False, location='form')
reg_parser.add_argument('last_name', type=str, required=False, location='form')
reg_parser.add_argument('phone', type=str, required=False, location='form')

@register_api.route('/')
class Register(Resource):
    @register_api.response(201, "Registered Successfully")
    @register_api.response(409, 'User existed')
    @register_api.doc(body=reg_parser)
    def post(self):
        """Register as a user"""
        args = reg_parser.parse_args()
        username = args['username']
        password = args['password']
        email = args['email']
        first_name = args['first_name']
        last_name = args['last_name']
        phone = args['phone']

        if query_user_by_name(username) is not None:
            return 'User already exist', 409
        if username is None or password is None or email is None:
            return 'Username/password/email required', 400
        new_user = models.User(username=username,
                               password=password,
                               email=email or None,
                               first_name=first_name or None,
                               last_name=last_name or None,
                               phone=phone or None)
        db.session.add(new_user)
        db.session.commit()
        return Response("Registered Successfully", 201)

    @register_api.response(200, 'Register form get')
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
@login_api.response(200, 'Success')
class Logout(Resource):
    def delete(self):
        """Current user logout"""
        logout_user()
        return "Logout Successfully", 200


reminder_api = Namespace('reminder', description="Send reminder operations")
book_vector.add_namespace(reminder_api)


@reminder_api.route('/send/<days>')
@reminder_api.doc(params={'days': 'within the number of days to remind users to return books'})
@reminder_api.response(201, 'Success')
@reminder_api.response(200, 'No reminders needed to be sent')
@reminder_api.response(404, 'Error found')
@reminder_api.response(400, 'days should be > 0')
class Reminder(Resource):
    def post(self, days):
        """Send reminders to those need to return books within specific days from current time"""
        if int(days) <= 0:
            return 'Days can not be smaller than 0', 400
        cur_time = datetime.utcnow()
        expired_time = cur_time + timedelta(days=int(days))
        toSend = db.session.query(models.Order).filter_by(status=ORDER_STATUS_ACCPETED).filter(
            models.Order.expire >= cur_time,
            models.Order.expire <= expired_time)
        if toSend is None:
            return 'No reminders needed to be sent.', 200
        try:
            for record in toSend:
                email = query_user_by_name(record.borrower).email
                if email is None:
                    continue
                book_copy = query_copy_by_id(record.copy)
                book = query_book_by_id(book_copy.book)
                EmailSender.send_email(email, record.borrower, book.title, record.expire)
            return 'Reminders sent successfully!', 201
        except Exception as e:
            return 'Error in sending reminders', 404
