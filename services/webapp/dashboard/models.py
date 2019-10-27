from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Student(models.Model):
    name = models.CharField(max_length=100)
    twitter_account = models.CharField(max_length=100)
    updated_date = models.DateTimeField(default=timezone.now)
    caregiver = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    uid = models.PositiveIntegerField(null=True)
    total_number_of_tweets = models.IntegerField(default=0)
    number_of_n_tweets = models.IntegerField(default=0)
    number_of_sh_tweets = models.IntegerField(default=0)
    wordcloud = models.CharField(max_length=500, null=True)
    
    mean_frequency_score = models.FloatField(default=0)

    bipolarity = models.BooleanField(default=False)
    has_frequency_changed = models.BooleanField(default=False)
    consistent_negativity = models.BooleanField(default=False)
    timing = models.BooleanField(default=False)
    suicidal = models.BooleanField(default=False)
    

    class Meta:
        verbose_name_plural = "students"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("student-detail", args=(self.pk,))


class Tweet(models.Model):
    text = models.TextField(null=True)
    text_status = models.BooleanField(null=True)

    media = models.URLField(null=True, max_length=200)
    media_status = models.BooleanField(null=True)
    overall_status = models.BooleanField(null=True)
    posted_date = models.DateTimeField(default=timezone.now)
    student = models.ForeignKey(Student, null=True, on_delete=models.CASCADE)
    s_harm = models.BooleanField(null=True)

    def __str__(self):
        return self.text


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.IntegerField(null=True)
    receive_email = models.BooleanField(default=False)
    receive_message = models.BooleanField(default=False)
    days = models.IntegerField(default=7)
    days_left = models.IntegerField(default=7)
    receive_alert = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} Profile'


class SelfHarmTweet(models.Model):
    tweet = models.OneToOneField(Tweet, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tweet.text}'