import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse, unquote
import sqlite3
from fastapi import FastAPI
import uuid

app = FastAPI()

def init_db(db_path='images.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def download_image(url, folder="downloaded_images"):
    os.makedirs(folder, exist_ok=True)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_name = os.path.basename(urlparse(url).path)
            file_path = os.path.join(folder, file_name)
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Изображение сохранено: {file_path}")
            return file_path
    except Exception as e:
        print(f"Ошибка при скачивании изображения {url}: {e}")
        return None

def insert_image(url, db_path="images.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    new_id = str(uuid.uuid4())
    cursor.execute('INSERT INTO images (id, url) VALUES (?, ?)', (new_id, url))
    conn.commit()
    conn.close()
    return new_id

def read_images(db_path="images.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM images')
    images = cursor.fetchall()
    conn.close()
    return images

def process_images(page_url):
    logo_icon_keywords = ['logo', 'icon', 'favicon']
    unwanted_url = "https://kubatura.ru/images/thumbnails/125/97/category/1943/\u043a\u0440\u0435\u0441\u043b\u0430.png"
    init_db()
    try:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img')
        for img in images:
            img_url = img.get('src') or img.get('data-src')
            if not img_url or unquote(img_url) == unwanted_url:
                continue
            if not img_url.startswith(('http://', 'https://')):
                img_url = urlparse(page_url).scheme + "://" + urlparse(page_url).netloc + img_url
            if any(keyword in img_url.lower() for keyword in logo_icon_keywords) or 'category_menu' in img_url:
                print(f"Skipping logo, icon, or category menu image: {img_url}")
                continue
            if img_url.endswith('.png') or img_url.endswith('.jpg') or img_url.endswith('.webp'):
                image_id = insert_image(img_url)
                print(f"Image URL {img_url} inserted with ID: {image_id}")
            else:
                print(f"Skipped non-png/jpg/webp image URL: {img_url}")
    except Exception as e:
        print("Произошла ошибка:", e)

@app.get("/process/")
async def process_endpoint(page_url: str):
    process_images(page_url)
    return {"message": "Images have been processed"}

base_url = "https://your_website/page/"
page_urls = [base_url] + [f"{base_url}page-{i}/" for i in range(2, 40)]

for url in page_urls:
    process_images(url)

images = read_images()
for img in images:
    print(img)
