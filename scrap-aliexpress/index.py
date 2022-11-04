from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json
import time


extension_path = './ublock_origin-1.44.4.xpi'
item_id = input('What is the item page id ?\n')
url = f'https://fr.aliexpress.com/item/{item_id}.html'

item_title = None
item_price = None
item_promo_price = None
item_full_description = None
item_images = []

browser_options = Options()
browser_options.headless = False
browser = webdriver.Firefox(options=browser_options)
print('installing ublock addon')
browser.install_addon(extension_path)

browser.get(url)

try:
    browser.execute_script("window.scrollTo(0,1482);")
    print('waiting 15 sec for images to load')
    time.sleep(15)

    print('getting title')
    title = browser.find_elements(By.CLASS_NAME, 'product-title-text')
    if len(title) > 0:
        item_title = title[0].text

    print('getting price')
    price = browser.find_elements(By.CLASS_NAME, 'product-price-value')
    if len(price) > 0:
        item_price = price[0].text

    print('getting promo price')
    price = browser.find_elements(By.CLASS_NAME, 'uniform-banner-box-price')
    if len(price) > 0:
        item_price = price[0].text

    print('getting images')
    images = []
    description = browser.find_elements(By.CLASS_NAME, 'detail-desc-decorate-richtext')
    if len(description) > 0:
        for image in description[0].find_elements(By.CSS_SELECTOR, 'p img'):
            images.append(image.get_property('src'))

    print('getting full description')
    description = browser.find_elements(By.ID, 'product-description')
    if len(description) > 0:
        item_full_description = description[0].get_attribute('innerHTML')

    json_string = {
        "url": url,
        "title": item_title,
        "price": item_price,
        "promo_price": item_promo_price,
        "full_description": item_full_description,
        "images": images
    }

    print('writing output file')
    with open(f'./data/item_{item_id}_dump.json', 'w', encoding="utf-8") as output:
        json.dump(json_string, output, ensure_ascii=False)

    print('information gathering process has ended successfully')
finally:
    browser.quit()

