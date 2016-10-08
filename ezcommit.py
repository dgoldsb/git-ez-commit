import hashlib
from git import Repo
import os
import sys
import argparse
import tempfile
from git import Actor

def commit_version(repo, requested_version, commit_msg, index, version_file):
    """
    Commits version to index
    """

    print("Committing: ", requested_version)

    index.add([version_file])
    #repo.git.add(update=True)
    index.commit(commit_msg)

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
    repo = Repo.init(path, bare=False)
    python_scripts = find_python_scripts(path)
    diff = repo.git.diff('HEAD~0', name_only=True)

    for script in python_scripts:
        if script in diff:
            print('Differences found in file ',path+script,', proceeding...')
            # Read the file off the disk
            current = open(path+script, 'r')

            # Fetch the file from the HEAD
            # Template:
            # file_contents = repo.git.show(('HEAD:'+script).format(commit.hexsha, entry.path))
            old = repo.git.show('HEAD:'+script)

            # To test
            """
            print('---')
            print(current.read())
            print('---')
            print(old)
            """
        else:
            print('No differences found in file ',path+script,', skipping...')

    # Compile message
    commit_message = 'Testcommit please ignore.'

    # Commit
    index = repo.index
    requested_version = 'What goes here :('
    version_file = diff
    commit_version(repo, requested_version, "Auto committed", index, version_file)

    # Push
    repo.remotes.origin.push

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
