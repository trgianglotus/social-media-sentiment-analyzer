import datetime
import json
import tweepy
import pytesseract
import requests
import urllib.request
import cv2
import datetime
import numpy as np
import requests
import re
import subprocess
import os
import threading

from time import sleep
from random import randint
from PIL import Image
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.test import selenium
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from twilio.twiml.messaging_response import Message, MessagingResponse

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API, Stream
from django_tables2.export.views import ExportMixin
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from background_task import background
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .tables import StudentTable
from .models import Student, Tweet, Profile, SelfHarmTweet
from .filters import StudentFilter
from .forms import NewStudentForm
from .nlp_engine.sentiment_analyser import SentimentAnalyser
from .nlp_engine.suicide_alert import get_self_harm
from .utils.wordcloud import get_word_cloud
# from .utils.encryption import AESCipher


consumer_key = 'Ktg8h5ZIHOnd4EHbTqC1Xpgob'
consumer_secret = 'lBC0PvbMG7Wmm6h6CEcNof6iKMlciz82RugA3MaVk4PQzbwOrv'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

endpoint = 'https://westcentralus.api.cognitive.microsoft.com/vision/v2.0'
subscription_key = '21785f73119e4e4193676daf4e495b39'
remote_image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg"
analyze_url = 'https://westcentralus.api.cognitive.microsoft.com/' + "vision/v2.0/analyze"

headers = {'Ocp-Apim-Subscription-Key': '21785f73119e4e4193676daf4e495b39'}
params = {'visualFeatures': 'Categories, Description, Color'}


class FilteredStudentListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView):
    model = Student
    table_class = StudentTable
    filterset_class = StudentFilter
    template_name = "dashboard/all_students.html"
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return Student.objects.filter(caregiver=user).order_by('-updated_date')


def classboard_test(request):
    return render(request, 'dashboard/dashboard_testing.html')


@login_required
def search_student(request):
    if request.method == 'POST':
        search_name = request.POST['name'].strip('@').lower()
        students = Student.objects.filter(caregiver=request.user, name__icontains=search_name).order_by('-updated_date')
        longer = len(students) // 3
        students_longer = students[:3*longer]

        three_students = []
        three_students_groups = []
        for student in students_longer:
            three_students.append(student)
            if len(three_students) == 3:
                three_students_groups.append(tuple(three_students))
                three_students = []
        
        less_than_three_groups = students[3*longer:]

        two_remaining_students = len(less_than_three_groups) > 1

        if two_remaining_students:
            less_than_three_groups = [less_than_three_groups]

        not_found = False
        if len(students_longer) == len(less_than_three_groups) == 0:
            not_found = True

        # Get summary results
        n_student = len(students)

        bipo = 0
        night = 0
        nega = 0
        s_harm = 0
        t_tweet = 0
        n_tweet = 0
        sh_tweet = 0

        for student in students:
            if student.bipolarity:
                bipo += 1
            if student.timing:
                night += 1
            if student.consistent_negativity:
                nega += 1
            if student.suicidal:
                s_harm += 1
            
            n_tweet += student.number_of_n_tweets
            t_tweet += student.total_number_of_tweets
            sh_tweet += student.number_of_sh_tweets

        summary = {
            'n_student': n_student,
            'bipo': bipo,
            'night': night,
            'nega': nega,
            's_harm': s_harm,
            'n_tweet': n_tweet,
            't_tweet': t_tweet,
            'p_tweet': t_tweet - n_tweet,
        }
        profile = Profile.objects.filter(user=request.user)[0]

        return render(request, 'dashboard/all_students.html', {'students': students, 
                                                                'three_students_groups': three_students_groups, 
                                                                'less_than_three_groups': less_than_three_groups,
                                                                'two_remaining_students': two_remaining_students,
                                                                'not_found': not_found,
                                                                'summary': summary,
                                                                'caregiver': profile,
                                                                })
    return redirect('all-students')


