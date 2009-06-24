# -*- coding: utf-8 -*-

import random

from snippets import ajax_processor
from advice.models import Text

@ajax_processor(None)
def get_random_advice(request):
    """ Функция для получения случайного совета. """
    advices = Text.objects.filter(enabled=True)
    randomize = []

    for i in advices:
        randomize += int(i.weight * 10) * [i.id]

    index = random.randint(0, len(randomize)-1)
    choosen_advice_id = randomize[index]
    result = advices.get(id=choosen_advice_id)

    return {'code': 200,
            'title': result.title,
            'desc': result.desc}
