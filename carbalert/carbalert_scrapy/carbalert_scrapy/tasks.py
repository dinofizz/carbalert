from email.header import Header
from email.mime.text import MIMEText

from celery import Celery, bootsteps
from celery.utils.log import get_task_logger
import smtplib


def add_worker_arguments(parser):
    parser.add_argument(
        '--email', default=False,
        help='Enable custom option.',
    ),
    parser.add_argument(
        '--password', default=False,
        help='Enable custom option.',
    ),


class SaveSenderEmailAddress(bootsteps.Step):

    def __init__(self, worker, email, **options):
        if email:
            worker.app.sender_email_address = email


class SaveSenderEmailAddressPassword(bootsteps.Step):

    def __init__(self, worker, password, **options):
        if password:
            worker.app.sender_email_address_password = password


logger = get_task_logger(__name__)
app = Celery('tasks')
app.conf.broker_url = 'redis://localhost:6379/0'
app.user_options['worker'].add(add_worker_arguments)
app.steps['worker'].add(SaveSenderEmailAddress)
app.steps['worker'].add(SaveSenderEmailAddressPassword)


@app.task
def send_email_notification(email_address, phrases, title, text, thread_url, thread_datetime):
    logger.info(f"Received alert for {email_address} for thread title: {title}")
    subject = f"CARBALERT: {title}"

    phrase_list = ""

    for phrase in phrases:
        phrase_list += f"{phrase}\n"

    text = f"{phrase_list}\n{thread_datetime}\n\n{title}\n\n{text}\n\n{thread_url}"

    gmail_sender = app.sender_email_address
    gmail_passwd = app.sender_email_address_password

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)

    msg = MIMEText(text, _charset="UTF-8")
    msg['Subject'] = Header(subject, "utf-8")
    msg['To'] = email_address

    try:
        server.sendmail(gmail_sender, [email_address], msg.as_string())
        expanded_phrases = " ".join(phrases)
        logger.info(f"email sent to {email_address} for search phrase(s): {expanded_phrases}")
    except Exception as ex:
        logger.error(ex)
        logger.error('error sending mail')

    server.quit()