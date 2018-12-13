import smtplib
from constant import *
import traceback

class EmailSender:
    @classmethod
    def send_email(cls, email_rec, user_name, book_name, return_date):
        msg = '''\nDear {},\n
        This is a kind reminder that you need to return the book: {} \n by the date of {}.\n
        Best Regards,\n
        From Book Vector Team\n'''.format(user_name, book_name, return_date.strftime("%Y-%m-%d %H:%M:%S"))
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            message = "Subject : {}\n\n{}".format("(Non Reply)Reminder: Return the book", msg)
            server.sendmail(EMAIL_ADDRESS, email_rec, message)
            server.quit()
            return True
        except Exception as e:
            try:
                raise TypeError("Error")
            except:
                pass
            traceback.print_exc()
            return False
