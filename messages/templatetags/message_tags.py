import operator
from django.core.cache import cache
from django.template.defaultfilters import stringfilter
from openerplib import dates

__author__ = 'Zhou Guangwen'
from django import template

register = template.Library()


@register.filter
def to_date(value):
    return dates.str_to_datetime(value)


def _get_menu(context):
    request = context['request']
    menu_obj = request.erpsession.get_model("internal.home.menu")
    menu_items = menu_obj.search_read([],
        ['name', 'sequence', 'parent_id', 'action', 'needaction_enabled', 'needaction_counter'])
    menu_items_map = dict((menu_item['id'], menu_item) for menu_item in menu_items)
    for menu_item in menu_items:
        if menu_item['parent_id']:
            parent = menu_item['parent_id'][0]
        else:
            parent = False
        if parent in menu_items_map:
            menu_items_map[parent].setdefault('children', []).append(menu_item)
    for menu_item in menu_items:
        menu_item.setdefault('children', []).sort(key=operator.itemgetter('sequence'))
    return menu_items_map


@register.assignment_tag(takes_context=True)
def load_menu(context):
    if cache.get('homepage_menu'):
        menu_items_map = cache.get('homepage_menu')
    else:
        menu_items_map = _get_menu(context)
        cache.set('homepage_menu', menu_items_map, 60 * 24)
    return menu_items_map

@stringfilter
def truncatehanzi(value, arg):
    """
    Truncates a string after a certain number of words including
    alphanumeric and CJK characters.
    Argument: Number of words to truncate after.
    """
    try:
        bits = []
        for x in arg.split(u':'):
            if len(x) == 0:
                bits.append(None)
            else:
                bits.append(int(x))
        if int(x) < len(value):
            return value[slice(*bits)] + '...'
        return value[slice(*bits)]

    except (ValueError, TypeError):
        return value # Fail silently.

register.filter('truncatehanzi', truncatehanzi)