import smtplib
from constant import *


class EmailSender:
    @classmethod
    def send_email(cls, email_rec, user_name, book_name, return_date):
        msg = '''\nDear {},\n
        This is a kind reminder that you need to return the book {} by the date of {}.\n'''.format(user_name, book_name,
                                                                                                   return_date)
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            message = "Subject : {}\n\n{}".format("Reminder: Return the book", msg)
            server.sendmail(EMAIL_ADDRESS, email_rec, message)
            server.quit()
            return True
        except:
            return False