@login_required
def all_students(request):
    students = Student.objects.filter(caregiver=request.user).order_by('-updated_date')
    longer = len(students) // 3
    students_longer = students[:3*longer]

    three_students = []
    three_students_groups = []
    for student in students_longer:
        three_students.append(student)
        if len(three_students) == 3:
            three_students_groups.append(tuple(three_students))
            three_students = []

    n_student = len(students)

    bipo = 0
    night = 0
    nega = 0
    s_harm = 0
    t_tweet = 0
    n_tweet = 0

    for student in students:
        if student.bipolarity:
            bipo += 1
        if student.timing:
            night += 1
        if student.consistent_negativity:
            nega += 1
        if student.suicidal:
            s_harm += 1
        
        n_tweet += student.number_of_n_tweets
        t_tweet += student.total_number_of_tweets

    summary = {
        'n_student': n_student,
        'bipo': bipo,
        'night': night,
        'nega': nega,
        's_harm': s_harm,
        'n_tweet': n_tweet,
        't_tweet': t_tweet,
        'p_tweet': t_tweet - n_tweet,
    }
    
    less_than_three_groups = students[3*longer:]

    two_remaining_students = len(less_than_three_groups) > 1
    if two_remaining_students:
        less_than_three_groups = [less_than_three_groups]

    not_found = False
    if len(students_longer) == len(less_than_three_groups) == 0:
        not_found = True
    

    profile = Profile.objects.filter(user=request.user)[0]
    return render(request, 'dashboard/all_students.html', {'students': students, 
                                                                'three_students_groups': three_students_groups, 
                                                                'less_than_three_groups': less_than_three_groups,
                                                                'two_remaining_students': two_remaining_students,
                                                                'not_found': not_found,
                                                                'summary': summary,
                                                                'caregiver': profile,
                                                                })


@login_required
def alert_message(request): 
    profile = Profile.objects.filter(user=request.user)[0]
    profile.receive_alert = not profile.receive_alert
    profile.save()
    return redirect('all-students')


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    tweets = Tweet.objects.filter(student=student).order_by('-posted_date')
    profile = Profile.objects.filter(user=request.user)[0]
    return render(request, "dashboard/student_detail.html", {"student": student,
                                                             "tweets": tweets, 
                                                             'caregiver': profile,
                                                             })


def login(request):
    if not request.user.is_authenticated:
        return render(request, 'dashboard/login_grid.html')
    else:
        return redirect('login')


def load_student(request):
    if request.user.is_authenticated:
        # client = TwitterClient(request)
        # oauth_token, oauth_token_secret = client.get_oauth_tokens()
        
        # following = [str(student.uid) for student in students]
        # print(following)
        # stream_tweet(oauth_token, oauth_token_secret, following)
        # # Update streamer
        # run_subprocess()
        # print('FINISHED STREAMING')
        auto_report()
        # res = get_tweet_by_month(request, 3)

    return redirect('all-students')


@login_required
def check_phone(request):
    profile = Profile.objects.filter(user=request.user)
    if len(profile) == 0:
        Profile(user=request.user).save()
        return redirect('all-students')

    update_streamer(request)
    return redirect('all-students')


@login_required
def enter_phone(request):
    phone = request.POST['phone'].strip('+')
    if not phone.isnumeric():
        return redirect('all-students')
    else: 
        profile = Profile.objects.filter(user=request.user)[0]
        profile.phone = phone
        profile.save()
        return redirect('all-students')


@login_required
def enter_days(request):
    days = request.POST['days']
    if not days.isnumeric():
        return redirect('all-students')
    else: 
        profile = Profile.objects.filter(user=request.user)[0]
        difference = profile.days - profile.days_left
        profile.days = days
        if difference > 0:
            profile.days_left = profile.days - difference
        else:
            profile.days_left = profile.days
        profile.save()
        return redirect('all-students')


