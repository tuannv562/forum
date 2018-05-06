import pytz
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone


class User(AbstractUser):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    date_of_birth = models.DateField(default=timezone.now)
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    local_timezone = models.CharField(max_length=100, choices=TIMEZONES, default='UTC')
    avatar = models.ImageField(upload_to='profile_images', blank=True)
    last_visit_at = models.DateTimeField(default=timezone.now)
    bio = models.TextField(default='')

    class Meta(object):
        unique_together = ('email',)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
