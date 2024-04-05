# ImageSpace

ImageSpace is a Python application that downloads images from web pages, filters out certain types of images, and stores the valid images in a SQLite database. It utilizes the FastAPI framework for providing an API endpoint to process web pages and extract images. The application also includes functionality to create a local database for storing the image URLs.

## Features
- Download images from web pages
- Filter out specific types of images
- Store valid images in a SQLite database
- API endpoint for processing web pages and extracting images
- Local database creation for storing image URLs

## Technologies Used
- Python
- Requests library
- BeautifulSoup library
- SQLite
- FastAPI

## Installation
1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the application using `uvicorn main:app --reload`.

Feel free to contribute and improve this application!
