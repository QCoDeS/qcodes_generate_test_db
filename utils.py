# General utilities for the database generation and loading scheme
from typing import Dict, Tuple, Union
import importlib
from contextlib import contextmanager
import os

from git import Repo

# A brief overview of what each version introduces:
#
# Inception of version 0: the original table schema, runs, experiments,
# layouts, dependencies, result-tables
#
# Upgrade from 0 to 1: a GUID column is added to the runs table
#
# Upgrade from 1 to 2: indices are added to runs; GUID and exp_id
#
# Upgrade from 2 to 3: run_description column is added to the runs table
#
# Upgrade from 3 to 4: fixes two bugs in the inferred annotation which
#   come from the previous "upgrade from 2 to 3"; this upgrade basically
#   re-does the "upgrade from 2 to 3" but without those bugs.
#
# Fix for version 4: a bug was introduced that accidentally wrote an
#   invalid runs description. The bug is reproduced by version 4a.
#   The commit of version 4 does not have the bug.
#
# Upgrade from 4 to 5: snapshot column is made always present
#   in the runs table
#
# Upgrade from 5 to 6: a top-level 'version' field is made present in the
#   runs_description JSON string
#
#
# The version '4a' hash represents a merge commit that accidentally broke the
# way run_descriptions were written. Since a fix was quickly implemented, we
# do not promote this to a schema upgrade, but leave it as a fix function.
# We do, however, still need a DB with the bug in it to test the fix.

# NOTE that each hash is supposed to be representing a commit JUST before the
# "next" version is being introduced.
#

GIT_HASHES: Dict[Union[int, str], str] = {
    0: '78d42620fc245a975b5a615ed5e33061baac7846',
    1: '056d59627e22fa3ca7aad4c265e9897c343f79cf',
    2: '5202255924542dad6841dfe3d941a7f80c43956c',
    3: '17436006caceaeb42ea66e5cbaca40bb4c54306a',
    '4a': '6b8f4d1940215a8cefc5f4c399c6aaaeee082d54',
    4: '57ad8711d158f68ecf101006bb8f2072aee157ab',
    5: '660a5534d83f245d772f600839ae3833dcfc8e09',
    6: '670004b06d6af27d7d2286ff65fede64947893a2'}

__initpath = os.path.realpath(importlib.util.find_spec('qcodes').origin)
gitrepopath = os.sep.join(__initpath.split(os.path.sep)[:-2])

repo = Repo(gitrepopath)

fixturepath = os.path.join(gitrepopath, 'qcodes', 'tests', 'dataset',
                           'fixtures', 'db_files')


@contextmanager
def leave_untouched(repo):
    """
    Leave a git repository untouched by whatever fiddling around we need to do
    We support both the case of the repo being initially in a detached head
    state (relevant for Travis) and the -hopefully- normal case for users of
    being at the tip of a branch
    """

    if repo.is_dirty():
        raise ValueError('Git repository is dirty. Can not proceed.')

    was_detached = repo.head.is_detached

    if not was_detached:
        current_branch = repo.active_branch
    current_commit = repo.head.commit

    try:
        yield

    finally:
        repo.git.reset('--hard', current_commit)
        if not was_detached:
            repo.git.checkout(current_branch)


def checkout_to_old_version_and_run_generators(version: Union[int, str],
                                               gens: Tuple) -> None:
    """
    Check out the repo to an older version and run the generating functions
    supplied.
    """

    with leave_untouched(repo):

        repo.git.checkout(GIT_HASHES[version])

        # If QCoDeS is not installed in editable mode, it makes no difference
        # to do our git magic, since the import will be from site-packages in
        # the environment folder, and not from the git-managed folder
        import qcodes
        qcpath = os.sep.join(qcodes.__file__.split(os.sep)[:-2])

        # Windows and paths... There can be random un-capitalizations
        if qcpath.lower() != gitrepopath.lower():
            raise ValueError('QCoDeS does not seem to be installed in editable'
                             ' mode, can not proceed. To use this script, '
                             'uninstall QCoDeS and reinstall it with pip '
                             'install -e <path-to-qcodes-folder>')
        for generator in gens:
            generator()
