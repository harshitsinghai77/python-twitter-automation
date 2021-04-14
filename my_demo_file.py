import git

g = git.Git()
g.fetch("origin", "gh-action-check-migration")
g.checkout("gh-action-check-migration")