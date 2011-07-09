# -*- coding: utf-8 -*-
"""
Create a Python metadata repository from a Python Package Index.

The implementation is a MESS, because it attempts to clean up
an even bigger mess.
"""
import os
import logging
import argparse
import shutil
from packaging.errors import IrrationalVersionError
from packaging.pypi.simple import Crawler, DEFAULT_SIMPLE_INDEX_URL

from pkgmeta.index2repo.config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def _random_project_sample(projects):
    """ XXX For development testing purposes only...

    Randomly select a sample from ~16000 packages with 4% error
    acceptance, so about 974 packages in the sample size."""
    _sample_size = 974
    count = 0
    new_projects_list = []
    from random import choice
    logger.info("Randomly sampling:")
    # XXX special cases that should be tests =/
    # Insert special case: Yarrow 1.2 Download IO error
    # Insert special case: sake 0.0 Download URL error
    # special_cases = ('sake', 'Yarrow')
    # for p in projects:
    #     if p.name in special_cases:
    #         logger.info("Selecting special case: {0}".format(p.name))
    #         count += 1
    #         new_projects_list.append(p)
    # end special cases
    while count != _sample_size:
        p = choice(projects)
        if p not in new_projects_list:
            logger.info("  Selecting: {0}".format(p.name))
            new_projects_list.append(p)
            count += 1
    return new_projects_list

def _releases_generator_function(crawler, projects, all_releases=False):
    """Yield the project and a list of releases for that project.

    By default, the release list will contain only one value unless
    the all_releases argument is set to True."""
    for project in projects:
        package_name = project.name

        try:
            # XXX Must call get_releases because get_release doesn't support
            #     the force_update argument.
            #     
            releases = crawler.get_releases(package_name, force_update=True)
            if not all_releases and len(releases) > 0:
                release = crawler.get_release(package_name,
                                              prefer_final=True)
                releases = [release]
        except IrrationalVersionError as err:
            logger.error("  Skipping {0} due to irrational version: {1}"\
                         .format(package_name, err))
            continue
        except Exception as err:
            logger.error("  Removing {0} due to an unknown error: {1}"\
                         .format(package_name, err))
            shutil.rmtree(package_dir)
            continue
        yield project, releases

def crawl_index(all_releases=False):
    """Crawl the index for project releases."""
    crawler = Crawler(follow_externals=False)
    projects = crawler.search_projects('')
    projects = _random_project_sample(projects)
    return _releases_generator_function(crawler, projects, all_releases)

def main():
    parser = argparse.ArgumentParser(description="Index to Repository")
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    parser.add_argument('--all-releases',
                        action='store_true', default=False,
                        help="Retrieve all releases not just the "\
                             "designated stable release. (default: False)")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    package_downloads = os.path.join(os.curdir, 'downloads')
    package_downloads = os.path.abspath(package_downloads)
    if not os.path.exists(package_downloads):
        os.mkdir(package_downloads)

    crawl = crawl_index(args.all_releases)

    collected_metadata = []
    for project, release_set in crawl:
        package_name = project.name
        package_dir = os.path.join(package_downloads, package_name)
        if not os.path.exists(package_dir):
            os.mkdir(package_dir)
        logger.debug("Downloading {0} to {1}".format(package_name,
                                                     package_dir))

        for release_info in release_set:
            version = str(release_info.version)
            download_dir = os.path.join(package_dir, version)
            if os.path.exists(download_dir):
                logger.info("  Already have {0} ({1})."\
                            .format(package_name, version))
                continue
            else:
                os.mkdir(download_dir)

            # FIXME It'd be nice if I could say where it was being
            #       downloaded from... and infact I need this information
            #       for the X-PkgMeta-Download value.
            logger.info("  Downloading {0} ({1})...".format(package_name,
                                                       version))
            try:
                download_path = release_info.download(download_dir)
            except IrrationalVersionError as err:
                logger.error("    Unable to download {0} ({1}) because it "
                             "contains an irrational "
                             "version.".format(package_name, version))
            # XXX See http://bugs.python.org/issue12366
            #     - ValueError from sake 0.0.0
            #     - IOError from Yarrow 1.2
            except (ValueError, IOError) as err:
                logger.error("    Problem downloading {0} ({1}): \n{2}"\
                             .format(package_name, version, err))
            # finally:
            #     metadata = find_metadata(unpacked_location)
            #     collected_metadata.append(metadata)
    # Do the metadata conversion

    return 0


run = main

if __name__ == '__main__':
    main()
