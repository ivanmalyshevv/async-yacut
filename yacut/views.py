import asyncio
from flask import Blueprint, render_template, redirect, url_for, flash, request
from yacut.forms import MainForm, FileUploadForm
from yacut.models import URLMap
from yacut.yadisk import get_upload_url, upload_file, get_download_url
from yacut import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    form = MainForm()
    short_url = None
    
    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = form.custom_id.data
        
        if not custom_id or custom_id.strip() == '':
            short_id = URLMap.get_unique_short_id()
        else:
            if custom_id == 'files':
                flash('Предложенный вариант короткой ссылки уже существует.', 'danger')
                return render_template('index.html', form=form)
            
            if URLMap.query.filter_by(short=custom_id).first():
                flash('Предложенный вариант короткой ссылки уже существует.', 'danger')
                return render_template('index.html', form=form)
            
            short_id = custom_id
        
        url_map = URLMap(original=original, short=short_id)
        db.session.add(url_map)
        db.session.commit()
        
        short_url = url_for('main.follow_short', short=short_id, _external=True)
        return render_template('index.html', form=form, short_url=short_url)
    
    return render_template('index.html', form=form, short_url=short_url)


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
        
        if uploaded_files and uploaded_files[0].filename:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = []
            
            for file_storage in uploaded_files:
                if file_storage and file_storage.filename:
                    filename = file_storage.filename
                    tasks.append(process_file(file_storage, filename))
            
            try:
                results = loop.run_until_complete(asyncio.gather(*tasks))
                for filename, short_id, download_url in results:
                    files_links.append({
                        'filename': filename,
                        'short_url': url_for('main.follow_short', short=short_id, _external=True),
                        'download_url': download_url
                    })
            except Exception as e:
                flash(f'Ошибка при загрузке файлов: {str(e)}', 'danger')
            finally:
                loop.close()
    
    return render_template('files.html', form=form, files_links=files_links)


async def process_file(file_storage, filename):
    short_id = URLMap.get_unique_short_id()
    
    upload_url = await get_upload_url(filename)
    path_on_disk = await upload_file(upload_url, file_storage)
    download_url = await get_download_url(path_on_disk)
    
    url_map = URLMap(original=download_url, short=short_id)
    db.session.add(url_map)
    db.session.commit()
    
    return filename, short_id, download_url