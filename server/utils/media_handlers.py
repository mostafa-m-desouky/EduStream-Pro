import os
import secrets
from PIL import Image
from flask import current_app

DEFAULT_IMAGES = ['male_default.png', 'female_default.png', 'default_course.jpg', 'default.jpg']

def save_picture(form_picture, folder='profile_pics'):

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    picture_path = os.path.join(current_app.root_path, 'static', folder, picture_fn)

    if folder == 'course_thumbnails':
        output_size = (800, 450)
    else:
        output_size = (250, 250)

    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    i.save(picture_path, optimize=True, quality=85)

    return picture_fn

def delete_old_picture(picture_fn, folder='profile_pics'):

    if picture_fn not in DEFAULT_IMAGES:
        picture_path = os.path.join(current_app.root_path, 'static', folder, picture_fn)
        try:
            if os.path.exists(picture_path):
                os.remove(picture_path)
        except Exception as e:
            print(f"Error deleting file: {e}")