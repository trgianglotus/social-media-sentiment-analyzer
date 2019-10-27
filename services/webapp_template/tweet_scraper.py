from selenium import webdriver
import urllib
import urllib.error
import urllib.request
import time
import sys
import numpy as np
import os
import datetime
from bs4 import BeautifulSoup

def internet_on():
    """
    Check if the network connection is on
    :return: boolean
    """
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib.error.URLError: 
        return False


def get_all_tweets_chrome(query: str, size: int):
    """
    Get all tweets from the webpage using the Chrome driver
    :param query: Tweet search query
    :return: all tweets on page as selenium objects
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')

    driver = webdriver.Chrome("drivers/chromedriver", options=chrome_options)
    driver.set_page_load_timeout(20)
    driver.get("https://twitter.com/search?f=tweets&vertical=default&q={}".format(urllib.parse.quote(query)))
    length = []
    try:
        while True:
            tweets_found = driver.find_elements_by_class_name('tweet') 
            driver.execute_script("return arguments[0].scrollIntoView();", tweets_found[::-1][0])
            # Stop the loop while no more found tweets 
            length.append(len(tweets_found))
            print('%s tweets found at %s' % (len(tweets_found), datetime.datetime.now().strftime('%d/%m/%Y - %H:%M')))

            if len(tweets_found) > size - 20 and (len(length) - len(set(length))) > 2:
                print('%s tweets found at %s' % (len(tweets_found), datetime.datetime.now().strftime('%d/%m/%Y - %H:%M')))
                break

                
            
    except IndexError:
        time.sleep(np.random.randint(50,100)*0.01)
        tweets_found = driver.find_elements_by_class_name('tweet') 
        print('%s tweets found at %s' % (len(tweets_found), datetime.datetime.now().strftime('%d/%m/%Y - %H:%M')))
    except Exception as e:
        print(e)
        time.sleep(np.random.randint(50,100)*0.01)
        tweets_found = driver.find_elements_by_class_name('tweet') 
        driver.execute_script("return arguments[0].scrollIntoView();", tweets_found[::-1][0])
    return driver


def format_tweets(driver):
    """
    Convert selenium objects into dictionnaries (images, date, text, username as keys)
    :param driver: Selenium driver (with tweets loaded)
    :return: well-formated tweets as a list of dictionnaries
    """
    start = time.time()
    tweets_found = driver.find_elements_by_class_name('tweet')
    print(time.time() - start)
    tweets = []
    for tweet in tweets_found:
        tweet_dict = {}
        tweet = tweet.get_attribute('innerHTML')
        bs = BeautifulSoup(tweet.strip(), "lxml")
        tweet_dict['username'] = bs.find('span', class_='username').text
        timestamp = float(bs.find('span', class_='_timestamp')['data-time'])
        tweet_dict['date'] = datetime.datetime.fromtimestamp(timestamp)
        tweet_dict['text'] = bs.find('p', class_='tweet-text').text
        try:
            tweet_dict['images'] = [k['src'] for k in bs.find('div', class_="AdaptiveMedia-container").find_all('img')]
        except:
            tweet_dict['images'] = []
        if len(tweet_dict['images']) > 0:
            tweet_dict['text'] = tweet_dict['text'][:tweet_dict['text'].index('pic.twitter')-1]
        tweets.append(tweet_dict)
    driver.close()
    return tweets


def filter_tweets(tweets):
    pass


if __name__ == "__main__":
    while not internet_on():
        time.sleep(1)
        time_slept += 1
        if time_slept > 15 : 
            print('%s - No network connection' % datetime.datetime.now().strftime('%d/%m/%Y - %H:%M'))
            sys.exit()

    query = input("Enter keyword: ")
    
    while True:
        try:
            size = int(input("Enter number of tweets you want to scrape: "))
            break
        except ValueError:
            print('Please enter a number!')

    driver = get_all_tweets_chrome(query, size)
    tweets = format_tweets(driver)
    
    f = open("data.txt", "w+")
    for tweet in tweets:
        f.write(str(tweet) + '\n')

