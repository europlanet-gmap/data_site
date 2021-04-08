import gpt

def verify_data(filename):
    _ext = filename.split('.')[-1]
    if _ext in ('gpkg','zip'):
        pkg = gpt.load_gpkg(filename)
    elif _ext in ('tif','tiff'):
        pkg = gpt.load_tiff(filename)
    else:
        return False
    return True
