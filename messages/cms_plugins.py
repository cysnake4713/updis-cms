# -*- coding: utf-8 -*-
import re

from cms.plugin_base import CMSPluginBase
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

from messages.models import MessageCategories


__author__ = 'Zhou Guangwen'
from cms.plugin_pool import plugin_pool


def _get_last_image(messages):
    for message in messages:
        content = message['content']
        if content:
            match = re.compile(r'''.*?<img[^>]+\s+src\s*=\s*['"]([^'"]+)['"][^>]*>.*?''', re.IGNORECASE).match(
                content.replace('\n', ' '))
            if match:
                return match.group(1), message
    return None


def get_messages_categories(position, request):
    erpsession = request.erpsession
    message_category_obj = erpsession.get_model("message.category")
    message_categories = message_category_obj.search_read([('display_position', '=', position)],
                                                          ['name', 'default_message_count', 'sequence'],
                                                          order='sequence')
    # for cat in message_categories:
    #     messages = message_obj.search_read([('category_id', '=', cat['id'])],
    #                                        ['category_message_title_meta_display', 'message_ids', 'name',
    #                                         "create_date"],
    #                                        limit=cat['default_message_count'] is not 0 and cat[
    #                                            'default_message_count'] or 8)
    #     cat.update({
    #         'messages': messages
    #     })
    return message_categories


def get_messages_categories_with_image(position, request):
    erpsession = request.erpsession
    message_category_obj = erpsession.get_model("message.category")
    message_obj = request.session.get('erpsession').get_model("message.message")
    message_categories = message_category_obj.search_read([('display_position', '=', position)],
                                                          ['name', 'default_message_count', 'sequence'],
                                                          order='sequence')
    for cat in message_categories:
        messages = message_obj.search_read([('category_id', '=', cat['id'])],
                                           ['category_message_title_meta_display', 'message_ids', 'content', 'name',
                                            'create_date'],
                                           limit=10)
        top_message = _get_last_image(messages)
        if top_message:
            top_message[1]['content'] = top_message[1]['content']
            cat['top_message'] = top_message
        if top_message:
            cat.update({
                'messages': messages[:3]
            })
        else:
            cat.update({
                'messages': messages[:8]
            })
    return message_categories


def get_department_message_categories(request):
    message_category_obj = request.erpsession.get_model("message.category")
    hr_department_obj = request.erpsession.get_model("hr.department")
    message_obj = request.erpsession.get_model("message.message")

    departments = hr_department_obj.search_read(
        [('display_in_front', '=', True), ('deleted', '=', False), ('is_in_use', '=', True)],
        ['name', 'short_name', 'sequence', 'have_image'], order="sequence")
    for dep in departments:
        message_categories = message_category_obj.search_read([('display_in_departments', '=', dep['id'])],
                                                              ['name', 'default_message_count', 'sequence',
                                                               'display_fbbm'], order='sequence')
        for cat in message_categories:
            messages = message_obj.search_read([('category_id', '=', cat['id']), ('department_id', '=', dep['id'])],
                                               ['name', 'write_date', 'write_uid', 'sequence', 'department_id', 'fbbm',
                                                'category_message_title_meta_display', 'create_date'],
                                               limit=cat['default_message_count'] is not 0 and cat[
                                                   'default_message_count'] or 8)
            cat.update({
                'messages': messages
            })
        dep['message_categories'] = message_categories
    return departments


class ShortcutMessageCategoriesPlugin(CMSPluginBase):
    model = MessageCategories
    name = _("Shortcut")
    render_template = "messages/plugins/shortcut.html"
    admin_preview = False

    def render(self, context, instance, placeholder):

        if cache.get('shortcut_category_cache'):
            message_categories = cache.get('shortcut_category_cache')
        else:
            message_categories = get_messages_categories('shortcut', context.get('request'))
            cache.set('shortcut_category_cache', message_categories, 60 * 100)
            context.update({
                'object': instance,
                'placeholder': placeholder,
                'message_categories': message_categories
            })
        return context


