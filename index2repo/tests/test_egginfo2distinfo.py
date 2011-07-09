# -*- coding: utf-8 -*-
import os
import tempfile
from packaging.metadata import Metadata
from pkgmeta.tests import unittest

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_INFO = os.path.join(HERE, 'test_info')

MOCK_DISTINFO = os.path.join(TEST_INFO, 'mock-0.7.2.dist-info')
MOCK_EGGINFO = os.path.join(TEST_INFO, 'mock-0.7.2.egg-info')
WSGIOAUTH_DISTINFO = os.path.join(TEST_INFO, 'wsgioauth-0.3.dist-info')
WSGIOAUTH_EGGINFO = os.path.join(TEST_INFO, 'wsgioauth-0.3.egg-info')


class EggInfo2DistInfoTestCase(unittest.TestCase):

    def test_pkginfo_conversion(self):
        # Basic metadata version 1.0 and 1.1 to 1.2
        ##expected_metadata = Metadata(os.path.join(MOCK_DISTINFO, 'METADATA'))
        from pkgmeta.index2repo.egginfo2distinfo import egginfo2distinfo

        #: Temporary file location for the output
        expected_distinfo_location = tempfile.mkdtemp('.dist-info',
                                                      'pkgmeta-')

        # Case: mock==0.7.2
        distinfo_dir = egginfo2distinfo(MOCK_EGGINFO,
                                        expected_distinfo_location)
        self.assertEqual(distinfo_dir, expected_distinfo_location)
        self.assertIn('METADATA', os.listdir(distinfo_dir))
        metadata = Metadata(os.path.join(distinfo_dir, 'METADATA'))
        # Ends up metadata version 1.0 because it doesn't have any
        #   PEP 345 markers (e.g. Requires-Dist).
        self.assertEqual(metadata['Metadata-Version'], '1.0')
        missing, warnings = metadata.check(strict=True,
                                           restructuredtext=True)

        # Case: wsgioauth==0.3
        expected_distinfo_location = tempfile.mkdtemp('.dist-info',
                                                      'pkgmeta-')
        distinfo_dir = egginfo2distinfo(WSGIOAUTH_EGGINFO,
                                        expected_distinfo_location)
        self.assertEqual(distinfo_dir, expected_distinfo_location)
        self.assertIn('METADATA', os.listdir(distinfo_dir))
        metadata = Metadata(os.path.join(distinfo_dir, 'METADATA'))
        self.assertEqual(metadata['Metadata-Version'], '1.2')
        missing, warnings = metadata.check(strict=True,
                                           restructuredtext=True)

    def test_unknown_file_logging(self):
        # Add an oddball file to the .egg-info to verify the oddball
        # is logged.
        self.fail()
