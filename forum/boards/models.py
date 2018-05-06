import math

from django.db import models
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.text import Truncator
from markdown import markdown

from ..users.models import User


# Create your models here.
class Board(models.Model):
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class Topic(TimestampedModel):
    subject = models.CharField(max_length=254)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='topics')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('posts', kwargs={'board_pk': self.board.pk, 'topic_pk': self.pk})

    def get_page_count(self):
        count = self.posts.count()
        pages = count / 2
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()
        return count > 6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)

    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]


class Post(TimestampedModel):
    message = models.CharField(max_length=4000)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        truncated_msg = Truncator(self.message)
        return truncated_msg.chars(30)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))

    def get_number_likes(self):
        return Like.objects.filter(post__id=self.id).count()


class Like(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='+')
