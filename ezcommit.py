from code_difference import generate_differences
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

    # For the summary
    root_nodes = []
    count_files_altered = 0
    count_files_added = 0
    count_files_removed = 0

    # Get the index
    index = repo.index


    for script in python_scripts:
        print("script ",script)
        if script in diff:
            print('Differences found in file ',os.path.join(path,script),', proceeding...')
            # Read the file off the disk
            current = open(os.path.join(path,script), 'r')
            # Fetch the file from the HEAD
            old = repo.git.show('HEAD:'+script)

            # Add new element to the commit message
            root_node = generate_differences(current.read(), old, script)
            root_nodes.append([script, root_node])

            # Update in index
            index.add([script])
            count_files_altered += 1

        elif script in untracked:
            print('New file ',os.path.join(path,script),', adding to repo...')
            # Read the file off the disk
            current = open(os.path.join(path,script), 'r')
            # Head is empty
            old = ''

            # Add new element to the commit message
            root_node = generate_differences(current.read(), old, script)
            root_nodes.append([script, root_node])

            # Add to the index
            index.add([script])
            count_files_added += 1

        elif script in deleted:
            print('Deleted file ',os.path.join(path,script),', removing from repo...')
            # File on disk is empty
            current = ''
            # Fetch the file from the HEAD
            old = repo.git.show('HEAD:'+script)

            # Add new element to the commit message
            root_node = generate_differences(current, old, script)
            root_nodes.append([script, root_node])

            index.remove(os.path.join(repo.working_tree_dir, script))
            count_files_removed += 1

        else:
            print('No differences found in file ',os.path.join(path,script),', skipping...')

    # Compile message
    total_additions = 0
    total_alters = 0
    total_deletions = 0
    a = str(count_files_added)
    b = str(count_files_altered)
    c = str(count_files_removed)
    commit_message = '[Bleep bloop automatic]\n'
    commit_message = commit_message+a+' files added, '+b+' files altered, '+c+' files removed.\n'
    d = str(total_additions)
    e = str(total_alters)
    f = str(total_deletions)
    commit_message = commit_message+'In total there are '+d+' additions, '+e+' alterations, '+f+' deletions.\n\n'
    for script in python_scripts:
        if script in diff or script in untracked:
            commit_message = commit_message+script+': '+'changes\n'

    print(commit_message)

    '''
    # Commit
    print('Committing with message:')
    print(commit_message)
    assert index.commit(commit_message).type == 'commit'
    repo.active_branch.commit = repo.commit('HEAD~1')
    author = Actor("Robot", "dgoldsb@live.nl")
    committer = Actor("Robot", "dgoldsb@live.nl")
    # commit by commit message and author and committer
    index.commit(commit_message, author=author, committer=committer)

    # Push
    repo.git.push()
    '''

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
