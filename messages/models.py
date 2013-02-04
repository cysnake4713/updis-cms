from cms.models import CMSPlugin
from django.db import models

# Create your models here.
class MessageCategories(CMSPlugin):
    category_ids = models.CharField(max_length=256)
