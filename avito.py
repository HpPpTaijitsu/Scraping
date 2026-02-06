from bs4 import BeautifulSoup
import requests
from requests import get
import time
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

url = 'https://www.avito.ru/stavropol/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?localPriority=0&p='
houses = []
count = 1

while count <= 5:
    url_page = f'https://www.avito.ru/stavropol/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?localPriority=0&p={count}'
    print(f"Страница {count}: {url_page}")
    
    try:
        response = get(url_page, headers=headers, timeout=10)
        response.raise_for_status()
        
        html_soup = BeautifulSoup(response.text, 'html.parser')
        
        # План А: Ищем по data-marker
        house_data = html_soup.find_all('div', attrs={'data-marker': 'item'})
        
        # План Б: Ищем по классу карточки
        if not house_data:
            house_data = html_soup.find_all('div', class_='iva-item-root-G3n7u')
        
        if not house_data:
            house_data = html_soup.find_all('div', class_=lambda x: x and 'iva-item-root' in x)
        
        if house_data:
            print(f"Найдено квартир: {len(house_data)}")
            houses.extend(house_data)
            
            delay = 3 + random.random() * 7  # Рандомная задержка от 3 до 10 секунд чтобы не забанили
            print(f"Задержка: {delay:.2f} секунд")
            time.sleep(delay)
        else:
            print(f"Пустая страница или изменилась структура")
            print("Текущий HTML сохранен в debug.html для анализа")
            with open('debug.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            break
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        break
    
    count += 1

print(f"\nВсего собрано квартир: {len(houses)}")

if houses:
    print("ДАННЫЕ КВАРТИР:")
    
    # Первые 5 квартир
    for i, house in enumerate(houses[:5]):
        print(f"\nКвартира #{i+1}:")
        
        # 1. Заголовок
        title_tag = house.find('h3', attrs={'itemprop': 'name'}) or \
                   house.find('h3', class_=lambda x: x and ('title' in x or 'styles-module-root' in x)) or \
                   house.find('a', attrs={'data-marker': 'item-title'})
        
        title = title_tag.text.strip() if title_tag else "Нет заголовка"
        print(f"Заголовок: {title}")
        
        # 2. Цена
        price_tag = house.find('meta', attrs={'itemprop': 'price'}) or \
                   house.find('span', attrs={'data-marker': 'item-price'}) or \
                   house.find('span', class_=lambda x: x and ('price' in x or 'styles-module-root' in x))
        
        if price_tag:
            if price_tag.has_attr('content'):
                price = f"{price_tag['content']} ₽"
            else:
                price = price_tag.text.strip()
        else:
            price = "Нет цены"
        print(f"Цена: {price}")
        
        # 3. Ссылка
        link_tag = house.find('a', attrs={'data-marker': 'item-title'}) or \
                  house.find('a', attrs={'itemprop': 'url'}) or \
                  house.find('a', href=True)
        
        if link_tag and link_tag.has_attr('href'):
            link = f"https://www.avito.ru{link_tag['href']}"
            print(f"Ссылка: {link}")
        else:
            print("Ссылка: Нет ссылки")
        
        # 4. Дополнительная информация
        # Адрес/район
        address_tag = house.find('div', class_=lambda x: x and ('geo' in x or 'address' in x)) or \
                     house.find('span', attrs={'data-marker': 'item-address'})
        if address_tag:
            address = address_tag.text.strip()
            print(f"Адрес: {address}")
        
        # Параметры (метраж, этаж)
        params_tag = house.find('div', class_=lambda x: x and ('params' in x or 'iva-item-text' in x))
        if params_tag:
            params = params_tag.text.strip()
            print(f"Параметры: {params}")
        
        print("-" * 30)

else:
    print("Не удалось собрать данные.")