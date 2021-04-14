import git

branch="feature-branch-2"
g = git.Git()
g.fetch("origin", branch)
g.checkout(branch)