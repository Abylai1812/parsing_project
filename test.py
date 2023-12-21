import requests
from bs4 import BeautifulSoup
import json

all_books_data = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for page_number in range(1, 3):
    page_url = f'https://www.marwin.kz/books/?from=block2&p={page_number}'
    response = requests.get(page_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')

        book_cards = soup.find_all('div', {'class': 'product-item-info'})

        for card in book_cards:
            title = card.find('a', {'class': 'product-item-link'}).text.strip()
            price = card.find('span', {'class': 'price'}).text.strip()

            book_url = card.find("a").get("href")

            if '/press/express-delivery.html' not in book_url: # лишный url
                book_response = requests.get(book_url, headers=headers)
                book_soup = BeautifulSoup(book_response.text, 'html.parser')
                additional_data = book_soup.find('div', class_= 'product attribute description').text.strip()
                breadcrumbs = book_soup.find('ul', class_='items')
                if breadcrumbs:
                    genre_element = breadcrumbs.find_all('li')[2]

                if genre_element and genre_element.find('a'):
                    genre = genre_element.find('a').text.strip()
                                    
                all_books_data.append({
                    'Название': title,
                    'Цена': price,
                    'Жанр': genre,
                    'Описание': additional_data
                })
    else:
        print(f"Ошибка при загрузке страницы: {page_url}")

with open('books_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_books_data, json_file, ensure_ascii=False, indent=4)

with open('books_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

genre_count = {}
lowest_price_book = None
lowest_price = float('inf')

for book in data:
    genre = book["Жанр"]
    price = float(book["Цена"].replace("₸", "").replace(" ", "").replace(" ", ""))
    
    genre_count[genre] = genre_count.get(genre, 0) + 1
    
    if price < lowest_price:
        lowest_price = price
        lowest_price_book = book

print("Число книг каждого жанра:")
for genre, count in genre_count.items():
    print(f"{genre}: {count} книг")

print("\nСамая дешевая книга:")
print(f"Название: {lowest_price_book['Название']}")
print(f"Жанр: {lowest_price_book['Жанр']}")
print(f"Цена: {lowest_price_book['Цена']}")