import asyncio
from http import HTTPStatus
from io import BytesIO
import pytest

from tests.conftest import generate_png_bytes, TEST_BASE_URL
from tests.yandex_disk_mock_server import (
    COMMON_ASSERT_MSG_FOR_UPLOAD_FILES, intercept_requests
)

FILES_URL = '/files'
EXPECTED_API_CALLS = {
    'get_upload_link',
    'upload',
    'get_download_link'
}


def test_files_upload_page_available(client):
    response = client.get(FILES_URL)
    assert response.status_code == HTTPStatus.OK, (
        'Убедитесь, что GET-запрос к странице загрузки файлов '
        f'(`{FILES_URL}`) возвращает статус {HTTPStatus.OK.value}.'
    )


def test_files_upload_page_has_form(client):
    response = client.get(FILES_URL)
    assert b'form' in response.data, (
        'Убедитесь, что на странице загрузки файлов отображается форма.'
    )


def test_files_upload_page_form_fields(client):
    response = client.get(FILES_URL)
    assert b'type="file"' in response.data, (
        'Убедитесь, что на странице загрузки файлов отображается поле '
        'для выбора файлов (`type="file"`).'
    )
    assert b'type="submit"' in response.data, (
        'Убедитесь, что на странице загрузки файлов отображается кнопка '
        'отправки формы (`type="submit"`).'
    )


@pytest.mark.skip(reason="This test is skipped on local environment")
async def test_upload_files(client, mock_server, monkeypatch):
    pass