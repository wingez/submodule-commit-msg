

Git-hook which inserts a summary of changes in submodules in each commit message.
For example inserts this into your commit messages:
```
My new commit

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
Place download and place the file under `.git/hooks/prepare-commit-msg`
Make it executable: `chmod +x .git/hooks/prepare-commit-msg`
