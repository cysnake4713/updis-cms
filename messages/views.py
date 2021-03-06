# Create your views here.
# -*- coding: utf-8 -*-
import base64
import psycopg2
import timeit

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.cache import cache
from django.utils import simplejson

from upcms import settings
from messages.forms import CommentForm
import cms_plugins


def update_read_time(id):
    conn = psycopg2.connect(host=settings.DB_HOST, database=settings.DB_NAME, user=settings.DB_USER,
                            password=settings.DB_PASSWORD,port=settings.DB_PORT)

    cursor = conn.cursor()
    cursor.execute(
        """update message_message set read_times = case when read_times is null then 1 else read_times + 1 end where id = %s""" % (
            id))
    conn.commit()
    cursor.close()
    conn.close()


class MessageList(object):
    def __init__(self, erpsession, domain, fields):
        self.message_obj = erpsession.get_model('message.message')
        self.domain = domain
        self.fields = fields

    def count(self):
        return self.message_obj.search_count(self.domain)

    def __getitem__(self, item):
        if isinstance(item, slice):
            count = item.stop - item.start
            return self.message_obj.search_read(self.domain, self.fields, offset=item.start, limit=count)


def detail(req, message_id):
    update_read_time(message_id)
    message_obj = req.erpsession.get_model('message.message')
    comment_obj = req.erpsession.get_model('mail.message')
    attachment_obj = req.erpsession.get_model('ir.attachment')

    messages = message_obj.search_read([('id', '=', message_id)],
                                       ['name', 'message_meta_display', 'content', 'message_ids',
                                        'category_id', 'message_summary', 'read_times', 'vote_like', 'vote_unlike'])
    if messages:
        message = messages[0]

        comments = comment_obj.read(message['message_ids'],
                                    ['body', 'date', 'subject', 'author_id', 'is_anonymous', 'attachment_ids'])
        for comment in comments:
            comment['attachment_ids'] = attachment_obj.read(comment.get('attachment_ids'), ["id", 'datas_fname'])
    else:
        raise Http404
    if req.method == 'POST':
        form = CommentForm(req.POST, req.FILES)
        if form.is_valid():
            erp_user = req.session['erp_user']
            res_users_obj = req.erpsession.get_model('res.users')
            partner_id = res_users_obj.search_read([('id', '=', erp_user['uid'])], ['partner_id'])[0]['partner_id'][0]
            params = {
                'body': form.cleaned_data['body'],
                'type': 'comment',
                'model': 'message.message',
                'res_id': message.get('id'),
                'is_anonymous': form.cleaned_data['is_anonymous'],
                'author_id': partner_id,
            }
            if form.cleaned_data['attachment']:
                attachment_id = attachment_obj.create({
                    'name': form.cleaned_data['attachment'].name,
                    'datas_fname': form.cleaned_data['attachment'].name,
                    'type': 'binary',
                    'file_size': form.cleaned_data['attachment'].size,
                    'db_datas': base64.encodestring(form.cleaned_data['attachment'].file.read()),
                })
                params.update({
                    'attachment_ids': [(4, attachment_id)],
                })
            comment_obj = req.erpsession.get_model('mail.message')
            comment_id = comment_obj.create(params)
            message_obj.write([message_id], {'read_times': message['read_times']})
            if form.cleaned_data['attachment']:
                attachment_obj = req.erpsession.get_model('ir.attachment')
                attachment_obj.write([attachment_id], {'res_model': 'mail.message', 'res_id': comment_id})
            return HttpResponseRedirect(req.path)
    else:
        form = CommentForm()
    return render_to_response("messages/detail.html", {'message': message,
                                                       'comments': comments,
                                                       'form': form,
    },
                              context_instance=RequestContext(req))


def vote_like(req, message_id):
    message_id = int(message_id)
    erpsession = req.erpsession
    erp_user = req.session['erp_user']
    if erp_user:
        user_id = erp_user['uid']
        message_obj = erpsession.get_model('message.message')
        is_voted = message_obj.vote_like(user_id, message_id)
        return HttpResponseRedirect("/message/message/%s/" % message_id)
    else:
        return HttpResponseRedirect("/account/login/%s" % req.path)


def vote_unlike(req, message_id):
    message_id = int(message_id)
    erpsession = req.erpsession
    erp_user = req.session['erp_user']
    if erp_user:
        user_id = erp_user['uid']
        message_obj = erpsession.get_model('message.message')
        is_voted = message_obj.vote_unlike(user_id, message_id)
        return HttpResponseRedirect("/message/message/%s/" % message_id)
    else:
        return HttpResponseRedirect("/account/login/%s" % req.path)


# @cache_page(60 * 5)
def index(req):
    response = render_to_response("messages/index.html", context_instance=RequestContext(req))
    return response


def by_category(req, category_id):
    erpsession = req.erpsession
    category_id = int(category_id)
    message_category_obj = erpsession.get_model("message.category")

    message_categorys = message_category_obj.search_read([('id', '=', category_id)])
    if message_categorys:
        message_category = message_categorys[0]
    else:
        raise Http404
    per_page = int(req.GET.get('per_page', 20))
    paginator = Paginator(MessageList(erpsession, [('category_id', '=', category_id)],
                                      ['name', 'message_ids', 'write_uid', 'fbbm',
                                       'write_date_display', 'create_date', 'read_times', 'create_date_display',
                                       'category_id', 'vote_like', 'vote_unlike',
                                       'is_display_name',
                                       'name_for_display']), per_page)
    page = req.GET.get('page')
    try:
        messages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        messages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        messages = paginator.page(paginator.num_pages)
        #    messages = message_obj.search_read([],['name','category_message_title_meta_display'],limit=10)
    return render_to_response("messages/by_category.html", {'category': message_category, 'messages': messages},
                              context_instance=RequestContext(req))


