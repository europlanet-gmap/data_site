import os
from flask import current_app
from werkzeug.utils import secure_filename


class Tempdir(str):
    """
    Create and holds the path for a tempfile, and deletes it when goes out of scope.
    """
    def __new__(cls, dir=None):
        from tempfile import mkdtemp
        _dir = mkdtemp(dir=dir)
        return super().__new__(cls, _dir)
    def __del__(self):
        from shutil import rmtree
        rmtree(str(self))


def mkdtemp():
    """
    Return path to temporary dir
    """
    from tempfile import mkdtemp
    tmpdir = Tempdir(dir = current_app.config['UPLOAD_FOLDER'])
    os.makedirs(tmpdir, exist_ok=True)
    return tmpdir


def save_file(file_form, dir):
    """
    Return filename uploaded from a WTForms UploadField
    """
    filename = secure_filename(file_form.filename)
    filepath = os.path.join(dir, filename)
    file_form.save(filepath)
    return filename
