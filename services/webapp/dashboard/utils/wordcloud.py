#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 13:43:52 2019

@author: adithyavh
"""
import os
from wordcloud import WordCloud, STOPWORDS
from PIL import Image


# print('CURRENT WORKING DIR IS:')
# print(os.getcwd())

def get_word_cloud (untokenised_text, twitter_account, max_font_size=40, max_words=100, background_color="white"):
    "returns PIL image"
    try:
        wordcloud1 = WordCloud(stopwords=STOPWORDS, max_font_size=max_font_size, max_words=max_words, background_color=background_color).generate(untokenised_text)
        wordcloud1.to_image().save(f"dashboard/static/img/{twitter_account}.jpg")
    except Exception as e:
        print(e)
        im = Image.open("dashboard/static/img/default.png").convert('RGB')
        im.save(f"dashboard/static/img/{twitter_account}.jpg")




#---------------Test Cases (Uncomment to run)--------------------#

#text = "The Houthis have repeatedly launched rockets, missiles and drones at populated areas in Saudi Arabia."\
#        " They are in conflict with a Saudi-led coalition which backs a president who the rebels had forced to flee "\
#        "when the Yemeni conflict escalated in March 2015. Iran is the regional rival of Saudi Arabia and an opponent "\
#        "of the US, which pulled out of a treaty aimed at limiting Tehran's nuclear programme after Mr Trump took power."\
#        "US-Iran tensions have risen markedly this year. The US said Iran was behind attacks on two oil tankers in the Gulf "\
#        "in June and July, as well as on another four in May. Tehran rejected the accusations in both cases."
#
#import matplotlib.pyplot as plt
#wordcloud2 = get_word_cloud(text)
#plt.figure()
#plt.imshow(wordcloud2, interpolation="bilinear")
#plt.axis("off")
#plt.show()

#---------------------------------------------------------------#

