from cms.plugin_base import CMSPluginBase
from django.utils.translation import ugettext_lazy as _
from messages.models import MessageCategories

__author__ = 'Zhou Guangwen'
from cms.plugin_pool import  plugin_pool

def get_messages_categories(position, request):
    erpsession = request.session.get('erpsession')
    message_category_obj = erpsession.get_model("message.category")
    message_obj = request.session.get('erpsession').get_model("message.message")
    message_categories = message_category_obj.search_read([('display_position', '=', position)],
        ['name', 'default_message_count', 'sequence'], order='sequence')
    for cat in message_categories:
        messages = message_obj.search_read([('category_id', '=', cat['id'])],
            ['category_message_title_meta_display', 'message_ids'], limit=6)
        cat.update({
            'messages': messages
        })
    return message_categories


def get_department_message_categories(request):
    message_category_obj = request.session.get('erpsession').get_model("message.category")
    hr_department_obj = request.session.get('erpsession').get_model("hr.department")
    message_obj = request.session.get('erpsession').get_model("message.message")

    departments = hr_department_obj.search_read(
        [('display_in_front', '=', True), ('deleted', '=', False), ('is_in_use', '=', True)],
        ['name', 'sequence', 'have_image'], order="sequence")
    for dep in departments:
        message_categories = message_category_obj.search_read([('display_in_departments', '=', dep['id'])],
            ['name', 'default_message_count', 'sequence', 'display_fbbm'], order='sequence')
        for cat in message_categories:
            messages = message_obj.search_read([('category_id', '=', cat['id']), ('department_id', '=', dep['id'])],
                ['name', 'write_date', 'write_uid', 'sequence', 'department_id', 'fbbm',
                 'category_message_title_meta_display'], limit=6)
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
        message_categories = get_messages_categories('shortcut', context.get('request'))
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

    def render(self, context, instance, placeholder):
        message_categories = get_messages_categories('content_left', context.get('request'))
        context.update({
            'object': instance,
            'placeholder': placeholder,
            'message_categories': message_categories
        })
        return context


class ContentRightMessageCategoriesPlugin(CMSPluginBase):
    model = MessageCategories
    name = _("Right message categories")
    render_template = "messages/plugins/contentright.html"
    admin_preview = False

    def render(self, context, instance, placeholder):
        message_categories = get_messages_categories('content_right', context.get('request'))
        context.update({
            'object': instance,
            'placeholder': placeholder,
            'message_categories': message_categories
        })
        return context


class DepartmentMessageCategoriesPlugin(CMSPluginBase):
    model = MessageCategories
    name = _("Department message categories")
    render_template = "messages/plugins/departmentmessages.html"
    admin_preview = False

    def render(self, context, instance, placeholder):
        department_message_categories = get_department_message_categories(context.get('request'))
        context.update({
            'object': instance,
            'placeholder': placeholder,
            'department_message_categories': department_message_categories
        })
        return context

plugin_pool.register_plugin(ShortcutMessageCategoriesPlugin)
plugin_pool.register_plugin(ContentLeftMessageCategoriesPlugin)
plugin_pool.register_plugin(ContentRightMessageCategoriesPlugin)
plugin_pool.register_plugin(DepartmentMessageCategoriesPlugin)