@login_required
def enter_email(request):
    email = request.POST['email'].strip('+')

    if check_email(email):
        profile = Profile.objects.filter(user=request.user)[0]        
        profile.user.email = email
        profile.user.save()
        return redirect('all-students')
    else: 
        return redirect('all-students')


@login_required
def update_receive_m(request):
    profile = Profile.objects.filter(user=request.user)[0]
    profile.receive_message = not profile.receive_message
    profile.save()
    return redirect('all-students')


@login_required
def update_receive_e(request):
    profile = Profile.objects.filter(user=request.user)[0]
    profile.receive_email = not profile.receive_email
    profile.save()
    return redirect('all-students')


@login_required
def redirect_twitter(request, account):
    return redirect('https://twitter.com/' + account)


@login_required
def delete_student(request, pk):
    Student.objects.filter(id=pk).delete()
    return redirect('all-students')


@login_required
def add_student(request):
    if request.method == 'POST':
        form = NewStudentForm(request.POST)

        if form.is_valid():
            twitter_account = request.POST['name'].strip('@').lower()

            if not Student.objects.filter(twitter_account=twitter_account, caregiver=request.user).count() > 0:
                api = get_api(request)
                try:
                    new_student = api.lookup_users(screen_names=[twitter_account])[0]._json

                    path_to_wc = 'img/' + new_student['screen_name'].lower() + '.jpg'
                    student = Student(name=new_student['name'],
                            uid=new_student['id'],
                            twitter_account=new_student['screen_name'].lower(),
                            caregiver=request.user,
                            wordcloud=path_to_wc)

                    student.save()
                    print(f'Added {twitter_account}!')

                    print('getting update status')
                    profile = Profile.objects.filter(user=request.user)[0]
                    update_student_wraper(student, api, request, profile.days)
                    print(f'Updated all tweets in the last {profile.days} days')
            

                    print('Updated streamer')

                except Exception as e:
                    # Do something here
                    print(f'WARNING: EXCEPTION RAISED{e}')
                    return redirect('all-students')
        else:
            # Do something here
            pass
    return redirect('all-students')


def get_post_date_time(data):
    table = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
                'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    ts = data['created_at'].split(' ')
    time = ts[3].split(':')

    return datetime.datetime(year=int(ts[5]), month=table[ts[1]], day=int(ts[2]), 
                            hour=int(time[0]), minute=int(time[1]), second=int(time[2]))
    

class TwitterClient(object):
    def __init__(self, request):
        self.consumer_key = 'Ktg8h5ZIHOnd4EHbTqC1Xpgob'
        self.consumer_secret = 'lBC0PvbMG7Wmm6h6CEcNof6iKMlciz82RugA3MaVk4PQzbwOrv'
        self.access_token = request.user.social_auth.get().extra_data['access_token']
        
    def get_oauth_tokens(self):
        oauth_token = self.access_token['oauth_token']
        oauth_token_secret = self.access_token['oauth_token_secret']
        return oauth_token, oauth_token_secret

    def get_auth(self):
        return tweepy.OAuthHandler(self.consumer_key, \
                                    self.consumer_secret).set_access_token(\
                                        self.access_token['oauth_token'], \
                                        self.access_token['oauth_token_secret'])


class TweetListener(StreamListener):
    def __init__(self):
        StreamListener.__init__(self)
        self.analyser = SentimentAnalyser()
        self.balancer = OcrBalancer()

    def on_error(self, status_code):
        print(status_code)
        return False

    def on_data(self, raw_data):
        data = json.loads(raw_data)
        save_tweet(self.analyser, self.balancer, data)


def load_tweet(screen_name, api, days=7):
    analyzer = SentimentAnalyser()
    balancer = OcrBalancer()
    for status in tweepy.Cursor(api.user_timeline, screen_name=screen_name).items():
        data = status._json
        posted_date_time = get_post_date_time(data)
        time_delta = datetime.date.today() - posted_date_time.date()

        if time_delta.days > days:
            break
        
        if not Tweet.objects.filter(posted_date=posted_date_time).count() > 0:
            save_tweet(analyzer, balancer, data)


