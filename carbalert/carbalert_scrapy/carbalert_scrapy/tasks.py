from celery import Celery
from celery.utils.log import get_task_logger
import smtplib


logger = get_task_logger(__name__)
app = Celery('tasks')
app.conf.broker_url = 'redis://localhost:6379/0'

@app.task
def send_email_notification(phrases, title, text, thread_url, thread_datetime):
    TO = 'dino@dinofizzotti.com'
    subject = f"CARBALERT: {title}"

    phrase_list = ""

    for phrase in phrases:
        phrase_list += f"{phrase}\n"

    text = f"{phrase_list}\n{thread_datetime}\n\n{title}\n\n{text}\n\n{thread_url}"

    gmail_sender = 'carbalertnotification'
    gmail_passwd = 'Tcsdgc$H@77hErWR'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)

    body = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % subject,
                        '', text])

    try:
        server.sendmail(gmail_sender, [TO], body)
        logger.info('email sent')
    except:
        logger.error('error sending mail')

    server.quit()
