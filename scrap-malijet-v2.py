from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json
from datetime import datetime

browser_options = Options()
browser_options.headless = True
browser = webdriver.Firefox(options=browser_options)
browser.get('https://malijet.com')

ticker = browser.find_element(By.ID, 'mainTicker')

try:
    ne_pas_manquer = browser.find_element(By.CSS_SELECTOR, '#dynamic_box_center_boot .alert-success a')
except:
    ne_pas_manquer = None

try:
    urgent = browser.find_element(By.CSS_SELECTOR, '#dynamic_box_center_boot .alert-danger a')
except:
    urgent = None

try:
    alert = browser.find_element(By.CSS_SELECTOR, '#dynamic_box_center_boot .alert-danger:nth-child(2) a')
except:
    alert = None

headlines = browser.find_element(By.ID, 'rotating_headlines')

latest_news = browser.find_element(By.ID, 'box_paged_latest')

ticker_list = []
ticker_html_list = []
for t in ticker.find_elements(By.CSS_SELECTOR, "div.section a:not(span a)"):
    ticker_list.append({"title": t.get_property('text'), "link": t.get_attribute('href')})
    ticker_html_list.append(f"<li>{t.get_property('text')}</li>")

headlines_list = []
for h in headlines.find_elements(By.CSS_SELECTOR, '#rotating_headlines h3 b a'):
    headlines_list.append({"text": h.get_property('text'), "link": h.get_attribute('href')})

latest_news_list = []
for ln in latest_news.find_elements(By.CSS_SELECTOR, '#box_paged_latest a'):
    latest_news_list.append({"title": ln.get_property('text'), "link": ln.get_attribute('href')})

json_string = {
    "ticker": ticker_list,
    "headlines": headlines_list,
    "latest_news": latest_news_list,
    "ne_pas_manquer": {
        "title": ne_pas_manquer.text,
        "link": ne_pas_manquer
            .get_attribute('href')
    },
    "urgent": {
        "title": urgent.text,
        "link": urgent
            .get_attribute('href')
    },
    # "alerte": {
    #     "title": alert.text,
    #     "link": alert.find_element(By.CSS_SELECTOR, 'div > a').get_attribute('href')
    # } if alert is not None else {},
}

today_date = datetime.today().strftime('%Y-%m-%d')
html_content = f"""
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>Resumé des articles Malijet du {today_date}</title>
</head>
<body>
    <ul>
        {ticker_html_list}
    </ul>
</body>
</html>
"""

index_html = open(f'index-{today_date}.html', 'w')
index_html.write(html_content)
index_html.close()

with open('dumped_new.json', 'w', encoding="utf-8") as output:
    json.dump(json_string, output, ensure_ascii=False)

browser.quit()


