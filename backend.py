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

def compose_package(metadata, files, files_path):
    import os
    report = ""
    try:
        pkg = gpt.GPkg(meta=metadata)
        if files:
            for filename in files:
                _ext = filename.split('.')[-1]
                if _ext in ('gpkg','zip'):
                    pkg.load_gpkg(os.path.join(files_path,filename))
                elif _ext in ('tif','tiff'):
                    pkg.load_tiff(os.path.join(files_path,filename))
                else:
                    continue
        report = str(pkg)
    except Exception as err:
        # report = f"Something went wrong: {str(err)}"
        raise err
    return report
