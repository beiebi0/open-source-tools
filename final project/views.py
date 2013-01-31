#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from models import *
from xml.etree import ElementTree  as et
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required

class View(webapp.RequestHandler):
    """
    """
    def __init__(self):
        super(View, self).__init__()
        self.cur_user = users.get_current_user()
        self.get_handlers = {}
        self.post_handlers = {}

    @login_required
    def get(self, method='index'):
        if method in self.get_handlers:
            self.get_handlers[method]()
        else:
            self.redirect('/')

    def post(self, method=None):
        if method in self.post_handlers:
            self.post_handlers[method]()
        else:
            self.redirect('/')

    def get_basic_info(self):
        if self.cur_user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        basic_info = {
                'url': url,
                'url_linktext': url_linktext,
                'username': self.cur_user.nickname(),
            }
        return basic_info

    def show_msg(self, result):
        self.response.out.write(template.render('template/info.html', result))


class MainPage(View):
    """
    """
    def __init__(self):
        super(MainPage, self).__init__()
        self.get_handlers = {
            'index': self.index
        }
        self.post_handlers = {
        }

    def index(self, info=None):
        if not info:
            info = self.get_basic_info()
        categories = Category.all()
        info['categories'] = categories
        info['home_state'] = 'active'
        self.response.out.write(template.render('template/index.html', info))