def _get_special_group(request):
    if cache.get('special_group'):
        return cache.get('special_group')
    else:
        groups_obj = request.erpsession.get_model("res.groups")
        groups = groups_obj.search_read([('name', '=', 'Special')])
        if groups:
            return groups[0]['users']
        else:
            return None


def search(request, search_context):
    erpsession = request.erpsession
    # message_message_obj = erpsession.get_model("message.message")
    per_page = int(request.GET.get('per_page', 20))

    users = _get_special_group(request)
    if request.session['erp_user']:
        if users is not None and request.session['erp_user']['uid'] not in users:
            fields = [('name', 'like', search_context.replace(' ', '%')),
                      ('category_id.name', '!=', u'在谈项目')]
        else:
            fields = [('name', 'like', search_context.replace(' ', '%'))]
    else:
        fields = [('name', 'like', search_context.replace(' ', '%')),
                  ('category_id.name', '!=', u'在谈项目')]

    paginator = Paginator(MessageList(erpsession, fields,
                                      ['name', 'message_ids', 'write_uid', 'fbbm', 'read_times',
                                       'write_date_display', 'create_date_display', 'create_date',
                                       'name_for_display', 'vote_like', 'vote_unlike',
                                       'category_id',
                                       'is_display_name']), per_page)

    page = request.GET.get('page')

    try:
        messages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        messages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        messages = paginator.page(paginator.num_pages)
    return render_to_response("messages/search_result.html", {'messages': messages, 'search_context': search_context},
                              context_instance=RequestContext(request))


def get_department_image(request, department_id):
    erp_session = request.erpsession

    department_id = int(department_id)
    message_category_obj = erp_session.get_model("hr.department")

    hr_departments = message_category_obj.search_read([('id', '=', department_id)], ['image_medium'])
    if hr_departments:
        hr_department = hr_departments[0]
    else:
        raise Http404
    response = HttpResponse(hr_department['image_medium'].decode('base64'))
    response['Content-Type'] = 'image/png'
    return response


def get_employee_image(request, employee_id):
    erp_session = request.erpsession

    employee_id = int(employee_id)
    employee_obj = erp_session.get_model("res.partner")

    hr_employees = employee_obj.search_read([('id', '=', employee_id)], ['image_small'])
    if hr_employees:
        hr_employee = hr_employees[0]
    else:
        raise Http404
    response = HttpResponse(hr_employee['image_small'].decode('base64'))
    response['Content-Type'] = 'image/png'
    return response


def get_department_image_big(request, department_id):
    erp_session = request.erpsession

    department_id = int(department_id)
    message_category_obj = erp_session.get_model("hr.department")

    hr_departments = message_category_obj.search_read([('id', '=', department_id)], ['image'])
    if hr_departments:
        hr_department = hr_departments[0]
    else:
        raise Http404
    response = HttpResponse(hr_department['image'].decode('base64'))
    response['Content-Type'] = 'image/png'
    return response


def get_attachment(request, attachment_id):
    attachment_id = int(attachment_id)
    attachment_obj = request.erpsession.get_model('ir.attachment')
    datas = attachment_obj.search_read([('id', '=', attachment_id)], ['datas', 'datas_fname'])
    if datas:
        data = datas[0]
    else:
        raise Http404
    response = HttpResponse(data['datas'].decode('base64'), mimetype='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=' + data['datas_fname'].encode('utf-8')
    return response


def reload_cache(request, TYPE):
    if TYPE == '0':
        cache.set('shortcut_category_cache', cms_plugins.get_messages_categories('shortcut', request), 60 * 100)
    if TYPE == '1':
        cache.set('left_category_cache', cms_plugins.get_messages_categories_with_image('content_left', request),
                  60 * 100)
    if TYPE == '2':
        cache.set('right_category_cache', cms_plugins.get_messages_categories_with_image('content_right', request),
                  60 * 100)
    if TYPE == '3':
        cache.set('department_message_category_cache', cms_plugins.get_department_message_categories(request), 60 * 100)
    return HttpResponse("")

def lazy_load(request):
    id = int(request.GET.get("id"))
    default = int(request.GET.get("default")) if request.GET.has_key("default") else 8
    department_id = int(request.GET.get("dep_id")) if request.GET.has_key("dep_id") else None
    erpsession = request.erpsession
    message_obj = erpsession.get_model("message.message")
    domain = [('category_id', '=', id)]
    if department_id:
        domain.append(('department_id', '=', department_id))
    messages = message_obj.search_read(domain,
                                       ['category_message_title_meta_display', 'message_ids', 'name',
                                        "create_date_display"],
                                       limit=default)
    return HttpResponse(simplejson.dumps(messages, ensure_ascii=False))


# if __name__ == '__main__':
#     t = timeit.Timer('update_read_time(40834)', "from __main__ import update_read_time")
#     v = t.timeit(1000)
#     print v
