# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import csv
import json
import logging
from os import path

from libmozdata import vcs_map
from tqdm import tqdm

from bugbug import bugzilla, db, repository

logging.basicConfig(level=logging.INFO)

# Path to Mozilla Gecko-Dev git mirror obtained via git-cinnabar. Change this based on your clone location.
# For more info: https://github.com/glandium/git-cinnabar/wiki/Mozilla:-A-git-workflow-for-Gecko-development
REPO_PATH = path.join("path", "to", "mozilla-unified")


def main():
    fix_list = list()  # contains all fixes (Bugzilla commit objects)
    cs_map = dict()  # contains cs_id -> [mercurial_hashes of commits]
    commit_cs_map = dict()  # contains pairs mercurial_hashes -> cs_id
    git_commits = dict()  # contains pairs cs_id -> [git commit]
    json_output = list()  # list of json object to save

    # Downloading Data from Mozilla
    logging.info("Downloading commits database...")
    assert db.download(repository.COMMITS_DB)
    logging.info("Downloading bugs database...")
    assert db.download(bugzilla.BUGS_DB)

    # Commit-Set Map Init
    logging.info("Initializing Commit-Set Map")
    for commit in tqdm(repository.get_commits()):
        if commit["bug_id"]:
            if commit["bug_id"] not in cs_map.keys():
                cs_map[commit["bug_id"]] = list()

            cs_map[commit["bug_id"]].append(commit)
            commit_cs_map[commit["node"]] = commit["bug_id"]

    logging.info(f"Initialization completed. {len(cs_map)} commit-sets found")

    # Fixes List Init
    logging.info("Gathering Fixes...")
    fix_list = [
        bug
        for bug in bugzilla.get_bugs()
        if bug["regressed_by"] and bug["resolution"] == "FIXED"
    ]
    logging.info(f"Gathering completed. {len(fix_list)} fixes found.")

    # Commit Mapping
    logging.info("Mapping Mercurial commit hashes into Git commit hashes...")
    commit_list = [commit for commit in repository.get_commits()]
    mercurial_hashes = [commit["node"] for commit in commit_list]
    git_hashes = [
        git_hash for git_hash in vcs_map.mercurial_to_git(REPO_PATH, mercurial_hashes)
    ]
    for i in tqdm(range(len(git_hashes))):
        git_commits.setdefault(commit_list[i]["bug_id"], []).append(git_hashes[i])

    logging.info("Mapping completed.")

    # Composing the Ground Truth
    logging.info("Composing Ground Truth...")
    index = 0
    with open("regressors_regressions_dataset.csv", "w+") as csv_file:
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
            ]
        )

        # Scanning all fixes
        for fix in tqdm(fix_list):
            fix_id = fix["id"]
            issue_date = fix["creation_time"]

            # Check for existing Fix for the Bug
            if fix_id not in git_commits:
                logging.info(
                    f"There is no commit for FIX {fix_id}."
                    f"Probably it has no associated FIX commit yet, or there is no Mapping."
                )
                continue

            # Retrieving Hashes for Mercurial and Git
            fix_mercurial_hashes = git_commits[fix_id]
            fix_git_hashes = git_commits[fix_id]

            # Retrieving Bugs related to the Fix
            bug_ids = [bug_id for bug_id in fix["regressed_by"]]

            # Retrieving Commits related to the Bug
            bug_mercurial_hashes = list()
            bug_git_hashes = list()
            for bug_id in bug_ids:
                if bug_id in cs_map:
                    bug_mercurial_hashes.extend(cs_map[bug_id])
                    bug_git_hashes.extend(git_commits[bug_id])

            # Creating and Writing the new record for the Dataset
            new_record = [
                fix_id,
                fix_mercurial_hashes,
                fix_git_hashes,
                bug_ids,
                bug_mercurial_hashes,
                bug_git_hashes,
            ]
            writer.writerow(new_record)

            # Creating objects for JSON format
            for fix_hash in fix_git_hashes:
                new_json_item = {
                    "id": index,
                    "repo_name": "path/to/mozilla-unified",
                    "fix_commits_hash": fix_hash,
                    "bug_commits_hash": bug_git_hashes,
                    "best_scenario_issue_date": issue_date,
                }
                json_output.append(new_json_item)

    # Writing Json File
    logging.info("Dataset Created. Saving JSON format...")
    with open("regressors_regressions_dataset.json", "w+") as json_file:
        json.dump(json_output, json_file, indent=4)

    json_file.close()
    logging.info("JSON file created.")


if __name__ == "__main__":
    main()
