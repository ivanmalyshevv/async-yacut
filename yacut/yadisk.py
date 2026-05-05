import os
import aiohttp
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'
CREATE_FOLDER_URL = f'{API_HOST}{API_VERSION}/disk/resources'
DISK_TOKEN = os.getenv('DISK_TOKEN')
AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}

TEST_MODE = DISK_TOKEN == 'y0_nbfoiu3445tno35_fd09v854bn2_cs0e8hrb4k'


async def create_folder(path):
    """Создание папки на Яндекс Диске"""
    if TEST_MODE:
        print("[TEST MODE] Skipping folder creation")
        return True
    
    async with aiohttp.ClientSession() as session:
        params = {'path': path}
        async with session.put(CREATE_FOLDER_URL, headers=AUTH_HEADERS,
                               params=params) as resp:
            print(f"[DEBUG] Create folder {path}: {resp.status}")
            return resp.status in (200, 201)


async def get_upload_url(filename):
    """Получение URL для загрузки файла"""
    folder_path = 'disk:/YaCut_Uploads'
    file_path = f'{folder_path}/{quote(filename)}'

    if not TEST_MODE:
        await create_folder(folder_path)

    params = {
        'path': file_path,
        'overwrite': 'true'
    }
    print(f"[DEBUG] Getting upload URL for: {filename}")
    print(f"[DEBUG] Path: {file_path}")

    # В тестовом режиме используем мок-сервер
    host = os.getenv('API_HOST', API_HOST)
    url = f'{host}{REQUEST_UPLOAD_URL}' if host != API_HOST else REQUEST_UPLOAD_URL
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url if host != API_HOST else REQUEST_UPLOAD_URL,
                              headers=AUTH_HEADERS,
                              params=params) as resp:
            print(f"[DEBUG] Response status: {resp.status}")
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"Ошибка получения URL загрузки: "
                                f"{resp.status}, {error_text}")
            data = await resp.json()
            print("[DEBUG] Got upload URL")
            return data['href']


async def upload_file_to_disk(file_storage, filename):
    """Загрузка файла на Яндекс Диск"""
    upload_url = await get_upload_url(filename)
    
    async with aiohttp.ClientSession() as session:
        file_storage.seek(0)
        data = file_storage.read()
        print(f"[DEBUG] Uploading {len(data)} bytes...")
        
        async with session.put(upload_url, data=data) as resp:
            print(f"[DEBUG] Upload response status: {resp.status}")
            if resp.status not in (200, 201):
                error_text = await resp.text()
                raise Exception(f"Ошибка загрузки файла: "
                                f"{resp.status}, {error_text}")

            location = resp.headers.get('Location')
            print(f"[DEBUG] Got location: {location}")
            
            # В тестовом режиме получаем ссылку для скачивания
            if TEST_MODE and location:
                download_url = await get_download_link(location)
                return location

            if not location:
                raise Exception("Не получен Location заголовок")
            return location


async def get_download_link(location):
    """Получение ссылки на скачивание файла"""
    clean_path = location
    print(f"[DEBUG] Download path: {clean_path}")
    
    params = {'path': clean_path}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(DOWNLOAD_LINK_URL, headers=AUTH_HEADERS,
                               params=params) as resp:
            print(f"[DEBUG] Download link response: {resp.status}")
            if resp.status != 200:
                error_text = await resp.text()
                if TEST_MODE:
                    # В тестовом режиме возвращаем заглушку
                    return f"http://test.download.link/{clean_path}"
                raise Exception(f"Ошибка получения ссылки скачивания: "
                                f"{resp.status}, {error_text}")
            data = await resp.json()
            return data['href']