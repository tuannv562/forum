from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    import pytz
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    local_timezone = models.CharField(max_length=100, choices=TIMEZONES, default='UTC')
    avatar = models.ImageField(upload_to='profile_images', blank=True)

    class Meta(object):
        unique_together = ('email',)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
