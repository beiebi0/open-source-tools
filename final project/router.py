#!/usr/bin/env python
# -*- coding: utf-8 -*-
import views
import test
from google.appengine.ext import webapp

application = webapp.WSGIApplication([
                                    ('/', views.MainPage),
                                    ('/category/item/(.*)', views.Item_View),
                                    ('/category/(.*)', views.Category_View),
                                    ],
                                    debug=True)
