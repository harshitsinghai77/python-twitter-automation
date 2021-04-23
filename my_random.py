import argparse

import aiohttp
import asyncio
import git

OWNER = "harshitsinghai77"
DEFAULT_REPO = "python-twitter-automation"
DEFAULT_MASTER_BRANCH = "master"
SPOCK_EMAIL = "harshitsinghai77@gmail.com"
SPOCK_NAME = "harshitsinghai77"
BASE_DIR = "my_demo_file.py"

BASE_URL = "https://api.github.com/"
params = {"state": "open", "per_page": 100}
headers = {"Accept": "application/vnd.github.v3+json"}


async def fetch(url, session, branch_name=None):
    """Make a get request to the given url, return response and status."""
    async with session.get(url, params=params, headers=headers) as resp:
        if branch_name:
            return {"branch_name": branch_name, "files": await resp.json()}
        return await resp.json(), resp.status


# def git_set_user_config():
#     """Set name and email config to use git."""
#     repo = git.Repo()
#     repo.config_writer().set_value("user", "name", SPOCK_NAME).release()
#     repo.config_writer().set_value("user", "email", SPOCK_EMAIL).release()


def rebase_branch_with_master(branch_name):
    """Fetch the branch from origin, checkout the branch and rebase it with master."""
    try:
        g = git.Git()
        g.fetch("origin", branch_name)
        g.checkout(branch_name)

        g.fetch("origin", DEFAULT_MASTER_BRANCH)
        g.rebase(f"origin/{DEFAULT_MASTER_BRANCH}")
    except git.exc.GitError as e:
        print("Some error occured while rebasing ", branch_name, e)
    finally:
        g.push(force=True)


async def main(pat: str):
    """pat: personal access token."""
    headers["Authorization"] = f"token {pat}"

    async with aiohttp.ClientSession() as session:
        # get all open pull requests
        all_pull_requests_url = BASE_URL + f"repos/{OWNER}/{DEFAULT_REPO}/pulls"
        all_pull_requests, status = await fetch(
            url=all_pull_requests_url, session=session
        )

        if status != 200:
            print(all_pull_requests)
            return

        if not all_pull_requests:
            return

        # get pull request number and name of the branch
        pull_requests = [(pr["number"], pr["head"]["ref"]) for pr in all_pull_requests]

        # for every open pull request get the list of files_changed in the PR. This will be async task,
        # each task will be append to a list and run concurrently. If all awaitables are completed successfully,
        # the result is an aggregate list of returned values.
        pull_request_files_changed_task = []

        for pr_number, branch_name in pull_requests:
            file_changed_url = (
                BASE_URL + f"repos/{OWNER}/{DEFAULT_REPO}/pulls/{pr_number}/files"
            )
            task = asyncio.create_task(
                fetch(url=file_changed_url, branch_name=branch_name, session=session)
            )
            pull_request_files_changed_task.append(task)

        all_pr_files_changed = await asyncio.gather(*pull_request_files_changed_task)

        # If the PR make any changes to the file inside BASE_DIR then add it the rebase_branch
        rebase_branch = set()
        for pr in all_pr_files_changed:
            branch_name = pr["branch_name"]
            for files in pr["files"]:
                file_changed = files["filename"]
                if file_changed.startswith(BASE_DIR):
                    print("branch_name for rebase", branch_name)
                    rebase_branch.add(branch_name)
                    break

        # set user config for git
        # git_set_user_config()

        # rebase `rebase_branch` with master.
        # for branch_name in rebase_branch:
        #     print("Rebasing for branch ", branch_name)
        #     rebase_branch_with_master(branch_name=branch_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pat", dest="pat", type=str)
    pat_key = parser.parse_args().pat

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(pat=pat_key))
    loop.close()