def save_tweet(analyzer ,balancer, data):
    if not is_delete(data):
        if is_retweet(data):
            return None
            # Handle exception too many values to unpack
            text, media, student = extract_data_retweet(data)
        else:
            text, media, student, url_ = extract_data(data)

        ocr_res = ''
        media_status = None
        # print(f'MEDIA: {media}')
        if media is not None:
            with urllib.request.urlopen(media) as url:
                image_np = np.asarray(bytearray(url.read()), dtype="uint8")
                image = cv2.imdecode(image_np, cv2.IMREAD_GRAYSCALE)
            try:
                ocr_res = balancer.get_ocr(media)
            except:
                print('429 RAISED')

            print(ocr_res)
            
            media_status = get_image_sentiment(media) or analyzer.predict(ocr_res)
            
            # true: not depressed
            # print('================IMAGE SENTIMENT RESULT================', '\n')
            # print('Depressed: ' + str(not media_status), '\n')

        # print('================TEXT ANALYZER RESULT================', '\n')
        text = text.strip(url_)
        text_status = analyzer.predict(text)
        # print('Depressed: ' + str(not text_status), '\n')
        if text == '' and ocr_res != '':
            text = ocr_res

        if media:
            overall_status = text_status or media_status
        else: 
            overall_status = text_status
        
        posted_date = get_post_date_time(data)

        tokens = analyzer.tokenized_text

        s_harm = get_self_harm(tokens)

        if s_harm:
            text_status = True

        new_tweet = Tweet(text=text, media=media, student=student, 
                text_status=text_status, posted_date=posted_date, 
                media_status=media_status, overall_status=overall_status,
                s_harm=s_harm)
        
        new_tweet.save()
        student.total_number_of_tweets += 1

        student.save()
        
        if not overall_status:
            student.number_of_n_tweets += 1

        if s_harm:
            SelfHarmTweet(tweet=new_tweet, student=student).save()
            profile = Profile.objects.filter(user=student.caregiver)[0]
            student.suicidal = True
            student.number_of_sh_tweets += 1

            if profile.receive_alert and profile.phone and check_self_harm(new_tweet.posted_date):

                send_whatsapp_alert(student_name=student.name, tweet=text, phone=profile.phone)
            # generate_call(student_name=student.name, tweet=text, phone=profile.phone)
        
        tweets = get_tweet_by_time(student, 7)
        wordcloud_wraper(tweets, student.twitter_account)
        
        student.save()
        print(f'total # of tweets: {student.total_number_of_tweets}')
        print(f'Added a new tweet from {student.twitter_account}!')


def is_delete(data):
    try:
        data['delete']
        return True
    except:
        return False


def is_retweet(data):
    try:
        data['retweeted_status']
        return True
    except:
        return False


def extract_data(data):
    url = None
    try:
        text = data['extended_tweet']['full_text']
        try:
            # If video available
            media = data['extended_tweet']['extended_entities']['media'][0]['video_info']['variants'][0]
        except:
            try:
                # If image available
                media = data['extended_tweet']['extended_entities']['media'][0]['media_url']
                try:
                    url = data['extended_tweet']['extended_entities']['media'][0]['url']
                except:
                    url = None
            except:
                media = None
    except:
        text = data['text']
        try:
            # If video available
            media = data['entities']['media'][0]['media_url']
            try:
                url = data['entities']['media'][0]['url']
            except:
                url = None
        except:
            media = None

    twitter_account = data['user']['screen_name'].lower()

    student = None
    try:
        student = Student.objects.filter(twitter_account=twitter_account)[0]
    except:
        print(twitter_account, '\n')

    return text, media, student, url


