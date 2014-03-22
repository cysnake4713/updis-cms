from cms.models import CMSPlugin
from django.db import models

# Create your models here.
class MessageCategories(CMSPlugin):
    category_ids = models.CharField(max_length=256, default='')


class BirthdayWish(CMSPlugin):
    people = models.CharField(max_length=512, default='')
    wish = models.CharField(max_length=512, default='')
    help = models.TextField(max_length=512, default='')