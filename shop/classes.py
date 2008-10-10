# -*- coding: utf-8 -*-

class CartItem:
    """ Класс объекта-корзины. """
    def __init__(self, title, count, price):
        self.title = title
        self.count = count
        self.price = price
        self.cost = count * price

