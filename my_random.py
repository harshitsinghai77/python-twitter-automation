import argparse
import aiohttp
import asyncio

import git

# OWNER = "deepsourcelabs"
# DEFAULT_REPO = "asgard"
# BASE_DIR = "core/migrations/"

OWNER = "harshitsinghai77"
DEFAULT_REPO = "python-twitter-automation"
BASE_DIR = "my_folder/"

BASE_URL = "https://api.github.com/"
params = {"state": "open", "per_page": 100}
headers = {"Accept": "application/vnd.github.v3+json"}


async def fetch(url, session, branch_name=None):
    """Make a get request to the given url, return response and status."""
    async with session.get(url, params=params, headers=headers) as resp:
        if branch_name:
            return {"branch_name": branch_name, "files": await resp.json()}
        return await resp.json(), resp.status


async def post(url, comment, session):
    """Make a post request to the given url, return response and status."""
    async with session.post(url, json={"body": comment}, headers=headers) as resp:
        return await resp.json(), resp.status


def rebase_branch_with_master(branch_name):
    
    # branch="feature-branch"
    master_branch="master"

    g = git.Git()
    g.fetch("origin", branch_name)
    g.checkout(branch_name)

    g.fetch("origin", "master")
    g.rebase(f"origin/{master_branch}")


async def main(pat: str):
    """pat: personal access token."""
    headers["Authorization"] = "token " + pat

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
        pull_request = [(pr["number"], pr["head"]["ref"]) for pr in all_pull_requests]

        # for every open pull request get the list of files_changed in the PR. This will be async task,
        # each task will be append to a list and run concurrently. If all awaitables are completed successfully,
        # the result is an aggregate list of returned values.
        pull_request_files_changed_task = []

        for pr in pull_request:
            pr_number = pr[0]
            branch_name = pr[1]
            file_changed_url = (
                BASE_URL + f"repos/{OWNER}/{DEFAULT_REPO}/pulls/{pr_number}/files"
            )
            task = asyncio.create_task(
                fetch(url=file_changed_url, branch_name=branch_name, session=session)
            )
            pull_request_files_changed_task.append(task)

        all_pr_files_changed = await asyncio.gather(*pull_request_files_changed_task)

        # with open("scripts/dump1.json", "w") as json_file:
        #     json.dump(list_pull_requests, json_file)

        # If the PR changed the file inside BASE_DIR then add it the rebase_pr
        rebase_pr = set()
        for pr in all_pr_files_changed:
            branch_name = pr["branch_name"]
            for files in pr["files"]:
                file_changed = files["filename"]
                if file_changed.startswith(BASE_DIR):
                    rebase_pr.add(branch_name)
                    break

        for pr in rebase_pr:
            print("Rebasing for pr ", pr)
            rebase_branch_with_master(pr)
        # # Loop through rebase_pr and for each pr, rebase the branch by commenting `/rebase`
        # for pr in rebase_pr:
        #     comment_url = (
        #         BASE_URL + f"repos/{OWNER}/{DEFAULT_REPO}/issues/{pr}/comments"
        #     )
        #     comment, status = await post(
        #         url=comment_url, comment="/rebase", session=session
        #     )
        #     if status == 201:
        #         print("Rebase the PR ", comment["html_url"])
        #     else:
        #         print("Some error occured ", comment)
        # url = BASE_URL + f"repos/{OWNER}/{DEFAULT_REPO}/merges"
        # result = await merge(
        #     url=url, head="my-temp-branch", base="master", session=session
        # )
        # print(result)


parser = argparse.ArgumentParser()
parser.add_argument("--pat", dest="pat", type=str)
pat_key = parser.parse_args().pat

loop = asyncio.get_event_loop()
loop.run_until_complete(main(pat=pat_key))
loop.close()

# g = git.Git()
# g.fetch("origin", "gh-action-check-migration")
# g.checkout("gh-action-check-migration")

# g.fetch("origin", "master")
# g.rebase("origin/master")

# repo = git.Repo()
# repo.git.fetch("origin", "master")
# repo.git.rebase("origin/master")

# rebased = repo.git.rebase()
# print(rebased)
