def send_email_alert(report, email):
    subject = '[Team 9]'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, report, email_from, recipient_list)


def send_whatsapp(report, phone):
    client = Client()
    FROM_WHATSAPP_NUMBER = "whatsapp:+14155238886"
    TO_WHATSAPP_NUMBER = "whatsapp:+6594516277"
    client.messages.create(body=report,
                           from_=FROM_WHATSAPP_NUMBER,
                           to=TO_WHATSAPP_NUMBER)


def send_whatsapp_alert(student_name, tweet, phone, verbose=True):
    print(phone)
    # kane:+65 94516277, giang:+65 94684096
    sid = 'AC85c805c874b2a1d1873ab9d612b6edcd'
    token = 'fc304b959047553288136fed2f57447d'
    FROM_WHATSAPP_NUMBER = "whatsapp:+14155238886"
    TO_WHATSAPP_NUMBER = f"whatsapp:+{phone}"
    # TO_WHATSAPP_NUMBER = "whatsapp:+6594516277"

    message = f'[Team 9] {student_name}\'s lastest tweet shows signs of self-harm:\n"{tweet}"'

    print(message)
 
    client = Client(sid, token)
    client.messages.create(body=message,
                           from_=FROM_WHATSAPP_NUMBER,
                           to=TO_WHATSAPP_NUMBER)
    if verbose:
        print('Sent alert message!')