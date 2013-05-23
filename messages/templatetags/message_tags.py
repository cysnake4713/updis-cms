# -*- coding: utf-8 -*-
import operator
import datetime
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

    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_sell')],
                                     ['res_id'], limit=1)
    ids['sell'] = notice[0]['res_id']
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_recommend')],
                                     ['res_id'], limit=1)
    ids['recommend'] = notice[0]['res_id']
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_inner_connection')],
                                     ['res_id'], limit=1)
    ids['inner_connection'] = notice[0]['res_id']

    cache.set('message_publish_url', ids, 60 * 3600)
    return ids


@register.simple_tag(name='message_publish_url', takes_context=True)
def message_publish_url(context, name):
    if cache.get('message_publish_url'):
        url = cache.get('message_publish_url')
    else:
        url = _get_message_publish_url(context)
        cache.set('message_publish_url', url, 60 * 3600)
    text = u'''<a class="publish-message" target="_blank" href="%s/#view_type=form&model=message.message&menu_id=277&action=%s">发布</a>'''
    from  upcms import settings

    host = settings.ERP_HOME
    # name = unicode(name, 'ascii')

    if name == u'畅所欲言':
        return text % (host, url['chat'])
    if name == u'通知':
        return text % (host, url['notice'])
    if name == u'业余生活':
        return text % (host, url['life'])
    if name == u'服务申报':
        return text % (host, url['service'])
    if name == u'餐论':
        return text % (host, url['food'])
    if name == u'共享资源':
        return text % (host, url['share'])
    if name == u'各所快讯':
        return text % (host, url['news'])
    if name == u'跳蚤市场':
        return text % (host, url['sell'])
    if name == u'大家推荐':
        return text % (host, url['recommend'])
    if name == u'内部交流':
        return text % (host, url['inner_connection'])

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


@register.simple_tag(name='is_today', takes_context=True)
def is_today(context, date):
    create_date = datetime.datetime.strptime(date,
                                             '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
    create_date = create_date.strftime('%Y-%m-%d')

    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d')
    if create_date == now:
        return 'style="font-weight: bold"'
    else:
        return ''

register.filter('truncatehanzi', truncatehanzi)