from django.db import models
from .enums import Profile_photo_options

class UserInfo(models.Model):
    username = models.CharField(max_length=200)
    alias = models.CharField(max_length=200)
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)
    photo_profile = models.CharField(max_length=200, default=Profile_photo_options.DEFAULT)
    friends = models.ManyToManyField("self", blank=True)
    elo = models.IntegerField(default=1000)
    cups = models.IntegerField(default=0)

    def __str__(self):
        return self.username

class MatchHistory(models.Model):
    opponent_1 = models.ForeignKey(UserInfo, related_name='opponent_1', on_delete=models.CASCADE)
    opponent_2 = models.ForeignKey(UserInfo, related_name='opponent_2', on_delete=models.CASCADE)
    opponent_1_points = models.IntegerField()
    opponent_2_points = models.IntegerField()
    match_type = models.CharField(max_length=100)
    elo_earned_opponent_1 = models.IntegerField()
    elo_earned_opponent_2 = models.IntegerField()
    date = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} vs {self.opponent.username} - {self.result}"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(UserInfo, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserInfo, related_name='received_friend_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)