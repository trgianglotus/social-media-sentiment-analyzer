

def get_ocr(media):
    analyze_url = 'https://westcentralus.api.cognitive.microsoft.com/' + "vision/v2.0/ocr"
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    params = {'language': 'en', 'detectOrientation': 'true'}
    media_ = {'url': media}
    response = requests.post(analyze_url, headers=headers,
                            params=params, json=media_)

    response.raise_for_status()
    res = response.json()

    full_text = ''
    for line in res['regions'][0]['lines']:
        words = line['words']
        for word in words:
            full_text += word['text'] + ' '

    return full_text


def get_image_sentiment(media):
    media_ = {'url': media}
    analyze_url = 'https://westcentralus.api.cognitive.microsoft.com/' + "vision/v2.0/analyze"
    headers = {'Ocp-Apim-Subscription-Key': '21785f73119e4e4193676daf4e495b39'}
    params = {'visualFeatures': 'Categories, Description, Color'}
    
    response = requests.post(analyze_url, headers=headers,
                    params=params, json=media_)

    analysis = response.json()
    if 'Black' in analysis['color']['dominantColors'] or 'Grey' in analysis['color']['dominantColors']:
        media_status = False
    else:
        media_status = True
    return media_status


def run_subprocess():
    wd = os.getcwd()
    os.chdir("/Users/nguyengiang/workspace/singagpore_india_hackathon/services/webapp/")
    subprocess.Popen("python3 manage.py process_tasks --queue stream-tweet", shell=True)
    os.chdir(wd)


def update_new_student(student, api):
    print('updating new student status')
    load_tweet(student.twitter_account, api)
    tweets = get_last_twenty_four_hours(student)
    if len(tweets) > 0:
        update_timing_score(tweets, student)    
        update_is_consistently_negative(tweets, student)   
        update_is_bipolar(tweets, student)


def update_student_wraper(student, api):
    update_thread = threading.Thread(target=update_new_student, args=[student, api])
    update_thread.start()


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


def check_email(email): 
    if(re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email)):  
        return True
    else:
        return False


def get_api(request):
    access_token = request.user.social_auth.get().extra_data['access_token']
    oauth_token = access_token['oauth_token']
    oauth_token_secret = access_token['oauth_token_secret']
    auth.set_access_token(oauth_token, oauth_token_secret)
    return tweepy.API(auth)


def get_update_status(request):
    print('getting update status')
    students = Student.objects.filter(caregiver=request.user)
    results = {}
    for student in students:
        tweets = get_last_twenty_four_hours(student)
  
        if len(tweets) > 0:
            update_timing_score(tweets, student)    
            update_is_consistently_negative(tweets, student)   
            update_is_bipolar(tweets, student)
            if (student.bipolarity + student.consistent_negativity + student.timing + student.suicidal) > 0:
                symptoms = []
                symptoms_ = ['bipolarity', 'consistent negativity', 'late night activity', 'suicidal thoughts']
                symptom_res = [student.bipolarity, student.consistent_negativity, student.timing, student.suicidal]
                for i, j in zip(symptoms_, symptom_res):
                    if j:
                        symptoms.append(i)
        results[student.name] = symptoms

    report = format_result(results)
    profile = Profile.objects.filter(user=request.user)[0]
    
    if profile.receive_email:
        if profile.email:
            send_email_alert(report, email)
            print('Sent email!')

    if profile.receive_message:
        if profile.phone:
            send_whatsapp(report, profile.phone)
            print('Sent message!')


def get_total_tweets(student):
    student.total_number_of_tweets = len(Tweet.objects.filter(student=student))
    return student.total_number_of_tweets


def get_last_twenty_four_hours(student):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    two_days_ago = tomorrow - datetime.timedelta(days=3)

    return Tweet.objects.filter(student=student, posted_date__range=[two_days_ago, tomorrow])


def update_is_consistently_negative(tweets, student, alpha=0.9, threshold=0.5):
    """ Latest tweets first , older posts are valued less"""
    combined_sentiment = [int(tweet.overall_status) for tweet in tweets]

    consistently_pos = sum([(alpha ** i) * sentiment for i, sentiment in
                            enumerate(combined_sentiment)]) / sum(
        [alpha ** i for i in range(len(combined_sentiment))])
    
    # print(student.consistent_negativity, consistently_pos)
    student.consistent_negativity = (1 - consistently_pos) >= threshold
    student.save()


def update_is_bipolar(tweets, student, threshold=0.3):
    """ Latest tweets first"""
    combined_sentiment = [int(tweet.overall_status) for tweet in tweets]
    print(combined_sentiment)
    changes = [abs(combined_sentiment[i] - combined_sentiment[i + 1]) for i in range(len(combined_sentiment) - 1)]

    if len(changes) > 0:
        student.bipolarity = sum(changes) / len(changes) >= threshold
    student.save()