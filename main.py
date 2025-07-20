import requests
from bs4 import BeautifulSoup
import json
import os
import time

HH_URL = 'https://hh.ru/search/vacancy?text=product+manager&excluded_text=&area=1&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=1&items_on_page=50&L_save_area=true&hhtmFrom=vacancy_search_filter'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}
SEEN_FILE = 'seen.json'
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def load_seen():
    try:
        with open(SEEN_FILE, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, 'w') as f:
        json.dump(list(seen), f)


def get_vacancies():
    urls = set()
    page = 0
    while True:
        paged_url = HH_URL + f"&page={page}"
        resp = requests.get(paged_url, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.find_all('a', {'data-qa': 'serp-item__title'})

        if not items:
            break

        for item in items:
            urls.add(item['href'])

        page += 1
        time.sleep(1)  # задержка для защиты от бана

    return urls


def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': text}
    requests.post(url, data=data)


def main():
    seen = load_seen()
    current = get_vacancies()
    new = current - seen

    if new:
        for url in new:
            send_telegram_message(url)
    else:
        send_telegram_message("Новых вакансий нет")

    save_seen(current)


if __name__ == "__main__":
    main()
