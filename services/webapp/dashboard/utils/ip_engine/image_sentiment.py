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