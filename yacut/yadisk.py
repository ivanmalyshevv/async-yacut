from urllib.parse import unquote

import aiohttp
from flask import current_app

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'

UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'
CREATE_FOLDER_URL = f'{API_HOST}{API_VERSION}/disk/resources'

FAKE_TOKEN = 'y0_nbfoiu3445tno35_fd09v854bn2_cs0e8hrb4k'


def _get_auth_headers() -> dict:
    token = current_app.config.get('DISK_TOKEN')
    return {'Authorization': f'OAuth {token}'} if token else {}


def _is_test_mode() -> bool:
    token = current_app.config.get('DISK_TOKEN')
    return token == FAKE_TOKEN


async def create_folder(path: str) -> None:
    """Создаёт папку на Яндекс Диске, если её нет."""
    if _is_test_mode():
        return

    headers = _get_auth_headers()
    params = {'path': path}

    async with aiohttp.ClientSession() as session:
        async with session.put(
            CREATE_FOLDER_URL, headers=headers, params=params
        ) as response:
            if response.status == 409:
                pass
            elif response.status not in (200, 201):
                error_text = await response.text()
                raise Exception(
                    f"Ошибка создания папки: {response.status}, {error_text}"
                )


async def get_upload_url(filename: str) -> str:
    """Получает URL для загрузки файла."""
    if _is_test_mode():
        return f"http://localhost:8080/upload/{filename}"

    await create_folder('disk:/YaCut')

    headers = _get_auth_headers()
    params = {
        'path': f'disk:/YaCut/{filename}',
        'overwrite': 'True',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            UPLOAD_URL, headers=headers, params=params
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(
                    f"Ошибка: {response.status}, {error_text}"
                )
            upload_info = await response.json()
            return upload_info['href']


async def upload_file(upload_url: str, file_storage) -> str:
    """Загружает файл по полученному URL."""
    if _is_test_mode():
        return f"/disk/YaCut_Uploads/{file_storage.filename}"

    file_bytes = file_storage.read()

    async with aiohttp.ClientSession() as session:
        async with session.put(upload_url, data=file_bytes) as response:
            if response.status not in (200, 201):
                error_text = await response.text()
                raise Exception(
                    f"Ошибка загрузки: {response.status}, {error_text}"
                )
            location = response.headers.get('Location', '')

    location = unquote(location)
    if location.startswith('/disk'):
        location = location[len('/disk'):]
    return location


async def get_download_url(path_on_disk: str) -> str:
    """Получает ссылку на скачивание файла."""
    if _is_test_mode():
        return f"http://localhost:8080/download{path_on_disk}"

    headers = _get_auth_headers()
    params = {'path': path_on_disk}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            DOWNLOAD_LINK_URL, headers=headers, params=params
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(
                    f"Ошибка: {response.status}, {error_text}"
                )
            download_info = await response.json()
            return download_info['href']