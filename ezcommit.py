import hashlib
from git import Repo
import os
import sys
import argparse
import tempfile
from git import Actor
import os

def find_python_scripts(path):
    """
    Find all python script names in a directory
    :param path: path to the directory
    """
    python_scripts = []
    for file in os.listdir(path):
        if file.endswith(".py"):
            python_scripts.append(file)

    return python_scripts

def generate_commit(path):
    """
    Generates an automatic commit message by comparing the current state
    versus the head of the local branch
    :param path: path the repository for which to generate a commit message
    """
    repo = Repo.init(path)
    #assert not repo.bare
    python_scripts = find_python_scripts(path)
    diff = repo.git.diff('HEAD~0', name_only=True)
    untracked = repo.untracked_files
    deleted = []

    # Get the index
    index = repo.index

    for script in deleted:
        index.remove(os.path.join(repo.working_tree_dir, script))

    print(python_scripts)
    for script in python_scripts:
        print("script ",script)
        if script in diff:
            print('Differences found in file ',path+script,', proceeding...')
            # Read the file off the disk
            current = open(path+script, 'r')

            # Fetch the file from the HEAD
            old = repo.git.show('HEAD:'+script)

            # Add new element to the commit message

            # Update in index
            index.add([script])
        elif script in untracked:
            print('New file ',path+script,', adding to repo...')
            # Read the file off the disk
            current = open(path+script, 'r')

            old = ['']

            # Add new element to the commit message

            # Add to the index
            index.add([script])
        else:
            print('No differences found in file ',path+script,', skipping...')

    # Compile message
    commit_message = 'Bleep bloop automatic'

    # Commit
    assert index.commit(commit_message).type == 'commit'
    repo.active_branch.commit = repo.commit('HEAD~1')
    author = Actor("Robot", "dgoldsb@live.nl")
    committer = Actor("Robot", "dgoldsb@live.nl")
    # commit by commit message and author and committer
    index.commit(commit_message, author=author, committer=committer)

    # Push
    repo.push()
    # repo.remotes.origin.push

def main(argv):
    """
    Uses an argument parser to get the repository location and initiate the
    EZcommit procedure
    """
    # Get the command line arguments
    parser = argparse.ArgumentParser(description='Provide the parameters for EZcommit.')
    parser.add_argument('-r','--repo', type=str, help='The repository path.')
    parser.add_argument('-b','--bunny', action='store_true', default=False, help='All hail.')
    args = parser.parse_args()
    repo_path = args.repo

    content_bunny = """

           ,.   ,.
           \.\ /,/
            Y Y f
            |. .|
           ("_, l
            ,- , \\
           (_)(_) Y,.
            _j _j |,'  ALL HAIL CONTENT BUNNY
           (_,(__,'
    """
    if args.bunny:
        print(content_bunny)

    # EZgit initiation
    generate_commit(repo_path)

if __name__ == "__main__":
    main(sys.argv)
    # TESTTTT