class Category_View(View):
    """
    """
    def __init__(self):
        super(Category_View, self).__init__()
        self.get_handlers = {
            'create':  self.create,
            'remove':  self.remove,
            'update':  self.update,
            'index':  self.index,
            'import': self.import_view,
            'export': self.export,
            'results': self.get_all_result,
            'view': self.view,
            'view_result': self.view_result
        }

        self.post_handlers = {
            'create':  self.create,
            'update':  self.update,
            'import':  self.import_categery,
            'vote':  self.vote,
        }

    def index(self):
        user = users.get_current_user()
        c_query = db.GqlQuery('SELECT * FROM Category WHERE \
        owner = :1', user)
        data = {
            'categories': c_query,
            'del_url': 'remove?key=',
            'up_url': 'update?key=',
            'edit_item_url': 'item/update?key=',
            'del_item_url':  'item/remove?key=',
            'category_state': 'active',
            'export_url':  'export?key=',
            'add_url':  'item/add?key=',
        }
        data.update(self.get_basic_info())
        return self.response.out.write(
            template.render('template/view_category.html', data))

    def view_result(self):
        key = self.request.GET.multi.get('key', None)
        if not key:
            self.redirect('/')
        category = Category.get(key)
	items = db.GqlQuery('SELECT * FROM Item WHERE category =:1', category)
	def getPen(Item):
		return Item.get_percentage()
	items=sorted(items,key=getPen,reverse=True)
        info = self.get_basic_info()
        info['category'] = category
	info['items'] = items
        return self.response.out.write(
            template.render('template/results.html', info))

    def view(self):
        key1 = self.request.GET.multi.get('key1', None)
        key2 = self.request.GET.multi.get('key2', None)
        voted = self.request.GET.multi.get('voted', None)
        key = self.request.GET.multi['key']
        category = Category.get(key)
        info = self.get_basic_info()
        items = db.GqlQuery('SELECT * FROM Item WHERE category = :1',
                            category)
        #items.filter('category =', cateogry)
        total_item = items.count()
        if total_item > 2:
            my_item = items.fetch(2, random.randint(0, total_item - 2))
        else:
            my_item = items
        if key1:
            item1 = Item.get(key1)
            item2 = Item.get(key2)
            voted_item = [item1, item2]
            voted = int(voted)
            info['voted'] = voted_item[voted - 1]
            info['voted_item'] = voted_item
        info['category'] = category
        info['my_item'] = my_item
        return self.response.out.write(
            template.render('template/vote_page.html', info))

    def export(self):
        """
        """
        key = self.request.GET.multi.get('key', None)
        self.export_categery(key)

    def import_view(self):
        data = self.get_basic_info()
        self.response.out.write(
                template.render('template/import_category.html', data))

    def create(self):
	info = self.get_basic_info()
        user = users.get_current_user()
        name = self.request.get('name')
        if not name:
            return self.response.out.write(
                    template.render('template/category.html', info))
        else:
            category = Category(name=name, owner=user)
            query = db.GqlQuery('SELECT * FROM Category WHERE name = :1', name)
            old_category = query.get()
            if old_category:
                result = {
                    'state': False,
                    'msg': 'Category %s exists!' % old_category.name
                }
                info['result'] = result
                self.show_msg(info)
                return False
            else:
                category.put()
            item_names = self.request.get('item_name', allow_multiple=True)
            for iname in item_names:
                if iname:
                    new_item = Item(name=iname, category=category)
                    new_item.put()
            self.redirect('/category/index')

    def remove(self):
        key_id = self.request.get('key')
        category = Category.get(key_id)
        category.delete()
        self.redirect('/category/index')

    def update(self):
        new_name = self.request.get('name')
        key_id = self.request.get('key')
        category = Category.get(key_id)
        if not new_name:
            data = {
                'category': category,
            }
            data.update(self.get_basic_info())
            return self.response.out.write(
                    template.render('template/edit_category.html', data))
        else:
            category.name = new_name
            category.put()
            self.redirect('/category/index')

    def import_categery(self):
        # make sure name uniq, or have privilege to change it
        xml_text = self.request.POST.multi['xml_file'].file.read()
        categories = self.get_xml_catergorys(xml_text)
        for category_info in categories:
            category = Category(name=category_info['name'],
                                owner=self.cur_user)
            old_category = category.is_exist()
            if old_category:
                if old_category.owner != self.cur_user:
                    result = {
                        'state': False,
                        'msg': 'You can not replace category %s, permission \
                        denied.' % old_category.name
                    }
                    return result
                else:
                    remove_item = [item for item in old_category.items if \
                                    item.name not in category_info['items']]
                    for item in remove_item:
                        item.remove_votes()
                        Item.delete(item)
                    for item_name in category_info['items']:
                        item = Item(name=item_name, category=old_category)
                        old_item = item.is_exist()
                        if not old_item:
                            item.put()
            else:
                category.put()
                for item_name in category_info['items']:
                    item = Item(name=item_name, category=category)
		    item.put()
        self.redirect('/category/index')

    def export_categery(self, key=None):
        xml_string = ''
        if not key:
            for category in Category.all():
                xml_string += self.categery_to_xml(category)
            xml_string = '<root>' + xml_string + '</root>'
        else:
            category = Category.get(key)
            xml_string = self.categery_to_xml(category)
        self.response.headers['Content-Type'] = 'text'
        self.response.out.write(xml_string)

    def categery_to_xml(self, category):
        if not category:
            return ''
        xml_string = "<CATEGORY>\n\t<NAME>%s</NAME>\n" % category.name
        for item in category.items:
            xml_string += "\t<ITEM>\n\t  <NAME>%s</NAME>\n\t</ITEM>\n" % item.name
        xml_string += "</CATEGORY>"
        return xml_string

    def get_xml_catergorys(self, xml_text):
        """
        """
        root = et.fromstring(xml_text)
        categories = []
        for node in root.getiterator('CATEGORY'):
            name = node.find('NAME').text
            items = []
            for item in node.findall('ITEM'):
                items.append(item.find("NAME").text)

            category = {
                'name': name,
                'items': items
            }
            categories.append(category)

        return categories

    def vote(self):
        item_key = self.request.get('vote_item')
        item1_key = self.request.get('item1')
        item2_key = self.request.get('item2')
        category = self.request.get('category')
        if item_key == item1_key:
            lost_key = item2_key
            voted = 1
        else:
            lost_key = item1_key
            voted = 2
        lost_item = Item.get(lost_key)
        item = Item.get(item_key)
        vote = Vote(voter=self.cur_user, vote=item, vote_type='win')
        lost_vote = Vote(voter=self.cur_user, vote=lost_item, vote_type='lose')
        vote.put()
        lost_vote.put()
        info = self.get_basic_info()
        info['voted_item'] = item
        info['lost_item'] = lost_item
        info['my_item'] = [item, lost_item]
        url = '/category/view?key=' + category + '&&key1=' + item_key + \
        '&&key2=' + lost_key + '&&voted=' + str(voted)

        self.redirect(url)

    def get_all_result(self):
        pass
#        return self.response.out.write(
#            template.render('template/results.html', data))


class Item_View(View):
    """
    """
    def __init__(self):
        """
        """
        super(Item_View, self).__init__()
        self.get_handlers = {
            'update':  self.update,
            'remove':  self.remove,
            'add':  self.add,
        }
        self.post_handlers = {
            'update': self.update,
            'add': self.add,
        }

    def update(self):
        item_key = self.request.get('key')
        item = Item.get(item_key)
        new_name = self.request.get('name')
        data = {
            'item':  item,
        }
        data.update(self.get_basic_info())
        if not new_name:
            return self.response.out.write(
                    template.render('template/edit_item.html', data))
        else:
            item.name = new_name
	    item.remove_votes()
            item.put()
            self.redirect('/category/index')

    def remove(self):
        item_key = self.request.get('key')
        item = Item.get(item_key)
        item.remove_votes()
        item.delete()
        self.redirect('/category/index')

    def add(self):
        category_key = self.request.get('key')
        category = Category.get(category_key)
        new_item = self.request.get('name')
        data = self.get_basic_info()
        if not new_item:
            return self.response.out.write(
                    template.render('template/edit_item.html', data))
        else:
            item = Item(name=new_item, category=category)
            item.put()
            self.redirect('/category/index')
