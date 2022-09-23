

A Git-hook which when you commits changes in a submodule, automagically inserts a summary of these changes in the commit message.
Let's say you make some new commits in submodule1 & submodule2. When you then commit those modules in the main repo, your commit msg will look like this
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
Download and place the file under `.git/hooks/prepare-commit-msg`
Make it executable: `chmod +x .git/hooks/prepare-commit-msg`
