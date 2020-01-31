# -*- coding: utf-8 -*-

import requests
import threading
from bs4 import BeautifulSoup
from concurrent.futures import Future

from decorators import timer
from logging_config import _logger as logger

@timer
def job_ads():
    _url = 'https://ws054.juntadeandalucia.es'
    _second = '/eureka2/eureka-demandantes/'
    init_url = _url + _second + 'listadoOfertas.do'

    _vars = get_items_list(init_url)

    if not _vars:
        logger.error('Request a pagina Inicial no valido.')
        return

    _soup = _vars[0]
    list_items = _vars[1]
    _dir = get_next_page(_soup)

    _continue = True
    while _continue:
        for offer_query in list_items:
            future = generate_request(_url + _second + offer_query)
            future.add_done_callback(get_item_info)
        
        if not _dir and future.done:
            break
    
        _vars = get_items_list(_url + _dir)
        _soup = _vars[0]
        list_items = _vars[1]
        _dir = get_next_page(_soup)


def get_items_list(url):
    response = _request(url)
    if not response:
        return response
    _soup = BeautifulSoup(response.content, 'html.parser') 
    
    _class = ['imparlist', 'parlist']
    list_par = get_list(_soup, _class[0])
    list_impar = get_list(_soup, _class[1])
    list_items = list_par + list_impar
    return _soup, list_items


def get_next_page(soup):
    next_page = soup.find_all('li', class_='next')
    _dir = None
    for i in next_page:
        _next_page = i.text.strip().split()[0].lower()
        if _next_page == 'siguiente':
            a_href = i.find('a')
            _dir = a_href.get('href')
    return _dir


def _request(url):
    response = requests.get(url)
    if response.status_code != 200:
        logger.error('Status code: {} - url:{}'.format(response.status_code, url))
        return None
    return response


def get_list(_soup, _class):
    list_items = []
    tr = _soup.find_all('tr', class_=_class)
    for tr_item in tr:
        td = tr_item.find_all('td')
        for a in td:
            _a = a.find_all('a')
            for target in (_a):
                if not (target.get('target') == '_blank'):
                    list_items.append(target.get('href'))
    return list_items


def get_item_info(future):
    response = future.result()
    
    url = response.url
    _soup = BeautifulSoup(response.content, 'html.parser') 
    tbody = _soup.find_all('tbody')

    key = 'ofertaId'
    value = url.split('ofertaId=')[1].split('&')[0]
    item = {}
    item[key] = value
    for _tbody in tbody:
        tr = _tbody.find_all('tr')
        for _tr in tr:
            td = _tr.find_all('td')
            key = td[0].text.strip()
            value = td[1].text.strip()
            item[key] = value
    logger.info(item)


def generate_request(url):
    future = Future()

    thread = threading.Thread(
        target=(lambda: future.set_result(_request(url))))
        
    thread.start()
    return future

if __name__ == '__main__':
    job_ads()
