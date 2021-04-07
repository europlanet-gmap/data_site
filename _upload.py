# from werkzeug.utils import secure_filename

def do_upload(files):
    f = files['the_file']
    f.save('/var/www/uploads/uploaded_file.txt)
    # f.save('/var/www/uploads/' + secure_filename(f.filename))
