from cms.models import CMSPlugin
from cms.plugins.text.models import AbstractText
from cms.plugins.text.utils import plugin_admin_html_to_tags, plugin_tags_to_admin_html
from django.db import models
from django.utils.text import truncate_words
from django.utils.translation import ugettext_lazy as _
from cms.plugins.text.utils import (plugin_tags_to_id_list, replace_plugin_tags)
from cms.utils.html import clean_html
from django.utils.html import strip_tags

# Create your models here.
class MessageCategories(CMSPlugin):
    category_ids = models.CharField(max_length=256, default='')


class BirthdayWishModel(AbstractText):
    """Abstract Text Plugin Class"""
    no_wish = models.TextField(_("body"))


    def _set_no_wish_admin(self, text):
        self.no_wish = plugin_admin_html_to_tags(text)


    def _get_no_wish_admin(self):
        return plugin_tags_to_admin_html(self.no_wish)


    no_wish_for_admin = property(_get_no_wish_admin, _set_no_wish_admin, None,
                                 """
                                 no_wish attribute, but with transformations
                                 applied to allow editing in the
                                 admin. Read/write.
                                 """)

    search_fields = ('body', 'no_wish')

    def __unicode__(self):
        return u"%s %s" % (truncate_words(strip_tags(self.body), 3)[:30] + "...", truncate_words(strip_tags(self.no_wish), 3)[:30] + "...")

    def clean(self):
        self.body = clean_html(self.body, full=False)
        self.no_wish = clean_html(self.no_wish, full=False)


class TimerModel(AbstractText):
    """Abstract Text Plugin Class"""


    search_fields = ('body')

    def clean(self):
        self.body = clean_html(self.body, full=False)

