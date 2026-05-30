from django.conf import settings
from django.db import models


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(max_length=300)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def score(self):
        up = self.votes.filter(value=Vote.UP).count()
        down = self.votes.filter(value=Vote.DOWN).count()
        return up - down

    @property
    def comment_count(self):
        return self.comments.count()


class Vote(models.Model):
    UP = 1
    DOWN = -1
    CHOICES = [(UP, 'Upvote'), (DOWN, 'Downvote')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    value = models.SmallIntegerField(choices=CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_vote_per_user_post'),
        ]

    def __str__(self):
        return f"{self.user.username} {'up' if self.value == self.UP else 'down'}voted {self.post_id}"


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username} on {self.post_id}"
