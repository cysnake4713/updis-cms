from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import Resource

__author__ = 'Zhou Guangwen'

class ERPObj(object):
    def __init__(self, request, data):
        self.request = request
        self.data = data

    def __getattr__(self, item):
        return getattr(self.data, item)


class ERPResource(Resource):
    def obj_get_list(self, request=None, **kwargs):
        erp_obj = request.erpsession.get_model(self._meta.erp_model)
        erps = erp_obj.search_read(self._meta.erp_domain, self._meta.erp_fields, limit=self._meta.limit)
        return [ERPObj(request=request, data=erp) for erp in erps]

    def dehydrate(self, bundle):
        bundle.data = bundle.obj.data
        return bundle


class CategoryResource(ERPResource):
    class Meta:
        resource_name = 'message_category'
        object_class = ERPObj
        erp_model = 'message.category'
        erp_domain = []
        erp_fields = ['name']

    def dehydrate(self, bundle):
        bundle = super(CategoryResource, self).dehydrate(bundle)
        message_obj = bundle.request.erpsession.get_model('message.message')
        bundle.data['messages'] = message_obj.search_read([('category_id', '=', bundle.data['id'])], ['name'],limit=20)
        return bundle


class MessageResource(ERPResource):
    class Meta:
        resource_name = 'message'
        object_class = ERPObj
        erp_model = 'message.message'
        erp_domain = []
        erp_fields = ['name', 'content', 'message_ids', 'write_uid', 'fbbm', 'image_medium', 'write_date',
                      'category_id']