def extract_data_retweet(data):
    try:
        text, media, _ = extract_data(data['retweeted_status'])
        twitter_account = data['user']['screen_name'].lower()
        student = Student.objects.filter(twitter_account=twitter_account)[0]
    except:
        print(extract_data(data['retweeted_status']))
        

    return text, media, student


def update_timing_score(tweets, student):
    before_three_am = datetime.time(4, 0, 0)
    after_eleven_pm = datetime.time(23, 0, 0)
    
    count = 0
    for tweet in tweets:
        if before_three_am > tweet.posted_date.time() > after_eleven_pm:
            count += 1
    
    student.timing = count / len(tweets) > 0.5
    student.save()


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


def get_total_tweets(student):
    student.total_number_of_tweets = len(Tweet.objects.filter(student=student))
    return student.total_number_of_tweets


def get_last_twenty_four_hours(student):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    two_days_ago = tomorrow - datetime.timedelta(days=3)

    return Tweet.objects.filter(student=student, posted_date__range=[two_days_ago, tomorrow])


def get_tweet_by_time(student, days=7):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    two_days_ago = tomorrow - datetime.timedelta(days=days+1)

    return Tweet.objects.filter(student=student, posted_date__range=[two_days_ago, tomorrow])


def get_tweet_by_month(students, preriod=3):
    
    res = []
    months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}    
    now = datetime.datetime.now()
    c_year = now.year
    c_month = now.month

    for m in range(preriod):
        s = 0 
        n = 0
        curr_month = datetime.datetime(year=c_year, month=c_month - m, day=1)
        next_month = datetime.datetime(year=c_year, month=c_month - m + 1, day=1)
        for student in students:
            tweets = Tweet.objects.filter(student=student, posted_date__range=[curr_month, next_month])
            for tweet in tweets:
                if not tweet.overall_status:
                    n += 1
                s += 1
        percentage = 100*n/s if s != 0 else 0

        res.append((months[c_month - m], percentage))
    
    return res[::-1]


# @background(schedule=0)
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


@background(schedule=0, queue='stream-tweet')
def stream_tweet(oauth_token, oauth_token_secret, following):
    auth.set_access_token(oauth_token, oauth_token_secret)
    tweet_listener = TweetListener()
    twitterStream = Stream(auth, tweet_listener)
    twitterStream.filter(follow=following)


def get_api(request):
    access_token = request.user.social_auth.get().extra_data['access_token']
    oauth_token = access_token['oauth_token']
    oauth_token_secret = access_token['oauth_token_secret']
    auth.set_access_token(oauth_token, oauth_token_secret)
    return tweepy.API(auth)


class ChartData(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        pc_labels, pc_data = [3, 40]
        pc_labels = ["Negative tweets", "Positive tweets"]

        students = Student.objects.filter(caregiver=request.user)
        res = get_tweet_by_month(students, 6)
        l_labels = []
        l_data = []
        for label, data in res:
            l_labels.append(label)
            l_data.append(data)

        data = {
            'pc_labels': pc_labels,
            'pc_data': pc_data,

            'l_labels': l_labels,
            'l_data': l_data
        }
        return Response(data)


class ChartDataDetail(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):        
        students = Student.objects.filter(pk=pk)
        print(pk)
        pc_labels, pc_data = [3, 40]
        pc_labels = ["Negative tweets", "Positive tweets"]

        res = get_tweet_by_month(students, 6)
        l_labels = []
        l_data = []
        for label, data in res:
            l_labels.append(label)
            l_data.append(data)

        data = {
            'pc_labels': pc_labels,
            'pc_data': pc_data,

            'l_labels': l_labels,
            'l_data': l_data
        }
        return Response(data)


class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_providers(self):
        return ["Central", "Eastside", "Westside"]

    def get_data(self):
        return [[75, 44, 92, 11, 44, 95, 35],
                [41, 92, 18, 3, 73, 87, 92],
                [87, 21, 94, 3, 90, 13, 65]]


line_chart = TemplateView.as_view(template_name='dashboard/chart.html')
line_chart_json = LineChartJSONView.as_view()


def send_email_alert(report, email):
    subject = '[Team 9]'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, report, email_from, recipient_list)


