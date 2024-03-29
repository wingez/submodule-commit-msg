# List Submodule Changes Commit Hook

A Git-hook which automagically creates a summary of changes in submodules, and inserts it into your commit message.

Let's say you make some new commits in submodule1 & submodule2. When you then commit those modules in the main repo,
your commit msg will look like this

```
Main repo commit

Submodule changes:
module1:
    Another commit
    New commit 10
    New commit 9
    New commit 8
    New commit 7
    New commit 6
    New commit 5
    New commit 4
    New commit 3
    New commit 2
    New commit 1
    ... +3 more

module2:
    A Single new commit

End of submodule changes:

```

## Install for a single repository

Download `prepare-commit-msg` and place it in your repo's hooks folder `.git/hooks/prepare-commit-msg`
Then make it executable: `chmod +x .git/hooks/prepare-commit-msg`

Or you can run the following from the root folder in your repo:

`curl -O --output-dir .git/hooks/ https://raw.githubusercontent.com/wingez/submodule-commit-msg/main/prepare-commit-msg && chmod +x .git/hooks/prepare-commit-msg`

## Install for all repositories

Download `prepare-commit-msg` to any folder. For example `~/githooks/`
Then make it executable: `chmod +x ~/githooks/*`

Then execute the following to make git looks for hooks in that folder. Note that all local hooks in repositories will no
longer work. All hooks need to be in this folder. `git config --global core.hooksPath ~/githooks/`

## Configuration

The hook can be configured to by setting the following settings in `git config`

| Key                                             | Default | Description                                                       |
|-------------------------------------------------|---------|-------------------------------------------------------------------|
| `hooks.submodule-commit-msg.hash-length`        | 8       | Include the first n letters of each submodule commit hash         |
| `hooks.submodule-commit-msg.max-commits-listed` | 12      | Max amount of commits listed per submodule before truncating list |
| `hooks.submodule-commit-msg.enabled`            | true    | Set to false to not modify the commit message at all              |
| `hooks.submodule-commit-msg.debug`              |         | Set to give more detailed error-information                       |

Example: `git config --global hooks.submodule-commit-msg.hash-length 10`

