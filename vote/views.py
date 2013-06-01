# Create your views here.
import datetime

import django.http
from django.shortcuts import render_to_response
from django.template import RequestContext


def get_votes(request):
    erpsession = request.erpsession
    vote_obj = erpsession.get_model("updis.vote")

    votes = vote_obj.search_read(domain=[('is_display', '=', True)], fields=['name', 'description'])
    return render_to_response("vote/vote.html", {'votes': votes},
                              context_instance=RequestContext(request))


def get_votes_record(request, vote__category_id):
    erpsession = request.erpsession
    vote_record_obj = erpsession.get_model("updis.vote.record")
    vote_records = vote_record_obj.search_read(domain=[('vote_category.id', '=', vote__category_id)],
                                               fields=['author', 'name', 'description', ])
    vote_obj = erpsession.get_model("updis.vote")
    votes = vote_obj.search_read(domain=[('id', '=', vote__category_id)], fields=['name', 'start_time', 'end_time'])
    if votes:
        votes = votes[0]
        start_time = datetime.datetime.strptime(votes['start_time'], "%Y-%m-%d")
        votes['start_time_small_than'] = (start_time.date() <= datetime.datetime.now().date())
        end_time = datetime.datetime.strptime(votes['end_time'], "%Y-%m-%d")
        votes['end_time_big_than'] = (end_time.date() >= datetime.datetime.now().date() )
    else:
        raise django.http.Http404
    return render_to_response("vote/vote_record.html", {'vote_records': vote_records, 'vote_category': votes},
                              context_instance=RequestContext(request))


def get_votes_detail(request, vote_record_id):
    erpsession = request.erpsession
    vote_record_obj = erpsession.get_model("updis.vote.record")
    vote_records = vote_record_obj.search_read(
        domain=[('id', '=', vote_record_id)], fields=['name', 'vote_category', 'author', 'content', 'description'])
    if vote_records:
        vote_record = vote_records[0]
    else:
        raise django.http.Http404

    return render_to_response("vote/vote_detail.html", {'vote_record': vote_record},
                              context_instance=RequestContext(request))


def get_image(request, id, model, field):
    erp_session = request.erpsession

    id = int(id)
    image_obj = erp_session.get_model(model)

    images = image_obj.search_read([('id', '=', id)], [field])
    if images:
        image = images[0]
    else:
        raise django.http.Http404
    response = django.http.HttpResponse(image[field].decode('base64'))
    response['Content-Type'] = 'image/png'
    return response
