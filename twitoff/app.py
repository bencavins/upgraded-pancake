from flask import Flask, render_template, request
from twitoff.predict import predict_user
from twitoff.twitter import add_or_update_user, vectorize_tweet
from .models import DB, User, Tweet
import os


def create_app():

    app = Flask(__name__)

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URI')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    DB.init_app(app)


    @app.route("/")
    def root():
        users = User.query.all()
        return render_template('base.html', title="Home", users=users)

    @app.route("/test")
    def test():
        return "<p>This is a test</p>"
    
    @app.route("/reset")
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template("base.html", title="Reset Database")
    
    @app.route("/update")
    def update():
        users = User.query.all()
        for user in users:
            add_or_update_user(user.username)
        return "All users have been updated"
    
    @app.route("/user", methods=['POST'])
    def user():
        name = request.values['user_name']
        add_or_update_user(name)
        message = f'User {name} was added successfully!'
    
    @app.route('/user/<name>')
    def user_lookup(name=None):
        tweets = User.query.filter(User.username == name).one().tweets

        return render_template('user.html', title=name, tweets=tweets, message='')
    
    @app.route("/compare", methods=['POST'])
    def compare():
        username0 = request.values['user0']
        username1 = request.values['user1']
        hypo_tweet_text = request.values['tweet_text']

        if username0 == username1:
            message = 'Cannot compare users to themselves!'
        else:
            prediction = predict_user(username0, username1, hypo_tweet_text)
            if prediction:
                # user 1 was predicted
                message = f'"{hypo_tweet_text} is more likely said by {username1}"'
            else:
                # user 0 was predicted
                message = f'"{hypo_tweet_text} is more likely said by {username0}"'
        
        return render_template('prediction.html', title="Prediction", message=message)
    
    @app.route("/populate")
    def populate():
        user1 = User(id=1, username='joe')
        DB.session.add(user1)
        tweet1_text = 'this is a tweet'
        tweet1 = Tweet(
            id=1, 
            text=tweet1_text, 
            user=user1,
            vector=vectorize_tweet(tweet1_text),
        )
        DB.session.add(tweet1)

        user2 = User(id=2, username='anne')
        DB.session.add(user2)
        tweet2_text = 'hello from anne'
        tweet2 = Tweet(
            id=2,
            text=tweet2_text,
            user=user2,
            vector=vectorize_tweet(tweet2_text),
        )
        DB.session.add(tweet2)

        DB.session.commit()
        return """The database has been reset
        <a href="/">Go to Home</a>
        <a href="/reset">Go to Reset</a>
        <a href="/populate">Go to Populate</a>"""

    
    return app