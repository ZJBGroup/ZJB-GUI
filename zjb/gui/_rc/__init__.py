import os


def find_resource_file(name):
    fname = os.path.join(__file__, "../", name)
    return os.path.abspath(fname)