def send_whatsapp(report, phone):
    sid = 'AC2fe7b172c7f34cc39a79475346d69da6'
    token = '0a6047b7f6f8c13bf7053f7129a598bf'
    client = Client(sid, token)
    FROM_WHATSAPP_NUMBER = "whatsapp:+14155238886"
    TO_WHATSAPP_NUMBER = f"whatsapp:+{phone}"
    client.messages.create(body=report,
                           from_=FROM_WHATSAPP_NUMBER,
                           to=TO_WHATSAPP_NUMBER)


def send_whatsapp_alert(student_name, tweet, phone, verbose=True):
    sid = 'AC2fe7b172c7f34cc39a79475346d69da6'
    token = '0a6047b7f6f8c13bf7053f7129a598bf'
    FROM_WHATSAPP_NUMBER = "whatsapp:+14155238886" # kane:+65 94516277, giang:+65 94684096
    if not phone:
        print('ADD PHONE NUMBER TO SEND MESSAGE')
        return
        
    TO_WHATSAPP_NUMBER = f"whatsapp:+{phone}"  # TO_WHATSAPP_NUMBER = "whatsapp:+6594516277"
   
    message = f'[Team 9] {student_name}\'s lastest tweet shows signs of self-harm:\n"{tweet}"'
 
    client = Client(sid, token)
    client.messages.create(body=message,
                           from_=FROM_WHATSAPP_NUMBER,
                           to=TO_WHATSAPP_NUMBER)
    if verbose:
        print('Sent alert message!')


def generate_call(student_name, tweet, phone, verbose=True):
    sid = 'AC2fe7b172c7f34cc39a79475346d69da6'
    token = '0a6047b7f6f8c13bf7053f7129a598bf'
    FROM_WHATSAPP_NUMBER = "+13343264842"
    client = Client(sid, token)

    call = client.calls.create(
        url='http://e6cb5c05.ngrok.io/call_response/',
        to=f'+{phone}',
        from_=FROM_WHATSAPP_NUMBER
        )


def check_email(email):
    if(re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email)):  
        return True
    else:
        return False


def get_ocr(media):
    sleep(0.3)
    analyze_url = 'https://westcentralus.api.cognitive.microsoft.com/' + "vision/v2.0/ocr"
    analyze_url2 = 'https://westcentralus.api.cognitive.microsoft.com/' + "vision/v1.0/ocr"
    analyze_url3 = 'https://westcentralus.api.cognitive.microsoft.com/' + "vision/v2.1/ocr"

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
    media_status = True
    media_ = {'url': media}
    analyze_url = 'https://westcentralus.api.cognitive.microsoft.com/' + "vision/v2.0/analyze"
    headers = {'Ocp-Apim-Subscription-Key': '21785f73119e4e4193676daf4e495b39'}
    params = {'visualFeatures': 'Categories, Description, Color'}
    
    response = requests.post(analyze_url, headers=headers,
                    params=params, json=media_)

    analysis = response.json()
    print(f'IMAGE SENTIMENT: \n{analysis}')
    try:
        if 'Black' in analysis['color']['dominantColors'] or 'Grey' in analysis['color']['dominantColors']:
            media_status = False
        else:
            media_status = True
    except:
        print('KEY ERROR RAISED')
        sleep(31)
        get_image_sentiment(media)

    return media_status


def run_subprocess():
    wd = os.getcwd()
    work_dir = wd.replace('dashboard','')
    os.chdir(work_dir)
    subprocess.Popen("pkill -f stream-tweet", shell=True)
    sleep(1)
    subprocess.Popen("python3 manage.py process_tasks --queue stream-tweet", shell=True)
    os.chdir(wd)


