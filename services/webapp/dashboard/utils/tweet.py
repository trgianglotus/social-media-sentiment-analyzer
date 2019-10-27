def save_tweet(analyzer, data):
    if not is_delete(data):
        if is_retweet(data):
            return None
            # Handle exception too many values to unpack
            text, media, student = extract_data_retweet(data)
        else:
            text, media, student, url_ = extract_data(data)

        ocr_res = ''
        media_status = None
        if media is not None:
            with urllib.request.urlopen(media) as url:
                image_np = np.asarray(bytearray(url.read()), dtype="uint8")
                image = cv2.imdecode(image_np, cv2.IMREAD_GRAYSCALE)
            # ocr_res = pytesseract.image_to_string(image, lang='eng', config='--oem 1 --psm 3')
            # print('================OCR RESULT================', '\n')

            ocr_res = get_ocr(media)
            print(ocr_res)

            # api_endpoint = 'http://0.0.0.0:3333/'
            # media_ = {'media': media}
            # media_status = not bool(requests.post(url=api_endpoint, data=media_).content)
            media_status = get_image_sentiment(media)
            
            # true: not depressed
            print('================IMAGE SENTIMENT RESULT================', '\n')
            print('Depressed: ' + str(not media_status), '\n')

        

        print('================TEXT ANALYZER RESULT================', '\n')
        text = text.strip(url_) + ' ' + ocr_res
        text_status = analyzer.predict(text)
        print('Depressed: ' + str(not text_status), '\n')
        
        if media:
            overall_status = text_status or media_status
        else: 
            overall_status = text_status
        
        posted_date = get_post_date_time(data)

        tokens = analyzer.tokenized_text

        s_harm = get_self_harm(tokens)

        new_tweet = Tweet(text=text, media=media, student=student, 
                text_status=text_status, posted_date=posted_date, 
                media_status=media_status, overall_status=overall_status,
                s_harm=s_harm)
        
        new_tweet.save()
        student.total_number_of_tweets += 1

        if not overall_status:
            student.number_of_n_tweets += 1

        if s_harm:
            SelfHarmTweet(tweet=new_tweet, student=student).save()
            profile = Profile.objects.filter(user=student.caregiver)[0]
            student.suicidal = True
            student.number_of_sh_tweets += 1
            send_whatsapp_alert(student_name=student.name, tweet=text, phone=profile.phone)
        
        student.save()
        print(f'Added a new tweet from {student.twitter_account}!')