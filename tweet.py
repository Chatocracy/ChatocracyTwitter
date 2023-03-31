import openai
import json
import requests
import pyshorteners
from requests_oauthlib import OAuth1Session
from datetime import datetime, timedelta
import time


CONSUMER_KEY = 'aKaxA2pCTDTeNH7Anm9qTdOCh'
CONSUMER_SECRET = 'fY72ZU3wkkCDYvYkVQDWv66sV3x3T5PGT1ksiS1suR7gYYWypo'
NEWS_API = '138ce02a63144ee5801244745fadde8a'
OPENAI_API ='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'


def shorten_url(url):
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(url)
    return short_url

def save_commented_headlines_to_file(commented_headlines):
    with open("commented_headlines.json", "w") as f:
        json.dump(commented_headlines, f)

def load_commented_headlines_from_file():
    try:
        with open("commented_headlines.json", "r") as f:
            commented_headlines = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print('here')
        commented_headlines = []

    return commented_headlines


def is_headline_commented(headline):
    commented_headlines = load_commented_headlines_from_file()
    return headline in commented_headlines

def save_headline_as_commented(headline):
    commented_headlines = load_commented_headlines_from_file()
    commented_headlines.append(headline)
    save_commented_headlines_to_file(commented_headlines)

def load_access_tokens():
    with open("access_tokens.json", "r") as f:
        tokens = json.load(f)
    return tokens["access_token"], tokens["access_token_secret"]


def save_access_tokens(access_token, access_token_secret):
    with open("access_tokens.json", "w") as f:
        json.dump({"access_token": access_token, "access_token_secret": access_token_secret}, f)



def authenticate(consumer_key, consumer_secret):
    access_token, access_token_secret = load_access_tokens()

    if not access_token or not access_token_secret:
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            print("There may have been an issue with the consumer_key or consumer_secret you entered.")

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")

        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print("Please go here and authorize: %s" % authorization_url)
        verifier = input("Paste the PIN here: ")

        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        save_access_tokens(access_token, access_token_secret)

    return access_token, access_token_secret


def post_tweet(consumer_key, consumer_secret, access_token, access_token_secret, tweet_text):
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    payload = {"text": tweet_text}
    response = oauth.post("https://api.twitter.com/2/tweets", json=payload)

    if response.status_code != 201:
        raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))

    print("Response code: {}".format(response.status_code))
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))


def get_latest_news(query, country='us', page_size=10):
    api_key = NEWS_API
    
    url = "https://newsapi.org/v2/top-headlines"

    params = {
        "apiKey": api_key,
        "country": country,
        "category": "politics",
        "pageSize": page_size,
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))

    news_data = response.json()
    return news_data["articles"]
    
def generate_comments(articles, model="text-davinci-002", max_tokens=50):
    openai.api_key = OPENAI_API

    comments = []
    for article in articles:
        headline = article["title"]
        url = article["url"]
        short_url = shorten_url(url)

        prompt = f"Please write a tweet about these news. The tweet must be within the allowed character length for Twitter, \
            be useful for my users, and attract users to subscribe to my Twitter account. In approximately 50% of the tweets, include a call to action \
            encouraging users to subscribe to Chatocracy. Please include the shortened URL to the source, \
            an appropriate hashtag (only one, to keep the tweet length in check), and relevant emojis such as 📰, 🗞️, 💡, or 🚀 or other appropriate emoji \
            Write all tweets in the style of Pam Moore without repeating the headline itself in the tweet. \
            Be creative and make a meaningful comment. Include a joke if it is appropriate and causes no harm. \
            Here is the headline: '{headline}', and the short url: '{short_url}'"

        while True:
            response = openai.Completion.create(
                engine=model,
                prompt=prompt,
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=0.5,
            )

            comment = response.choices[0].text.strip()

            # Check if the generated tweet is within the allowed character limit
            if len(comment) <= 280:
                break
            else:
                max_tokens = max_tokens - 5  # Reduce max_tokens to generate a shorter tweet

        comments.append(comment)

    return comments

if __name__ == "__main__":
    query = "politics"
    
    # Authenticate and get access tokens
    access_token, access_token_secret = authenticate(CONSUMER_KEY, CONSUMER_SECRET)
    
    while True:
        top_political_headlines = get_latest_news(query)
        comments = generate_comments(top_political_headlines)

        for article, comment in zip(top_political_headlines, comments):
            headline = article["title"]
            
            if not is_headline_commented(headline):
                print(f"Headline: {headline}")
                print(f"Comment: {comment}")
                print()
                
                # Post the tweet here
                tweet = post_tweet(CONSUMER_KEY, CONSUMER_SECRET, access_token, access_token_secret, comment)
                print('!!!')
                save_headline_as_commented(headline)
                
                # Sleep for an hour before tweeting the next comment
                time.sleep(3600)
        # Sleep for an hour before fetching the next portion of news
        time.sleep(3600)
