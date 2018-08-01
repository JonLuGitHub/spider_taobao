# coding=gbk

import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq
from config import *
from urllib.parse import quote


#options = webdriver.ChromeOptions()
#options.add_argument('--ignore-certificate-errors')
#browser = webdriver.Chrome(chrome_options=options)
browser = webdriver.Chrome()

wait = WebDriverWait(browser, 10)
KEYWORD = 'iPad'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


def index_page(page):
    """ץȡ����ҳ"""
    print('������ȡ��', page, 'ҳ')
    try:
        url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
        browser.get(url)
        if page > 1:
            input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                 '#mainsrp-pager div.form > input')))
            submit = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 
                '#mainsrp-pager div.form > span.btn.J_Submit')))
            input.clear()
            input.send_keys(page)
            submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, 
            '#mainsrp-pager li.item.active > span'),str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 
            '.m-itemlist .item .item')))
        get_products()
    except TimeoutException:
        index_page(page)
        
        
def get_products():
    """��ȡ��Ʒ����"""
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('data-src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)
        
        
def save_to_mongo(result):
    """������MongoDB"""
    try:
        if db[MONGO_COLLECTION].insert(result):
            print('�洢��MongoDB�ɹ�')
    except Exception:
        print('�洢��MongoDBʧ��')
        
        
def main():
    """����ÿһҳ"""
    for i in range(1, MAX_PAGE +1):
        index_page(i)
    browser.close()
    
    
if __name__ == '__main__':
    main()
    
