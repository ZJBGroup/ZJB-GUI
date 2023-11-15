import os


def find_resource_file(name, abs=True):
    fname = os.path.join(__file__, "../", name)
    if abs:
        return os.path.abspath(fname)
    else:
        return os.path.relpath(fname)
