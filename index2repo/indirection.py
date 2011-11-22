# -*- coding: utf-8 -*-
"""\
A module used to give direction for backwards and forwards compatiblity.
"""
import sys
try:
    import packaging.pypi
except ImportError:
    # This indirection contains forwards compatibility for select
    # parts of packaging.
    from index2repo._compat.packaging import pypi
    sys.modules['packaging.pypi'] = pypi
