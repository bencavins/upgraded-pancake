import numpy as np
from sklearn.linear_model import LogisticRegression
from .models import User
from .twitter import vectorize_tweet


def predict_user(username0, username1, hypo_tweet_text):
    """
    Determines which user is more likely to write a 
    given tweet.
    """

    # Grab users from db
    user0 = User.query.filter(User.username == username0).one()
    user1 = User.query.filter(User.username == username1).one()

    # Grab all tweet vectors for each user
    user0_vectors = np.array([tweet.vector for tweet in user0.tweets])
    user1_vectors = np.array([tweet.vector for tweet in user1.tweets])

    # Vertially stack tweet vectors into one numpy array
    vectors = np.vstack([user0_vectors, user1_vectors])
    labels = np.concatenate([
        np.zeros(len(user0.tweets)),
        np.ones(len(user1.tweets)),
    ])

    # Fit our data into the model
    log_reg = LogisticRegression().fit(vectors, labels)

    hypo_tweet_vector = vectorize_tweet(hypo_tweet_text)

    return log_reg.predict(hypo_tweet_vector.reshape(1, -1))