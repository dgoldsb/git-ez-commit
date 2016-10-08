from code_difference import generate_differences
import hashlib
from git import Repo
import os
import sys
import argparse
import tempfile
from git import Actor
import time
import numpy as np
import praw
import random

def breadthfirst_important_features(root_node, max_length):
    node = root_node[1]
    script = root_node[0]

    # Add the root node
    important_nodes = [node]

    while len(important_nodes) < max_length and len(important_nodes) is not 0:
        # Remove the first node
        first_node = important_nodes.pop(0)
        children = first_node.children
        while len(important_nodes) < max_length and len(children) is not 0:
            important_nodes.append(children.pop(0))

    # Build important_feats
    important_feats = []
    for item in important_nodes:
        important_feats.append([script, item.value.type, item.value.current_ast_node])

    return important_feats

def depthfirst_overview(adds, dels, alters, node):
    if node.value is not None:
        if node.value.type == 1:
            adds = adds + 1
        elif node.value.type == 2:
            dels = dels + 1
        else:
            alters = alters + 1

    for child in node.children:
        adds, alters, dels = depthfirst_overview(adds, dels, alters, child)

    return adds, alters, dels

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

def generate_commit(path, feat_count, submissions, debug):
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
    z = 1

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

    # Scan through all rootnodes to count totals
    total_adds = 0
    total_alters = 0
    total_dels = 0
    for root_node in root_nodes:
        total_adds, total_dels, total_alters = depthfirst_overview(total_adds, total_dels, total_alters, root_node[1])

    # Find the important things per file
    # Create an overarching list
    all_important_feats = []
    for root_node in root_nodes:
        # Create the important features for one script
        important_feats = breadthfirst_important_features(root_node, feat_count)
        all_important_feats.append(important_feats)

    # Compile message
    a = str(count_files_added)
    b = str(count_files_altered)
    c = str(count_files_removed)
    commit_message = '[Bleep bloop automatic]\n'
    commit_message = commit_message+a+' files added, '+b+' files altered, '+c+' files removed.\n'
    d = str(total_adds)
    e = str(total_alters)
    f = str(total_dels)
    commit_message = commit_message+'In total there are '+d+' additions, '+e+' alterations, '+f+' deletions.\n\n'
    for script in python_scripts:
        if script in diff or script in untracked:
            # Write out the changes for his one
            script_features = [t for t in all_important_feats if (t[0] is script)]
            changes = '\n- '
            for i in range(0, feat_count):
                if len(script_features) > 0:
                    script_feature = script_features.pop(0)
                    changes = changes+'- '
                    changes = changes+str(script_feature[1])+' '+str(script_feature[2])

            # Build the message
            commit_message = commit_message+script+': '+changes+'\n'

    commit_message = commit_message +'\nShowerthought of the day:\n'
    commit_message = commit_message +random.choice(submissions)
    print(commit_message)

    if not debug:
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

def main(argv):
    """
    Uses an argument parser to get the repository location and initiate the
    EZcommit procedure
    """
    # Get the command line arguments
    parser = argparse.ArgumentParser(description='Provide the parameters for EZcommit.')
    parser.add_argument('-r','--repo', type=str, help='The repository path.')
    parser.add_argument('-f','--features', type=int, default=4, help='The number of changes listed per file.')
    parser.add_argument('-b','--bunny', action='store_true', default=False, help='All hail.')
    parser.add_argument('-d','--debug', action='store_true', default=False, help='All hail.')
    args = parser.parse_args()
    repo_path = args.repo
    feat_count = args.features

    r = praw.Reddit(user_agent="ezcommitter")
    submissions = r.get_subreddit('showerthoughts').get_top(limit=50)
    titles = []
    for submission in submissions:
        titles.append(submission.title)

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
    generate_commit(repo_path, feat_count, titles, args.debug)

    """
    print('Transferring virus')
    for i in range(0,20):
        print('=', end="")
        sys.stdout.flush()
        time.sleep(abs(np.random.normal(0.5, 0.3)))
    print('')
    """

if __name__ == "__main__":
    main(sys.argv)