def update_new_student(student, api, request, days=7):    
    # print('Updating student')
    load_tweet(student.twitter_account, api, days)
    student = Student.objects.filter(twitter_account=student.twitter_account)[0]
    print(f'Total number of tweets after loading tweets {student.total_number_of_tweets}')
    tweets = get_tweet_by_time(student, days)
    wordcloud_wraper(tweets, student.twitter_account)
    update_streamer(request)

    if len(tweets) > 0:
        update_timing_score(tweets, student)    
        update_is_consistently_negative(tweets, student)   
        update_is_bipolar(tweets, student)


def update_student_wraper(student, api,request, days):
    update_thread = threading.Thread(target=update_new_student, args=[student, api, request, days])
    update_thread.start()


def wordcloud_wraper(tweets, twitter_account):
    fulltext = ''
    for tweet in tweets:
        fulltext = fulltext + ' ' + tweet.text
    
    fulltext = SentimentAnalyser.clean_text(fulltext)
    
    # print('Getting wordcloud')
    get_word_cloud(fulltext, twitter_account)


class OcrBalancer():
    def __init__(self):
        self.last_use = 0
        self.count0 = 0
        self.count1 = 0
        self.count2 = 0

    def get_ocr(self, media):
        print(f'Using endpoint: {self.last_use}')

        if self.last_use == 2:
            analyze_url = 'https://westcentralus.api.cognitive.microsoft.com/' + "vision/v2.0/ocr"
            self.last_use = 0
            self.count0 += 1

        elif self.last_use == 0:
            analyze_url = 'https://westcentralus.api.cognitive.microsoft.com/' + "vision/v1.0/ocr"
            self.last_use = 2
            self.count1 += 1
        else:
            analyze_url = 'https://westcentralus.api.cognitive.microsoft.com/' + "vision/v2.1/ocr"
            self.last_use = 2
            self.count2 += 1

        # print(f'Switched to endpoint: {self.last_use}')
        # print(f'count 0: {self.count0}')
        # print(f'count 1: {self.count1}')
        # print(f'count 2: {self.count2}')

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
    

@background(schedule=86400, queue="auto-report")
def auto_report():
    users = User.objects.all()
    print(users)
    print('Hi')
    for user in users:
        profile = Profile.objects.filter(user=user)[0]
        if profile.days_left == 0:
            students = Student.objects.filter(caregiver=user)
            results = get_user_data(students=students, days=profile.days)
            report = generate_caregiver_message(results)
            send_whatsapp(report, profile.phone)
            profile.days_left = profile.days
            profile.save()
            print(f'Automatically reported to {user.username}')
        else:
            profile.days_left -= 1
            profile.save()
        


@csrf_exempt
def incoming_message(request):
    data = request.POST
    data = data.dict()
   
    phone = data['From'].strip('whatsapp:+')
    profile = Profile.objects.filter(phone=phone)[0]
    user = profile.user
    message = data['Body']
    student_names, symptom = parse_user_request(message)
    
    print(symptom)
    found_symptom = False

    if symptom is None:
        students = Student.objects.filter(caregiver=user)
    elif symptom == 'bipolarity':
        students = Student.objects.filter(caregiver=user, bipolarity=True)
        found_symptom = True
    elif symptom == 'night use':
        students = Student.objects.filter(caregiver=user, consistent_negativity=True)
        found_symptom = True
    elif symptom == 'negativity':
        students = Student.objects.filter(caregiver=user, timing=True)
        found_symptom = True
    elif symptom == 'self harm':
        students = Student.objects.filter(caregiver=user, suicidal=True)
        found_symptom = True
    else:
        students = Student.objects.filter(caregiver=user, twitter_account__in=student_names)

    results = get_user_data(students=students, days=7)

    if len(results)==0 and found_symptom:
        reply = f'No student experiencing "{symptom}""'

    elif len(results)==0 and not found_symptom:
        reply = 'I didn\'t get that.\nType in the format:\n\nstudent1, student2\n*OR*\nOne of the following: \
all students, bipolarity, night use, negativity, self harm'
        # *OR*\nstudent1, student2 / <No of days>'
    else:
        reply = generate_caregiver_message(results, symptom)

    resp = MessagingResponse()  
    resp.message(reply)
    return HttpResponse(str(resp))


