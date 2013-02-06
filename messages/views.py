# Create your views here.
import base64
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from sekizai.context import SekizaiContext
from messages.forms import CommentForm, LoginForm
from openerplib import AuthenticationError

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
    message_obj = req.erpsession.get_model('message.message')
    comment_obj = req.erpsession.get_model('mail.message')
    partner_obj = req.erpsession.get_model('res.partner')
    attachment_obj = req.erpsession.get_model('ir.attachment')

    messages = message_obj.search_read([('id', '=', message_id)],
        ['name', 'message_meta_display', 'content', 'message_ids', 'message_summary'])
    message = messages[0]
    comments = comment_obj.read(message['message_ids'], ['body', 'date', 'subject', 'author_id', 'is_anonymous'])
    for comment in comments:
        comment.update(partner_obj.read(comment.get('author_id')[0], ["image_small"]))
    if req.method == 'POST':
        form = CommentForm(req.POST, req.FILES)
        if form.is_valid():
            params = {
                'body': form.cleaned_data['body'],
                'type': 'comment',
                'model': 'message.message',
                'res_id': message.get('id'),
                'is_anonymous': form.cleaned_data['is_anonymous'],
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
            comment_id = comment_obj.create(params)
            if form.cleaned_data['attachment']:
                attachment_obj.write([attachment_id], {'res_model': 'mail.message', 'res_id': comment_id})
            return HttpResponseRedirect(req.path)
    else:
        form = CommentForm()
    return render_to_response("messages/detail.html", {'message': message,
                                                       'comments': comments,
                                                       'form': form,
    },
        context_instance=RequestContext(req))


@cache_page(60 * 15)
def index(req):
    return render_to_response("messages/index.html", context_instance=RequestContext(req))


def by_category(req, category_id):
    erpsession = req.erpsession
    category_id = int(category_id)
    message_category_obj = erpsession.get_model("message.category")

    message_category = message_category_obj.search_read([('id', '=', category_id)])[0]
    per_page = int(req.GET.get('per_page', 8))
    paginator = Paginator(MessageList(erpsession, [('category_id', '=', category_id)],
        ['name', 'content', 'message_ids', 'write_uid', 'fbbm', 'image_medium', 'write_date', 'category_id']), per_page)
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


def login(request):
    default_url = reverse('zh-CN:messages_index')
    redirect_url = request.GET.get('redirect_url',default_url)
    if request.method == 'POST':
        form = LoginForm(request.POST,request=request)
        if form.is_valid():
                return HttpResponseRedirect(redirect_url)
    else:
        form = LoginForm(request=request)
    return render_to_response("messages/login.html", {'form':form}, context_instance=RequestContext(request))