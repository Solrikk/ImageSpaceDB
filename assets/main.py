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
  with open(filePath, "r+") as file:
    images = json.load(file)
    if not any(image['url'] == url
               for image in images):  # Check if URL already exists
      images.append({"url": url})
      file.seek(0)
      file.truncate()
      json.dump(images, file)


def read_images(filePath="images.json"):
  with open(filePath, "r") as file:
    images = json.load(file)
  return images


def process_images(page_url):
  create_db()
  try:
    response = requests.get(page_url)
    if response.status_code == 404:
      print(f"Страница по URL {page_url} не найдена. Пропускаем.")
      return
    soup = BeautifulSoup(response.content, 'html.parser')
    main_photos_links = soup.find_all(
        'a', class_='ecl-owl-carousel-main__thumbs-place')
    for link in main_photos_links:
      product_page_url = link.get('href')
      if product_page_url:
        print(
            f"Найдена ссылка на главную фотографию товара: {product_page_url}")
        insert_image(product_page_url)
  except Exception as e:
    print(f"Произошла ошибка при обработке страницы {page_url}: {e}")


@app.get("/process/")
async def process_endpoint(page_url: str):
  process_images(page_url)
  return {"message": "Images have been processed"}


base_url = "https://kubatura.ru/mebel/divany-i-kresla/"
page_urls = [base_url] + [f"{base_url}page-{i}/" for i in range(2, 100)]

for url in page_urls:
  process_images(url)

images = read_images()
for img in images:
  print(img)
