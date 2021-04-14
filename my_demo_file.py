import git

branch="feature-branch"
master_branch="master"

g = git.Git()
g.fetch("origin", branch)
g.checkout(branch)

g.fetch("origin", "master")
g.rebase(f"origin/{master_branch}")