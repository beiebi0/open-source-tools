#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.ext import db


class Category(db.Model):
    name = db.StringProperty()
    owner = db.UserProperty()

    def is_exist(self):
        query = db.GqlQuery('SELECT * FROM Category WHERE \
            name = :1', self.name)
        category = query.get()
        if category:
            return category
        else:
            return False
    

class Item(db.Model):
    """
    """
    name = db.StringProperty()
    category = db.ReferenceProperty(Category, collection_name='items')

    def is_exist(self):
        query = db.GqlQuery('SELECT * FROM Item WHERE \
            name = :1 AND category = :2', self.name, self.category)
        item = query.get()
        if item:
            return item
        else:
            return False

    def remove_votes(self):
        for v in self.votes:
            return Vote.delete(v)

    def get_win(self):
        win = 0
        for vote in self.votes:
            if vote.vote_type == 'win':
                win += 1

        return win

    def get_lost(self):
        lost = 0
        for vote in self.votes:
            if vote.vote_type == 'lose':
                lost += 1

        return lost

    def get_percentage(self):
        win = self.get_win()
        total = self.get_win() + self.get_lost()
        if total:
            return (int)((win * 1.0) / total * 100)
        else:
            return 0


class Vote(db.Model):
    """
    """
    voter = db.UserProperty()
    vote = db.ReferenceProperty(Item, collection_name='votes')
    vote_type = db.StringProperty()
