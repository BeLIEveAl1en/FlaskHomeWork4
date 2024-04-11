import os
import time

import requests
import threading
import multiprocessing
import asyncio
from aiohttp import ClientSession
from flask import Flask, request

app = Flask(__name__)


def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
            print(f"Downloaded {filename} from {url}")


def download_images_threading(urls):
    threads = []
    for url in urls:
        filename = url.split('/')[-1]
        t = threading.Thread(target=download_image, args=(url, filename))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


def download_images_multiprocessing(urls):
    processes = []
    for url in urls:
        filename = url.split('/')[-1]
        p = multiprocessing.Process(target=download_image, args=(url, filename))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


async def download_image_async(url, filename, session):
    async with session.get(url) as response:
        if response.status == 200:
            with open(filename, 'wb') as f:
                f.write(await response.read())
                print(f"Downloaded {filename} from {url}")


async def download_images_async(urls):
    tasks = []
    async with ClientSession() as session:
        for url in urls:
            filename = url.split('/')[-1]
            task = asyncio.create_task(download_image_async(url, filename, session))
            tasks.append(task)
        await asyncio.gather(*tasks)


@app.route('/download', methods=['POST'])
def download():
    urls = request.json.get('urls', [])
    if not urls:
        return "No URLs provided", 400

    start_time = time.time()

    download_images_threading(urls)

    download_images_multiprocessing(urls)

    asyncio.run(download_images_async(urls))

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total execution time: {total_time} seconds")

    return "Images downloaded successfully"


if __name__ == '__main__':
    app.run(debug=True)
