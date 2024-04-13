import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse, unquote
import json
from fastapi import FastAPI
import uuid

app = FastAPI()


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
    else:
      print(
          f"Изображение не сохранено, URL: {url} возвращает статус {response.status_code}"
      )
  except Exception as e:
    print(f"Ошибка при скачивании изображения {url}: {e}")
    return None


def create_db(filePath="images.json"):
  if not os.path.exists(filePath):
    with open(filePath, "w") as file:
      json.dump([], file)


def insert_image(url, filePath="images.json"):
  response = requests.get(url)
  if response.status_code == 404:
    print(f"Изображение по ссылке {url} не найдено (404). Пропускаем.")
    return
  with open(filePath, "r+") as file:
    images = json.load(file)
    images.append({"url": url})
    file.seek(0)
    file.truncate()
    json.dump(images, file)


def read_images(filePath="images.json"):
  with open(filePath, "r") as file:
    images = json.load(file)
  return images


def process_images(page_url):
  logo_icon_keywords = ['logo', 'icon', 'favicon']
  unwanted_url = "https://kubatura.ru/images/thumbnails/125/97/category/1943/\u043a\u0440\u0435\u0441\u043b\u0430.png"

  create_db()
  try:
    response = requests.get(page_url)
    if response.status_code == 404:
      print(f"Страница по URL {page_url} не найдена. Пропускаем.")
      return
    soup = BeautifulSoup(response.content, 'html.parser')
    images = soup.find_all('img')
    for img in images:
      img_url = img.get('src') or img.get('data-src')
      if not img_url or unquote(img_url) == unwanted_url:
        continue
      if not img_url.startswith(('http://', 'https://')):
        img_url = urlparse(page_url).scheme + "://" + urlparse(
            page_url).netloc + img_url

      if any(keyword in img_url.lower()
             for keyword in logo_icon_keywords) or 'category_menu' in img_url:
        print(f"Skipping logo, icon, or category menu image: {img_url}")
        continue

      if img_url.endswith('.png') or img_url.endswith(
          '.jpg') or img_url.endswith('.webp'):
        insert_image(img_url)
        print(f"Image URL {img_url} inserted")
      else:
        print(f"Skipped non-png/jpg/webp image URL: {img_url}")
  except Exception as e:
    print("Произошла ошибка:", e)


@app.get("/process/")
async def process_endpoint(page_url: str):
  process_images(page_url)
  return {"message": "Images have been processed"}


base_url = "https://kubatura.ru/mebel/divany-i-kresla/"
page_urls = [base_url] + [f"{base_url}page-{i}/" for i in range(2, 5)]

for url in page_urls:
  process_images(url)

images = read_images()
for img in images:
  print(img)
