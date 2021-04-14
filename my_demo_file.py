import git

branch="feature-branch"
rebase_branch="feature-branch-2"

g = git.Git()
g.fetch("origin", branch)
g.checkout(branch)

g.fetch("origin", "master")
g.rebase(f"origin/{rebase_branch}")