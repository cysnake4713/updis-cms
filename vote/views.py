# -*- coding: utf-8 -*-
import datetime

import django.http
from django.shortcuts import render_to_response
from django.template import RequestContext


def get_votes(request):
    erpsession = request.erpsession
    vote_obj = erpsession.get_model("updis.vote")

    votes = vote_obj.search_read(domain=[('is_display', '=', True)], fields=['name', 'description', 'have_image'])
    return render_to_response("vote/vote.html", {'votes': votes},
                              context_instance=RequestContext(request))


def get_votes_record(request, vote__category_id):
    error = ""
    erpsession = request.erpsession
    vote_record_obj = erpsession.get_model("updis.vote.record")
    vote_records = vote_record_obj.search_read(domain=[('vote_category.id', '=', vote__category_id)],
                                               fields=['author', 'name', 'description', 'vote_logs', 'have_image'])
    vote_obj = erpsession.get_model("updis.vote")
    votes = vote_obj.search_read(domain=[('id', '=', vote__category_id)],
                                 fields=['name', 'start_time', 'end_time', 'allow_vote_time', 'comment', 'show_result'])
    if votes:
        votes = votes[0]
        start_time = datetime.datetime.strptime(votes['start_time'], "%Y-%m-%d")
        votes['start_time_small_than'] = (start_time.date() <= datetime.datetime.now().date())
        end_time = datetime.datetime.strptime(votes['end_time'], "%Y-%m-%d")
        votes['end_time_big_than'] = (end_time.date() >= datetime.datetime.now().date())

        #if its form post, log
        vote_logs_obj = erpsession.get_model("updis.vote.log")
        erp_user = request.session['erp_user']
        if erp_user:
            vote_logs = vote_logs_obj.search_read(
                domain=[('vote_category.id', '=', vote__category_id), ('voter.id', '=', erp_user['uid'])])
            if vote_logs:
                votes['is_voted'] = True
            else:
                votes['is_voted'] = False
        else:
            votes['is_voted'] = False

        if request.method == 'POST':
            if votes['is_voted'] is True:
                error = u"已经投过票了!"
            else:
                vote_record_list = request.REQUEST.getlist('vote_record')
                if len(vote_record_list) != votes['allow_vote_time']:
                    error = u"票数必须为%s票" % votes['allow_vote_time']
                else:
                    vote_record_list = [int(v) for v in vote_record_list]
                    params = {
                        'voter': erp_user['uid'],
                        'vote_category': int(vote__category_id),
                        # 'vote_time': datetime.datetime.utcnow(),
                        'vote_for': [(6, 0, vote_record_list)],
                    }
                    vote_logs_obj.create(params)
                    votes['is_voted'] = True
                    vote_records = vote_record_obj.search_read(domain=[('vote_category.id', '=', vote__category_id)],
                                                               fields=['author', 'name', 'description', 'vote_logs',
                                                                       'have_image'])

    else:
        raise django.http.Http404

    return render_to_response("vote/vote_record.html",
                              {'vote_records': vote_records, 'vote_category': votes, 'error': error},
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
