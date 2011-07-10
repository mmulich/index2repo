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

XXX_sample_size = None


# ################# #
#   Functionality   #
# ################# #

def _random_project_sample(projects):
    """ XXX For development testing purposes only...

    Randomly select a sample from ~16000 packages with 4% error
    acceptance, so about 974 packages in the sample size."""
    global XXX_sample_size
    _sample_size = XXX_sample_size or 974
    count = 0
    new_projects_list = []
    from random import choice
    # XXX special cases that should be tests =/
    # Insert special case: redsolutioncms.django-chunks IrrationalVersionError
    # Insert special case: Yarrow 1.2 Download IO error
    # Insert special case: sake 0.0 Download URL error
    # special_cases = ('sake', 'Yarrow',)
    # for p in projects:
    #     if p.name in special_cases:
    #         count += 1
    #         new_projects_list.append(p)
    # end special cases
    while count != _sample_size:
        p = choice(projects)
        if p not in new_projects_list:
            new_projects_list.append(p)
            count += 1
    return new_projects_list

def _releases_generator_function(projects, prefer_final=True):
    """Yield the project and a list of releases for that project.

    By default, the release list will contain only one value unless
    the prefer_final argument is set to False."""
    while projects:
        project = projects.pop()
        try:
            # XXX There is an issue with the Crawler API that forces
            #     us to use the index rather than the resulting project.
            #     See also http://bugs.python.org/issue12526
            project = project._index.get_releases(project.name,
                                                  prefer_final=prefer_final,
                                                  force_update=True)
        except Exception as err:
            # FIXME I don't like this, but lack a better solution at
            #       the moment.
            setattr(project, 'failure', err)
        yield project

def crawl_index(all_releases=False):
    """Crawl the index for project releases."""
    crawler = Crawler(follow_externals=False)
    projects = crawler.search_projects('')
    projects = _random_project_sample(projects)
    return _releases_generator_function(projects, not all_releases)

def download_project_releases(project, release_set,
                              download_directory="downloads"):
    """Download the the project's releases."""
    # TODO What kind of release should we download? source or bin?
    pass


# ################ #
#   Main program   #
# ################ #

def main():
    parser = argparse.ArgumentParser(description="Index to Repository")
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    parser.add_argument('--all-releases',
                        action='store_true', default=False,
                        help="Retrieve all releases not just the "\
                             "designated stable release. (default: False)")
    # XXX Used in manual testing...
    parser.add_argument('--xxx-sample-size', type=int, nargs=1)
    args = parser.parse_args()

    # XXX values
    if args.xxx_sample_size:
        global XXX_sample_size
        XXX_sample_size = args.xxx_sample_size[0]

    logger = logging.getLogger(LOGGER_NAME)
    if args.debug:
        logger.setLevel(logging.DEBUG)

    package_downloads = os.path.join(os.curdir, 'downloads')
    package_downloads = os.path.abspath(package_downloads)
    if not os.path.exists(package_downloads):
        os.mkdir(package_downloads)

    crawl = crawl_index(args.all_releases)

    collected_metadata = []
    for project in crawl:
        package_name = project.name
        if len(project) == 0:
            logger.info("Skipping {0} because it has no releases."\
                        .format(package_name))
            continue
        package_dir = os.path.join(package_downloads, package_name)
        if not os.path.exists(package_dir):
            os.mkdir(package_dir)
        logger.debug("Downloading {0} to {1}".format(package_name,
                                                     package_dir))

        for release_info in project:
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
