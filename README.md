# The dataset

This dataset has been published in ["SZZ in the time of Pull Requests"](https://arxiv.org/abs/2209.03311) and is a collection of 11991 links from bug-introducing and bug-fixing commit sets extracted from Mozilla's Bugzilla (https://bugzilla.mozilla.org) with the use of [bugbug](https://github.com/mozilla/bugbug).

Bug IDs refer to Bugzilla, e.g. 1856572 is https://bugzilla.mozilla.org/show_bug.cgi?id=1856572.
Mercurial hashes refer to the mozilla-central repository, e.g. 3c1db459589a845238abc0359c581fb436a9458f is https://hg.mozilla.org/mozilla-central/rev/3c1db459589a845238abc0359c581fb436a9458f.
Git hashes refer to a clone of the mozilla-central repository using [git-cinnabar](https://github.com/glandium/git-cinnabar): `git clone hg::https://hg.mozilla.org/mozilla-central`.

# Example usage of the dataset

Run the example.py script with Python to see some high-level statistics about the dataset:

```Python
python example.py
```

The output is:

```
Total number of pairs: 20897
Number of pairs with no shared files: 3126
Number of pairs where the bug-fix only contains new lines: 1869
Number of pairs where the bug-introducing only contains removed lines: 998
Number of pairs where the bug-introducing is not linked to any commit: 880
Number of bugs which are not fixed yet and where the cause has been identified: 8906
Deciles for the number of commits associated to bug fixes:
[0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 2.0]
Deciles for the number of commits associated to bug introducing:
[1.0, 1.0, 1.0, 2.0, 2.0, 3.0, 4.0, 6.0, 12.0]
```

# Format

In this repository, you will find the dataset in two alternative formats:

1. A CSV file containing all the information related to each issue
2. A JSON file in a format compatible with [PySZZ](https://github.com/grosa1/pyszz)

In the CSV file, each record represents a link between a bug-introducing and a bug-fixing commit set, and it contains the following columns:

- `FIX_ID`: the ID of the regression bug (bug linked to the bug-fixing commits) on [Bugzilla](https://bugzilla.mozilla.org/)
- `FIX_COMMITS_MERCURIAL`: the list of bug-fixing commit hashes from the original Mozilla [mozilla-central](https://hg.mozilla.org/mozilla-central/) repository hosted in Mercurial
- `FIX_COMMITS_GIT`: the list of bug-fixing commit hashes on the mozilla-central mirror git repository (see https://github.com/glandium/git-cinnabar)
- `BUG_ID`: the ID of the regressor bug (bug linked to the bug-introducing commits) on [Bugzilla](https://bugzilla.mozilla.org/)
- `BUG_COMMITS_MERCURIAL`: the list of bug-introducing commit hashes from the original mozilla-central repository hosted in Mercurial
- `BUG_COMMITS_GIT`: the list of fix-inducing commit hashes on the mozilla-central mirror git repository
- `NO_FILE_SHARED`: a boolean value. `TRUE` if no file is shared between the bug-fixing and bug-introducing commit sets (Extrinsic Bug/Ghost Commits), `FALSE` otherwise.
- `NEW_LINES_ONLY_FIX`: a boolean value. `TRUE` if there are only added lines in the bug-fixing commit-set (Ghost Commits), `FALSE` otherwise.
- `REMOVE_LINES_ONLY_BUG`: a boolean value. `TRUE` if there are only removed lines in the bug-introducing commit-set (Ghost Commits), `FALSE` otherwise.
- `NO_BUG`: a boolean value. `TRUE` if there is no commit linked to the regressor bug (Extrinsic Bug), `FALSE` otherwise.
