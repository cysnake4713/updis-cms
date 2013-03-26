from django.core.urlresolvers import reverse
from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _
from openerplib import get_connection, Service

__author__ = 'Zhou Guangwen'


class TestMenu(Menu):
    def get_nodes(self, request):
        nodes = []
        service = get_connection("localhost", database="test").get_service("common")
        menu_obj = request.erpsession.get_model("internal.home.menu")
        #        top_menu_id = menu_obj.search([("name","=","Top menu")])
        menus = menu_obj.search_read([], ['name', 'complete_name', 'parent_id', "action"])
        for menu in menus:
            parent_id = menu['parent_id'] and menu['parent_id'][0] or None
            node = NavigationNode(menu['name'], '/', menu['id'], parent_id=parent_id)
            nodes.append(node)
        return nodes


menu_pool.register_menu(TestMenu)