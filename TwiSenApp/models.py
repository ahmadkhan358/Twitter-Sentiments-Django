from django.db import models

# Create your models here.
class Post(models.Model):
    usernameorhashtag = models.CharField(max_length=200)
    since = models.DateField(null=True)


class Tweet(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    tweet_text = models.TextField()
    tweet_id = models.IntegerField()
    tweet_length = models.IntegerField()
    tweet_created_at = models.DateTimeField()
    tweet_source = models.CharField(max_length=200)
    tweet_favorite_count = models.IntegerField()
    tweet_retweet_count = models.IntegerField()
    tweet_location = models.CharField(max_length=255)