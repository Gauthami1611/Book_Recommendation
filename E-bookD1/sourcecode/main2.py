import pymysql
conn=pymysql.connect(host="localhost", user="root", password="Gauthu@12", db="e_book")
cursor=conn.cursor()

import pandas as pd
import requests

def get_books_by_category(subject, max_results=10):
    url = f"https://www.googleapis.com/books/v1/volumes?q=subject:{subject}&maxResults={max_results}"
    response = requests.get(url)
    data = response.json()

    books = []

    if 'items' in data:
        for item in data['items']:
            volume_info = item.get('volumeInfo', {})

            book = {
                'Title': volume_info.get('title'),
                'Author': volume_info.get('authors', ['Unknown'])[0],
                'Publisher': volume_info.get('publisher', 'Unknown'),
                'Published Date': volume_info.get('publishedDate', 'Unknown'),
                'Description': volume_info.get('description', 'No description available'),
                'Cover URL': volume_info.get('imageLinks', {}).get('thumbnail'),
                'Categories': ", ".join(volume_info.get('categories', ['Uncategorized']))
            }

            books.append(book)

    return books


try:
    with conn.cursor() as cursor:
        books = get_books_by_category("children+fiction", max_results=10)
        for book in books:
            sql = """
                INSERT INTO not_rated (title, author, publisher, published_date, description, cover_url, categories, rating)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                book['Title'],
                book['Author'],
                book['Publisher'],
                book['Published Date'],
                book['Description'],
                book['Cover URL'],
                book['Categories'],
                0.0
            ))

    conn.commit()
    print("Books inserted successfully!")

except Exception as e:
    print("Error inserting books:", e)