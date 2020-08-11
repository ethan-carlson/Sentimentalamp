# Sentimentalamp

IoT lamp with visual Twitter Sentiment Analysis indicator

The NLP portion of this project is based on the work of Anas Al-Masri, who wrote a great tutorial for writing a Naive Bayes Classifier to determine Twitter sentiment analysis: https://towardsdatascience.com/creating-the-twitter-sentiment-analysis-program-in-python-with-naive-bayes-classification-672e5589a7ed

The Arduino code runs on an ESP32, and the python script runs locally on a laptop with an internet connection. The two need to be connected via USB Serial at the time of this writing.

Future updates to include an API to deliver tweets within 50mi of an arbitrary location, and remove the need for USB Serial.
