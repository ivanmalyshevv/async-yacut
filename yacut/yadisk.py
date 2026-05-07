from urllib.parse import unquote

import aiohttp
from flask import current_app

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'

DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


def _get_auth_headers() -> dict:
    token = current_app.config.get('DISK_TOKEN')
    return {'Authorization': f'OAuth {token}'} if token else {}


async def get_upload_url(filename: str) -> str:
    headers = _get_auth_headers()
    params = {
        'path': f'app:/{filename}',
        'overwrite': 'True',
    }
    upload_url_endpoint = f'{API_HOST}{API_VERSION}/disk/resources/upload'

    async with aiohttp.ClientSession() as session:
        async with session.get(
            upload_url_endpoint,
            headers=headers,
            params=params,
        ) as response:
            upload_info = await response.json()
            return upload_info['href']


async def upload_file(upload_url: str, file_storage) -> str:
    file_bytes = file_storage.read()

    async with aiohttp.ClientSession() as session:
        async with session.put(upload_url, data=file_bytes) as response:
            location = response.headers.get('Location', '')
    
    location = unquote(location)
    if location.startswith('/disk'):
        location = location[len('/disk'):]
    return location


async def get_download_url(path_on_disk: str) -> str:
    headers = _get_auth_headers()
    params = {'path': path_on_disk}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            DOWNLOAD_LINK_URL,
            headers=headers,
            params=params,
        ) as response:
            download_info = await response.json()
            return download_info['href']