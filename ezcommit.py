from git import Repo
import os
import sys
import argparse
import tempfile

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
    repo = Repo.init(path, bare=True)
    assert repo.bare
    python_scripts = find_python_scripts(path)

    for script in python_scripts:
        # Read the file off the disk
        old = open(script, 'r')

        # Fetch the file from the HEAD
        #file_contents = repo.git.show(('HEAD:'+script).format(commit.hexsha, entry.path))
        current = repo.git.show('HEAD:'+script)

        #Everything
        print(current)
        print(old)

def main(argv):
    """
    Uses an argument parser to get the repository location and initiate the
    EZcommit procedure
    """
    # Get the command line arguments
    parser = argparse.ArgumentParser(description='Provide the parameters for EZcommit.')
    parser.add_argument('-r','--repo', type=str, default=10, help='The number of timesteps.')
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
    print(content_bunny)

    # EZgit initiation
    generate_commit(repo_path)

if __name__ == "__main__":
    main(sys.argv)
