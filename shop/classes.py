# -*- coding: utf-8 -*-

class CartItem:
    """ Класс объекта-корзины. """
    def __init__(self, record, count, price):
        self.record = record
        self.count = count
        self.price = price
        self.cost = count * price

