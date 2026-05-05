from flask_wtf import FlaskForm
from wtforms import StringField, FileField, MultipleFileField
from wtforms.validators import DataRequired, Length, Optional, URL, Regexp, ValidationError

class MainForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'), URL(message='Введите корректный URL')]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=16, message='Не более 16 символов'),
            Regexp(r'^[a-zA-Z0-9]+$', message='Только латинские буквы и цифры')
        ]
    )

class FileUploadForm(FlaskForm):
    files = MultipleFileField(
        'Файлы для загрузки',
        validators=[DataRequired(message='Выберите хотя бы один файл')]
    )