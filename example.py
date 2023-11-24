# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import csv
import statistics
import sys

num = 0
nums_commits_fix = []
nums_commits_introducing = []
num_no_file_shared = 0
num_new_lines_only_fix = 0
num_remove_lines_only_bug = 0
num_no_bug = 0
num_no_fix_yet = 0

csv.field_size_limit(sys.maxsize)

with open("dataset.csv", "r") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        num += 1

        num_commits_fix = (
            row["FIX_COMMITS_MERCURIAL"].count(" ") + 1
            if row["FIX_COMMITS_MERCURIAL"] != ""
            else 0
        )
        if num_commits_fix == 0:
            num_no_fix_yet += 1
        nums_commits_fix.append(num_commits_fix)

        nums_commits_introducing.append(row["BUG_COMMITS_MERCURIAL"].count(" ") + 1)

        if row["NO_FILE_SHARED"] == "True":
            num_no_file_shared += 1

        if row["NEW_LINES_ONLY_FIX"] == "True":
            num_new_lines_only_fix += 1

        if row["REMOVE_LINES_ONLY_BUG"] == "True":
            num_remove_lines_only_bug += 1

        if row["NO_BUG"] == "True":
            num_no_bug += 1


print(f"Total number of pairs: {num}")
print(f"Total number of pairs where both bug-introducing and bug-fix are known: {num - num_no_fix_yet}")
print(f"Number of pairs with no shared files: {num_no_file_shared}")
print(
    f"Number of pairs where the bug-fix only contains new lines: {num_new_lines_only_fix}"
)
print(
    f"Number of pairs where the bug-introducing only contains removed lines: {num_remove_lines_only_bug}"
)
print(
    f"Number of pairs where the bug-introducing is not linked to any commit: {num_no_bug}"
)
print(
    f"Number of bugs which are not fixed yet and where the cause has been identified: {num_no_fix_yet}"
)
print("Deciles for the number of commits associated to bug fixes:")
print(statistics.quantiles(nums_commits_fix, n=10, method="inclusive"))
print("Deciles for the number of commits associated to bug introducing:")
print(statistics.quantiles(nums_commits_introducing, n=10, method="inclusive"))
