
# List Submodule Changes Commit Hook
A Git-hook which when you commits changes in a submodule, automagically inserts a summary of these changes in the commit message.
Let's say you make some new commits in submodule1 & submodule2. When you then commit those modules in the main repo, your commit msg will look like this
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

## Installation
Download `prepare-commit-msg` and place it in your repo's hooks folder `.git/hooks/prepare-commit-msg`
Then make it executable: `chmod +x .git/hooks/prepare-commit-msg`

Or you can run the following from the root folder in your repo:

`curl -O --output-dir .git/hooks/ https://raw.githubusercontent.com/wingez/submodule-commit-msg/main/prepare-commit-msg && chmod +x .git/hooks/prepare-commit-msg`

## Configuration
The script can be configured to by setting the following environment variables to integer values:

| Environment variable | Default | Description |
|----------------------|---------|-------------|
| `SUBMODULE_HOOK_HASH_LENGTH` |  8  |   Include the first n letters of each submodule commit hash          |
| `SUBMODULE_HOOK_MAX_COMMIT_SHOWN` |    12     |      Max amount of commits listed per submodule before truncating list       |
| `SUBMODULE_HOOK_DEBUG` |         |      Set to give more detailed error-information        |

 

