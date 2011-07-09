# -*- coding: utf-8 -*-
"""Conversion tool for taking metadata from an egg-info format
to the dist-info format.
"""
import os
import sys
import shutil
from packaging.metadata import Metadata, _345_FIELDS, _345_MARKERS
from pkgmeta.utils import Registry

PKGINFO = 'PKG-INFO'
METADATA = 'METADATA'
egginfo_handlers = Registry()


def _convert(egginfo_dir, distinfo_dir=None, handlers=egginfo_handlers):
    """Converts an .egg-info directory structure to a .dist-info structure.
    """
    pkginfo = os.path.join(egginfo_dir, PKGINFO)
    metadata = Metadata(pkginfo)
    #: Define a .dist-info directory location if one wasn't given
    if distinfo_dir is None:
        # Name the directory based on the metadata and PEP 376 naming:
        # http://www.python.org/dev/peps/pep-0376/#one-dist-info-directory-per-installed-distribution
        container = os.path.abspath(egginfo_dir).split(os.sep)[:-1]
        container = os.path.join(*container)
        dirname = "{0}-{1}.dist-info"\
                  .format(metadata['Name'], metadata['Version'])
        distinfo_dir = os.path.join(container, dirname)
    #: Create the .dist-info directory if it doesn't exits
    if not os.path.exists(distinfo_dir):
        os.makedirs(distinfo_dir)
    distinfo_metadata = os.path.join(distinfo_dir, METADATA)
    shutil.copy2(pkginfo, distinfo_metadata)
    #: Pave over the exist metadata variable and use the .dist-info one
    metadata = Metadata(distinfo_metadata)

    fields, version = up_convert(metadata._fields)
    #: Update the fileds and metadata version
    metadata.update(fields)

    if not isinstance(handlers, Registry):
        raise TypeError("Expected a Registry objects recieved a {0}"\
                        .format(type(handlers)))
    handlers.init_handlers(metadata, egginfo_dir)

    for name in handlers:
        handlers[name]()

    metadata.write(distinfo_metadata)
    return distinfo_dir


def up_convert(fields):
    updated_fields = {}
    for field in fields.keys():
        if field not in _345_FIELDS and field not in _345_MARKERS:
            raise NotImplementedError('Oops?')
    # XXX Hard-coding the metadata version for now?
    return updated_fields, '1.2'


class BaseEggInfoHandler:

    def __init__(self, metadata, egginfo_dir):
        self.metadata = metadata
        self.egginfo = egginfo_dir

    def __call__(self):
        return self.run()

class RequiresTxt(BaseEggInfoHandler):

    name = 'requires.txt'

    def run(self):
        requires_txt = os.path.join(self.egginfo, 'requires.txt')
        if not os.path.exists(requires_txt):
            #: Doesn't exist, so drop out...
            return
        reqs = []
        with open(requires_txt, 'r') as f:
            for req_line in f.readlines():
                req_line = req_line.strip()
                if req_line.startswith('['):
                    # FIXME Break out for now, but we'd like to provide
                    #       support to requirement extras in some capacity.
                    break
                elif req_line:
                    reqs.append(req_line)
        self.metadata.set('Requires-Dist', reqs)

egginfo_handlers.add(RequiresTxt)


def egginfo2distinfo(egginfo_dir, distinfo_dir=None):
    """Converts an .egg-info metadata format to .dist-info or
    PEP 345 format. Returns the location of the newly created .dist-info
    directory."""
    if not os.path.exists(os.path.join(egginfo_dir, PKGINFO)):
        raise ValueError("Supplied directory is not valid egg-info")
    distinfo = _convert(egginfo_dir, distinfo_dir,
                        handlers=egginfo_handlers)
    return distinfo


def main():
    pass


if __name__ == '__main__':
    main()
