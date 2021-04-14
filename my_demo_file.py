import git

branch="feature-branch"

g = git.Git()
g.fetch("origin", branch)
g.checkout(branch)

g.fetch("origin", "master")
g.rebase("origin/master")