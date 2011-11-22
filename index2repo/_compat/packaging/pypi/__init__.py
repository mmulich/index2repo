#
# Snagged from CPython at revison 0feb5a5dbaeb
# https://bitbucket.org/mirror/cpython/raw/0feb5a5dbaeb/Lib/packaging/pypi/__init__.py
#
"""Low-level and high-level APIs to interact with project indexes."""

__all__ = ['simple',
           'xmlrpc',
           'dist',
           'errors',
           'mirrors']

# CCC --
# BBB by pumazi: Commented out to allow for indirect imports
# from packaging.pypi.dist import ReleaseInfo, ReleasesList, DistInfo
# /CCC
