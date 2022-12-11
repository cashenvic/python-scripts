from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from mysql.connector import connect, Error
from dotenv import load_dotenv
import json
import time
import os


class Style:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


extension_path = './ublock_origin-1.44.4.xpi'
item_id = input('What is the item page id ?\n')
url = f'https://fr.aliexpress.com/item/{item_id}.html'

item_title = None
item_price = None
item_promo_price = None
item_full_description = None
item_images = []

browser_options = Options()
browser_options.headless = True
browser = webdriver.Firefox(options=browser_options)
print(Style.CYAN + 'installing ublock addon')
browser.install_addon(extension_path)

browser.get(url)

try:
    browser.execute_script("window.scrollTo(0,1482);")
    print(Style.CYAN + 'waiting 15 sec for images to load')
    time.sleep(15)

    print(Style.CYAN + 'getting title')
    title = browser.find_elements(By.CLASS_NAME, 'product-title-text')
    if len(title) > 0:
        item_title = title[0].text

    print(Style.CYAN + 'getting price')
    price = browser.find_elements(By.CLASS_NAME, 'product-price-value')
    if len(price) > 0:
        item_price = price[0].text

    print(Style.CYAN + 'getting promo price')
    price = browser.find_elements(By.CLASS_NAME, 'uniform-banner-box-price')
    if len(price) > 0:
        item_price = price[0].text

    print(Style.CYAN + 'getting images')
    images = []
    description = browser.find_elements(By.CLASS_NAME, 'detail-desc-decorate-richtext')
    if len(description) > 0:
        for image in description[0].find_elements(By.CSS_SELECTOR, 'p img'):
            images.append(image.get_property('src'))

    print(Style.CYAN + 'getting full description')
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

    print(Style.CYAN + 'writing output file')
    with open(f"{os.path.join(os.path.dirname(__file__), f'./data/item_{item_id}_dump.json')}", 'w',
              encoding="utf-8") as output:
        json.dump(json_string, output, ensure_ascii=False)

    print(Style.GREEN + 'information gathering process has ended successfully')
finally:
    browser.quit()

if json_string is not None:
    print(Style.CYAN + 'connecting to database')
    load_dotenv()
    try:
        with connect(
                host=os.environ.get("db_host"),
                user=os.environ.get("db_user"),
                password=os.environ.get("db_password"),
                database=os.environ.get("db_name")
        ) as connection:
            print(Style.GREEN + 'connected successfully to database')

        check_product = """
            SELECT id FROM products WHERE product_id = %s
        """
        insert_product_query = """
            INSERT INTO products
            (product_id, url, title, price, promo_price, full_description, images_urls)
            VALUES ( %s, %s, %s, %s, %s, %s, %s )
        """
        item_to_insert = (
            item_id,
            json_string.get("url"),
            json_string.get("title"),
            json_string.get("price"),
            json_string.get("promo_price"),
            json_string.get("full_description"),
            ','.join(json_string.get("images")),
        )
        update_product_query = """
            UPDATE products SET 
            url=%s,
            title=%s,
            price=%s,
            promo_price=%s,
            full_description=%s,
            images_urls=%s
            WHERE product_id=%s
        """
        item_to_update = (
            json_string.get("url"),
            json_string.get("title"),
            json_string.get("price"),
            json_string.get("promo_price"),
            json_string.get("full_description"),
            ','.join(json_string.get("images")),
            item_id,
        )
        try:
            connection.reconnect()
            product_id = None
            with connection.cursor() as cursor:
                cursor.execute(check_product, (item_id,))
                for (id) in cursor:
                    product_id = id

                if product_id is None:
                    print(Style.CYAN + 'inserting item to database')
                    cursor.execute(insert_product_query, item_to_insert)
                    connection.commit()
                    print(Style.GREEN + 'successfully INSERTED item into database')
                else:
                    print(Style.YELLOW + f'this product exists: {product_id}; updating')
                    cursor.execute(update_product_query, item_to_update)
                    connection.commit()
                    print(Style.GREEN + 'successfully UPDATED item')
        except Error as err:
            print(Style.RED + err.msg)
            connection.close()

    except Error as e:
        print(Style.RED + 'Error connecting database')
        print(e)
