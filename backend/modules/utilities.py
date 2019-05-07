import os
from modules.settings import Settings
import datetime
from hashlib import sha256


def check_download_exists(download_filename):
    settings = Settings()
    download_path = settings.path_for_image('download', download_filename)
    download_url = settings.url_for_image('download', download_filename)
    download_exists = os.path.isfile(download_path)
    return download_exists, download_url


def file_extension_from_filename(filename):
    filename, file_extension = os.path.splitext(filename)
    return file_extension


def filename_for_uploaded_file(uploaded_filename):
    file_extension = file_extension_from_filename(uploaded_filename)
    hashable_string = uploaded_filename.encode('utf-8') + str(
        datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')).encode('utf-8')
    filename = sha256(hashable_string).hexdigest() + file_extension
    return filename
