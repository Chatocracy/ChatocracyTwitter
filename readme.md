Tweet Generator

A Python script that generates and posts tweets about the latest political news using OpenAI's GPT-3 language model and the Twitter API. The script fetches the latest political news articles from the News API and generates tweets about them using GPT-3. The tweets are then posted to Twitter using the Twitter API.
Features

    Fetches the latest political news articles from the News API
    Generates tweets about the news articles using OpenAI's GPT-3 language model
    Posts the tweets to Twitter using the Twitter API
    Automatically saves the headlines that have already been commented on
    Only generates comments that are within the allowed character limit and contain the shortened URL
    Provides progress updates with the number of attempts made to generate a valid tweet
    Includes a call to action encouraging users to subscribe to the @chatocracy_app Twitter account

Installation

    Clone the repository to your local machine.
    Install the required packages by running pip install -r requirements.txt.
    Create a .env file in the root directory of the project and add your API keys to it as follows:

makefile

CONSUMER_KEY=<your_consumer_key_here>
CONSUMER_SECRET=<your_consumer_secret_here>
NEWS_API=<your_news_api_key_here>
OPENAI_API=<your_openai_api_key_here>

    Run the script using python tweet_generator.py.

Credits

This project was created by Anton Polevanov. If you find it useful, please consider subscribing to the @chatocracy_app Twitter account for more updates and news.
License

This project is licensed under the MIT License - see the LICENSE file for details.