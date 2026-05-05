import asyncio
from flask import Blueprint, render_template, redirect, url_for, flash, request
from yacut.forms import MainForm, FileUploadForm
from yacut.models import URLMap
from yacut.utils import get_unique_short_id
from yacut import db
from yacut.yadisk import upload_file_to_disk, get_download_link

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    form = MainForm()
    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = form.custom_id.data

        if not custom_id or custom_id.strip() == '':
            custom_id = get_unique_short_id()

        if custom_id == 'files':
            flash('Предложенный вариант короткой ссылки уже существует.',
                  'danger')
            return render_template('index.html', form=form)

        if URLMap.query.filter_by(short=custom_id).first():
            flash('Предложенный вариант короткой ссылки уже существует.',
                  'danger')
            return render_template('index.html', form=form)

        url_map = URLMap(original=original, short=custom_id)
        db.session.add(url_map)
        db.session.commit()

        short_url = url_for('main.follow_short', short=custom_id,
                            _external=True)
        return render_template('index.html', form=form, short_url=short_url)

    return render_template('index.html', form=form)


@main_bp.route('/<string:short>')
def follow_short(short):
    url_map = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map.original)


@main_bp.route('/files', methods=['GET', 'POST'])
def files():
    form = FileUploadForm()
    files_links = []

    if form.validate_on_submit():
        uploaded_files = request.files.getlist('files')
        print(f"[DEBUG] Received {len(uploaded_files)} files")

        if uploaded_files and uploaded_files[0].filename:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = []

            for file_storage in uploaded_files:
                if file_storage and file_storage.filename:
                    filename = file_storage.filename
                    print(f"[DEBUG] Processing file: {filename}")
                    tasks.append(process_file(file_storage, filename))

            try:
                results = loop.run_until_complete(asyncio.gather(*tasks))
                for filename, short_id, disk_url in results:
                    files_links.append({
                        'filename': filename,
                        'short_url': url_for('main.download_file',
                                             short_id=short_id,
                                             _external=True),
                        'download_url': disk_url
                    })
                    print(f"[DEBUG] Successfully processed: "
                          f"{filename} -> {short_id}")
            except Exception as e:
                flash(f'Ошибка при загрузке файлов: {str(e)}', 'danger')
                print(f"[DEBUG] Error: {e}")
            finally:
                loop.close()
        else:
            flash('Выберите файлы для загрузки', 'danger')

    return render_template('files.html', form=form, files_links=files_links)


async def process_file(file_storage, filename):
    """Обработка одного файла"""
    short_id = get_unique_short_id()
    print(f"[DEBUG] Generated short_id: {short_id} for {filename}")

    location = await upload_file_to_disk(file_storage, filename)
    print(f"[DEBUG] File uploaded, location: {location}")

    download_url = await get_download_link(location)
    print(f"[DEBUG] Got download link: {download_url[:100] if download_url else 'None'}...")

    url_map = URLMap(original=download_url, short=short_id)
    db.session.add(url_map)
    db.session.commit()

    return filename, short_id, download_url


@main_bp.route('/download/<short_id>')
def download_file(short_id):
    """Скачивание файла по короткой ссылке"""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)