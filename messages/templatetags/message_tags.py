from openerplib import dates

__author__ = 'Zhou Guangwen'
from django import template

register = template.Library()

@register.filter
def to_date(value):
    return dates.str_to_datetime(value)