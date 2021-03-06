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


def _get_menu_detail(menu_obj, ir_action_obj, menu_ids):
    menu_ids = menu_obj.search_read([('id', 'in', menu_ids)], ['name', 'child_id', 'action'], order='sequence')

    for menu_item in menu_ids:
        if menu_item['action']:
            url = ir_action_obj.search_read([('id', '=', menu_item['action'].split(',')[1])],
                                            ['name', 'url'])
            menu_item['action'] = url[0]
        if menu_item['child_id']:
            menu_item['child_id'] = _get_menu_detail(menu_obj, ir_action_obj, menu_item['child_id'])

    return menu_ids


def _get_menu(context):
    request = context['request']
    menu_obj = request.erpsession.get_model("internal.home.menu")
    ir_action_obj = request.erpsession.get_model("ir.actions.act_url")
    menu_items = {
        'top_menu': menu_obj.search_read([('name', '=', 'Top menu')], ['name', 'child_id', ])[0]['child_id'],
        'bottom_menu': menu_obj.search_read([('name', '=', 'Footer Menu')], ['name', 'child_id', ])[0]['child_id'],
    }
    menu_items['top_menu'] = _get_menu_detail(menu_obj, ir_action_obj, menu_items['top_menu'])
    menu_items['bottom_menu'] = _get_menu_detail(menu_obj, ir_action_obj, menu_items['bottom_menu'])
    return menu_items


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

    my_menu = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'menu_message_message_my_act')],
                                      ['res_id'], limit=1)
    my_menu_id = my_menu[0]['res_id']

    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_notice')],
                                     ['res_id'], limit=1)
    ids['notice'] = [my_menu_id, notice[0]['res_id']]
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_food')],
                                     ['res_id'], limit=1)
    ids['food'] = [my_menu_id, notice[0]['res_id']]
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_service')],
                                     ['res_id'], limit=1)
    ids['service'] = [my_menu_id, notice[0]['res_id']]
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_chat')],
                                     ['res_id'], limit=1)
    ids['chat'] = [my_menu_id, notice[0]['res_id']]
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_life')],
                                     ['res_id'], limit=1)
    ids['life'] = [my_menu_id, notice[0]['res_id']]
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_share')],
                                     ['res_id'], limit=1)
    ids['share'] = [my_menu_id, notice[0]['res_id']]
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_news')],
                                     ['res_id'], limit=1)
    ids['news'] = [my_menu_id, notice[0]['res_id']]
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_sell')],
                                     ['res_id'], limit=1)
    ids['sell'] = [my_menu_id, notice[0]['res_id']]
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_recommend')],
                                     ['res_id'], limit=1)
    ids['recommend'] = [my_menu_id, notice[0]['res_id']]
    notice = ir_data_obj.search_read([('module', '=', 'message'), ('name', '=', 'action_my_messages_inner_connection')],
                                     ['res_id'], limit=1)
    ids['inner_connection'] = [my_menu_id, notice[0]['res_id']]

    internal_menu = ir_data_obj.search_read(
        [('module', '=', 'message'), ('name', '=', 'menu_message_message_internal_act')],
        ['res_id'], limit=1)
    internal_menu_id = internal_menu[0]['res_id']
    notice = ir_data_obj.search_read(
        [('module', '=', 'message'), ('name', '=', 'action_internal_messages_incoming_project')],
        ['res_id'], limit=1)
    ids['incoming_project'] = [internal_menu_id, notice[0]['res_id']]

    cache.set('message_publish_url', ids, 60 * 3600)
    return ids


@register.simple_tag(name='message_publish_url', takes_context=True)
def message_publish_url(context, name):
    if cache.get('message_publish_url'):
        url = cache.get('message_publish_url')
    else:
        url = _get_message_publish_url(context)
        cache.set('message_publish_url', url, 60 * 3600)
    text = u'''<a class="publish-message" target="_blank" href="%s/#view_type=form&model=message.message&menu_id=%d&action=%s">发布</a>'''
    from  upcms import settings

    host = settings.ERP_HOME
    # name = unicode(name, 'ascii')

    if name == u'畅所欲言':
        return text % (host, url['chat'][0], url['chat'][1])
    if name == u'通知':
        return text % (host, url['notice'][0], url['notice'][1])
    if name == u'业余生活':
        return text % (host, url['life'][0], url['life'][1])
    if name == u'服务申报':
        return text % (host, url['service'][0], url['service'][1])
    if name == u'餐论':
        return text % (host, url['food'][0], url['food'][1])
    if name == u'共享资源':
        return text % (host, url['share'][0], url['share'][1])
    if name == u'各所快讯':
        return text % (host, url['news'][0], url['news'][1])
    if name == u'跳蚤市场':
        return text % (host, url['sell'][0], url['sell'][1])
    if name == u'大家推荐':
        return text % (host, url['recommend'][0], url['recommend'][1])
    if name == u'内部交流':
        return text % (host, url['inner_connection'][0], url['inner_connection'][1])

    if name == u'在谈项目':
        return text % (host, url['incoming_project'][0], url['incoming_project'][1])

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