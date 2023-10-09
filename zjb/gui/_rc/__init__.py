

import os


def find_resource_file(name, rel=True):
    fname = os.path.join(__file__, '../', name)
    if rel:
        return os.path.relpath(fname)
    else:
        return os.path.abspath(fname)
