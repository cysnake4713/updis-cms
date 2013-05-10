import operator
from django.core.cache import cache
from django.template.defaultfilters import stringfilter
from openerplib import dates

__author__ = 'Zhou Guangwen'
from django import template
from upcms import settings

register = template.Library()


@register.filter
def to_date(value):
    return dates.str_to_datetime(value)


@register.assignment_tag(takes_context=True)
def get_erp_address(context):
    path = settings.ERP_HOME
    return str(path)


def _get_menu(context):
    request = context['request']
    menu_obj = request.erpsession.get_model("internal.home.menu")
    ir_action_obj = request.erpsession.get_model("ir.actions.act_url")
    menu_items = menu_obj.search_read([], ['name', 'sequence', 'parent_id',
                                           'action', 'needaction_enabled', 'needaction_counter'])
    for menu_item in menu_items:
        if menu_item['action']:
            url = ir_action_obj.search_read([('id', '=', menu_item['action'].split(',')[1])],
                                            ['name', 'url'])
            menu_item['action'] = url[0]
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


def _get_message_publish_url(context):
    request = context['request']

    ir_data_obj = request.erpsession.get_model("ir.model.data")
    ids = {}
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_notice')],
                                     ['res_id'], limit=1)
    ids['notice'] = notice[0]['res_id']
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_food')],
                                     ['res_id'], limit=1)
    ids['food'] = notice[0]['res_id']
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_service')],
                                     ['res_id'], limit=1)
    ids['service'] = notice[0]['res_id']
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_chat')],
                                     ['res_id'], limit=1)
    ids['chat'] = notice[0]['res_id']
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_life')],
                                     ['res_id'], limit=1)
    ids['life'] = notice[0]['res_id']
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_share')],
                                     ['res_id'], limit=1)
    ids['share'] = notice[0]['res_id']
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_news')],
                                     ['res_id'], limit=1)
    ids['news'] = notice[0]['res_id']
    cache.set('message_publish_url', ids, 60 * 3600)
    return ids


@register.simple_tag(name='message_publish_url', takes_context=True)
def message_publish_url(context, name):
    if cache.get('message_publish_url'):
        url = cache.get('message_publish_url')
    else:
        url = _get_message_publish_url(context)
        cache.set('message_publish_url', url, 60 * 3600)
    text = u'''<a class="publish-message" target="_blank" href="http://%s/#view_type=form&model=message.message&menu_id=277&action=%s">\u53d1\u5e03</a>'''
    from  upcms import settings

    if settings.ERP_PORT == 80:
        host = settings.ERP_HOST
    else:
        host = settings.ERP_HOST + ':' + str(settings.ERP_PORT)

        # name = unicode(name, 'ascii')

    if name == u'\u7545\u6240\u6b32\u8a00':
        return text % (host, url['chat'])
    if name == u'\u901a\u77e5':
        return text % (host, url['notice'])
    if name == u'\u4e1a\u4f59\u751f\u6d3b':
        return text % (host, url['life'])
    if name == u'\u670d\u52a1\u7533\u62a5':
        return text % (host, url['service'])
    if name == u'\u9910\u8bba':
        return text % (host, url['food'])
    if name == u'\u5171\u4eab\u8d44\u6e90':
        return text % (host, url['share'])
    if name == u'\u5404\u6240\u5feb\u8baf':
        return text % (host, url['news'])
    return ''


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