def get_user_data(students, days=7):
    results = {}
    for student in students:
        results[student.name] = tuple([student.consistent_negativity,
                                        student.bipolarity,
                                        student.timing,
                                        student.suicidal])
    
    return results


def parse_user_request(raw_text):
    """ input example: 'StuDenT1, Student2 / 2' OR 'StuDenT1, Student2' """
    raw_text = raw_text.lower()
    
    if raw_text == 'all students':
        return None, None

    elif raw_text == 'bipolarity':
        return None, raw_text

    elif raw_text == 'night use':
        return None, raw_text

    elif raw_text == 'negativity':
        return None, raw_text

    elif raw_text == 'self harm':
        return None, raw_text

    text_chunks = [word.strip() for word in raw_text.split("/")]
    
    users = []
    time = 1
    
    if len(text_chunks)==1:
        users  =  [word.strip() for word in text_chunks[0].split(",")]
        time = 1 # 1 day
    elif len(text_chunks)==2:
        users  =  [word.strip() for word in text_chunks[0].split(",")]
        time = text_chunks[1]
    
    try:
        time = int(time)
    except:
        time = 1
    
    return (users, time)
    

def generate_caregiver_message(dict_student_params, symptom=None):
    """ input example: {'student1': (1,0,0,1), student2 : (0,0,0,1) ,...} """
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not symptom:
        result_string  = f"Students Wellbeing Report \n{time}\n"
    else:
        result_string  = f"{time}\nShowing all students with signs of {symptom}\n"
    
    param_keys = ['Negativity', 'Bipolarity', 'Night Use', 'Self Harm']
    
    for student in dict_student_params.keys():
        result_string += "-"*30+"\n"
        result_string += "Student Name: \t*" + student + "*\n"
        result_string += "-"*30+"\n"
        
        for i, param in enumerate(param_keys):
            if dict_student_params[student][i]==1:
                result_string += param + " :\t*" + str(dict_student_params[student][i]==1) + "*\n"
            else:
                result_string += param + " :\t" + str(dict_student_params[student][i]==1) + "\n"
        
        result_string += "-"*30+"\n\n"
    return result_string


def check_self_harm(_datetime):
    today = datetime.datetime.today()
    margin = datetime.timedelta(days = 1)

    return today - margin <= _datetime <= today + margin


@user_passes_test(lambda u: u.is_superuser)
def start_server(request):

    run_auto_report()
    # run_auto_streamer()
    return HttpResponse("Started auto_report")


def update_streamer(request):
    if request.user.is_authenticated:
        client = TwitterClient(request)
        oauth_token, oauth_token_secret = client.get_oauth_tokens()
        students = Student.objects.filter(caregiver=request.user)
        following = [str(student.uid) for student in students]
        print(following)
        stream_tweet(oauth_token, oauth_token_secret, following)
        # Update streamer
        run_subprocess()
        print('FINISHED STREAMING')
    return redirect('all-students')


def run_auto_report():
    wd = os.getcwd()
    auto_report()
    work_dir = wd.replace('dashboard','')
    os.chdir(work_dir)
    subprocess.Popen("pkill -f auto-report", shell=True)
    sleep(1)
    subprocess.Popen("python3 manage.py process_tasks --queue auto-report", shell=True)
    os.chdir(wd)



cmds = ['all students', 'bipolarity', 'night-activity', 'negativity', 'self-harm']