class ContentLeftMessageCategoriesPlugin(CMSPluginBase):
    model = MessageCategories
    name = _("Left message categories")
    render_template = "messages/plugins/contentleft.html"
    admin_preview = False

    def _get_special_group(self, request):
        if cache.get('special_group'):
            return cache.get('special_group')
        else:
            groups_obj = request.erpsession.get_model("res.groups")
            groups = groups_obj.search_read([('name', '=', 'Special')])
            if groups:
                return groups[0]['users']
            else:
                return None

    def render(self, context, instance, placeholder):
        request = context['request']
        if cache.get('left_category_cache'):
            message_categories = cache.get('left_category_cache')
        else:
            message_categories = get_messages_categories_with_image('content_left', context.get('request'))
            cache.set('left_category_cache', message_categories, 60 * 100)
            # message_categories = get_messages_categories_with_image('content_left', context.get('request'))

        for cate in message_categories:
            if cate['name'] == u'在谈项目':
                users = self._get_special_group(request)
                if request.session['erp_user']:
                    if users is not None and request.session['erp_user']['uid'] not in users:
                        message_categories.remove(cate)
                else:
                    message_categories.remove(cate)

        context.update({
            'object': instance,
            'placeholder': placeholder,
            'message_categories': message_categories,
        })
        return context


class ContentRightMessageCategoriesPlugin(CMSPluginBase):
    model = MessageCategories
    name = _("Right message categories")
    render_template = "messages/plugins/contentright.html"
    admin_preview = False


    def _get_special_group(self, request):
        if cache.get('special_group'):
            return cache.get('special_group')
        else:
            groups_obj = request.erpsession.get_model("res.groups")
            groups = groups_obj.search_read([('name', '=', 'Special')])
            if groups:
                return groups[0]['users']
            else:
                return None

    def render(self, context, instance, placeholder):
        request = context['request']
        #cache top message
        if cache.get('right_category_cache'):
            message_categories = cache.get('right_category_cache')
        else:
            message_categories = get_messages_categories_with_image('content_right', context.get('request'))
            cache.set('right_category_cache', message_categories, 60 * 100)
            # message_categories = get_messages_categories_with_image('content_right', context.get('request'))

        for cate in message_categories:
            if cate['name'] == u'在谈项目':
                users = self._get_special_group(request)
                if request.session['erp_user']:
                    if users is not None and request.session['erp_user']['uid'] not in users:
                        message_categories.remove(cate)
                else:
                    message_categories.remove(cate)

        context.update({
            'object': instance,
            'placeholder': placeholder,
            'message_categories': message_categories,
        })
        return context


class DepartmentMessageCategoriesPlugin(CMSPluginBase):
    model = MessageCategories
    name = _("Department message categories")
    render_template = "messages/plugins/departmentmessages.html"
    admin_preview = False

    def render(self, context, instance, placeholder):
        if cache.get('department_message_category_cache'):
            department_message_categories = cache.get('department_message_category_cache')
        else:
            department_message_categories = get_department_message_categories(context.get('request'))
            cache.set('department_message_category_cache', department_message_categories, 60 * 100)
        context.update({
            'object': instance,
            'placeholder': placeholder,
            'department_message_categories': department_message_categories
        })
        return context


class Android2DImagePlugin(CMSPluginBase):
    name = _("Android 2D Image plugin")
    render_template = "messages/plugins/phone2d.html"
    admin_preview = False

    def render(self, context, instance, placeholder):
        return context


plugin_pool.register_plugin(ShortcutMessageCategoriesPlugin)
plugin_pool.register_plugin(ContentLeftMessageCategoriesPlugin)
plugin_pool.register_plugin(ContentRightMessageCategoriesPlugin)
plugin_pool.register_plugin(DepartmentMessageCategoriesPlugin)
plugin_pool.register_plugin(Android2DImagePlugin)