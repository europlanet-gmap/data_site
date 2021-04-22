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
