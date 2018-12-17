# CS5500 Book Library Web Service by Jiahuan Yu, Xianyin Chen
The server was deployed on https://book-vector.herokuapp.com/

By using this sever, you can:
1. register as a user, and then login to do operations, then logout
2. add/update/remove a book to the library server
3. search a book by year/category/author or any combination search
4. add/remove/update different lists of books for a user

 To deal with loaning books, we use COPY of book
 
5. add/remove/update copy (associated with book_id) to a user (which means a user owned it)
6. add/remove/update note for a copy
7. make/accept/decline an order(which means to loan a book)
8. return a book (make order status complete)
9. check if a copy of book is loaned/not_loaned/damage/lost
10. Send email to users to remind them to return the book by some date
