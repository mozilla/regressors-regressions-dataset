This dataset has been published in ["SZZ in the time of Pull Requests"](https://arxiv.org/abs/2209.03311) and is a collection of 5348 issues extracted from Mozilla's Bugzilla (https://bugzilla.mozilla.org) with the use of [bugbug](https://github.com/mozilla/bugbug). In this repository, you will find two shapes of it:
1. A CSV file containing all the information related to each issue
2. A JSON file in a format compatible with [PySZZ](https://github.com/grosa1/pyszz)

In the CSV file, each record represents a link between a bug-introducing and a bug-fixing commit set, and it is composed as follows:

- `FIX_ID`: the ID of the regression bug (bug linked to the bug-fixing commits) on [Bugzilla](https://bugzilla.mozilla.org/)
- `FIX_COMMITS_MERCURIAL`: the list of bug-fixing commit hashes from the original Mozilla [mozilla-central](https://hg.mozilla.org/mozilla-central/) repository hosted in Mercurial
- `FIX_COMMITS_GIT`: the list of bug-fixing commit hashes on the mozilla-central mirror repository hosted on GitHub (https://github.com/mozilla/gecko-dev)
- `BUG_ID`: the ID of the regressor bug (bug linked to the bug-introducing commits) on [Bugzilla](https://bugzilla.mozilla.org/)
- `BUG_COMMITS_MERCURIAL`: the list of bug-introducing commit hashes from the original mozilla-central repository hosted in Mercurial
- `BUG_COMMITS_GIT`: the list of fix-inducing commit hashes on the mozilla-central mirror repository hosted on GitHub
- `NO_FILE_SHARED`: a boolean value. `TRUE` if no file is shared between the bug-fixing and bug-introducing commit sets (Extrinsic Bug/Ghost Commits), `FALSE` otherwise.
- `NEW_LINES_ONLY_FIX`: a boolean value. `TRUE` if there are only added lines in the bug-fixing commit-set (Ghost Commits), `FALSE` otherwise.
- `REMOVE_LINES_ONLY_BUG`: a boolean value. `TRUE` if there are only removed lines in the bug-introducing commit-set (Ghost Commits), `FALSE` otherwise.
- `NO_BUG`: a boolean value. `TRUE` if there is no commit linked to the regressor bug (Extrinsic Bug), `FALSE` otherwise.
- `UNLINKABLE`: a boolean value. `TRUE` if any previous condition is matched, `FALSE` otherwise.