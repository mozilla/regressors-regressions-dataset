# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import csv
import json
import logging

from bugbug import bugzilla, db, repository
from libmozdata import vcs_map
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)

# Path to a git clone of the mozilla-central or mozilla-central repository.
# 1. Install git-cinnabar (https://github.com/glandium/git-cinnabar)
# 2. git clone hg::https://hg.mozilla.org/mozilla-central
REPO_PATH = "mozilla-central"


def main():
    # List of regression bugs
    fix_list = []
    # Map from a bug ID to a list of Mercurial hashes of commits that fix the bug
    cs_map = {}
    # Map from a commit to a bug that is fixed by it
    commit_cs_map = {}
    # Map from a bug ID to a list of git hashes of commits that fix the bug
    git_commits = {}

    # Downloading Bugzilla and commits data from Mozilla
    logging.info("Downloading commits database...")
    assert db.download(repository.COMMITS_DB)
    logging.info("Downloading bugs database...")
    assert db.download(bugzilla.BUGS_DB)

    # Retrieve regression bugs
    logging.info("Gathering bug fixes...")
    bug_ids = set()
    fix_list = []
    for bug in bugzilla.get_bugs():
        if bug["regressed_by"]:
            fix_list.append(bug)

            bug_ids.add(bug["id"])
            bug_ids |= set(bug["regressed_by"])
    logging.info(f"Gathering completed. {len(fix_list)} fixes found.")

    # Commit-Set Map Init
    logging.info("Initializing commit-set map")
    for commit in tqdm(repository.get_commits()):
        if commit["bug_id"] is None or commit["bug_id"] not in bug_ids:
            continue

        if commit["bug_id"] not in cs_map:
            cs_map[commit["bug_id"]] = []

        cs_map[commit["bug_id"]].append(commit)
        commit_cs_map[commit["node"]] = commit["bug_id"]

    logging.info(f"Initialization completed. {len(cs_map)} commit-sets found")

    # Commit Mapping
    logging.info("Mapping Mercurial commit hashes to Git commit hashes...")
    mercurial_hashes = [
        commit["node"]
        for commit in repository.get_commits()
        if commit["node"] in commit_cs_map
    ]

    for mercurial_hash, git_hash in zip(
        mercurial_hashes, vcs_map.mercurial_to_git(REPO_PATH, mercurial_hashes)
    ):
        git_commits.setdefault(commit_cs_map[mercurial_hash], []).append(git_hash)

    logging.info("Mapping completed.")

    # Composing the Ground Truth
    logging.info("Generating dataset in CSV format...")
    results = []
    index = 0
    with open("dataset.csv", "w") as csv_file:
        writer = csv.writer(csv_file)

        # Writing Header of CSV file
        writer.writerow(
            [
                "FIX_ID",
                "FIX_COMMITS_MERCURIAL",
                "FIX_COMMITS_GIT",
                "BUG_ID",
                "BUG_COMMITS_MERCURIAL",
                "BUG_COMMITS_GIT",
                "NO_FILE_SHARED",
                "NEW_LINES_ONLY_FIX",
                "REMOVE_LINES_ONLY_BUG",
                "NO_BUG",
            ]
        )

        # Scanning all fixes
        for fix in tqdm(fix_list):
            fix_id = fix["id"]
            issue_date = fix["creation_time"]

            # Check for existing Fix for the Bug
            if fix_id not in git_commits:
                logging.info(
                    f"There is no commit for bug {fix_id}."
                    f"Probably it has no associated fix commit yet, or there is no mapping."
                )
                continue

            # Retrieving Hashes for Mercurial and Git
            fix_mercurial_commits = cs_map[fix_id]
            fix_git_hashes = git_commits[fix_id]

            # Retrieving Bugs related to the Fix
            bug_ids = [bug_id for bug_id in fix["regressed_by"]]

            # Retrieving Commits related to the Bug
            bug_mercurial_commits = []
            bug_git_hashes = []
            for bug_id in bug_ids:
                if bug_id in cs_map:
                    bug_mercurial_commits.extend(cs_map[bug_id])
                    bug_git_hashes.extend(git_commits[bug_id])

            # Creating and Writing the new record for the Dataset
            writer.writerow(
                [
                    fix_id,
                    " ".join(commit["node"] for commit in fix_mercurial_commits),
                    " ".join(fix_git_hashes),
                    " ".join(str(bug_id) for bug_id in bug_ids),
                    " ".join(commit["node"] for commit in bug_mercurial_commits),
                    " ".join(bug_git_hashes),
                    len(
                        set(
                            path
                            for commit in fix_mercurial_commits
                            for path in commit["files"]
                        )
                        & set(
                            path
                            for commit in bug_mercurial_commits
                            for path in commit["files"]
                        )
                    )
                    == 0,
                    sum(
                        commit["source_code_deleted"]
                        + commit["test_deleted"]
                        + commit["other_deleted"]
                        for commit in fix_mercurial_commits
                    )
                    == 0,
                    sum(
                        commit["source_code_added"]
                        + commit["test_added"]
                        + commit["other_added"]
                        for commit in bug_mercurial_commits
                    )
                    == 0,
                    len(bug_mercurial_commits) == 0,
                ]
            )

            # Creating objects for the dataset in the JSON format
            for fix_hash in fix_git_hashes:
                results.append(
                    {
                        "id": index,
                        "repo_name": "mozilla-central",
                        "fix_commits_hash": fix_hash,
                        "bug_commits_hash": bug_git_hashes,
                        "best_scenario_issue_date": issue_date,
                    }
                )

    # Writing json file
    logging.info("Dataset Created. Saving JSON format...")
    with open("dataset.json", "w") as json_file:
        json.dump(results, json_file, indent=4)

    logging.info("JSON file created.")


if __name__ == "__main__":
    main()
