import argparse
import urllib.request

import github

import review_runner_lib
import review_types


def process_commit(commit_sha: str) -> review_types.ReviewRequest:
    with urllib.request.urlopen(
        f"https://github.com/llvm/llvm-project/commit/{commit_sha}.diff"
    ) as commit_diff_response:
        commit_diff = commit_diff_response.read().decode("utf-8")
    # TODO(boomanaiden154): We should eventually parse the title and description
    # from the .patch URL.
    return review_types.ReviewRequest(diff=commit_diff, title="", description="")


def process_pull_request(pr_number: int) -> review_types.ReviewRequest:
    with urllib.request.urlopen(
        f"https://patch-diff.githubusercontent.com/raw/llvm/llvm-project/pull/{pr_number}.diff"
    ) as pr_diff_response:
        pr_diff = pr_diff_response.read().decode("utf-8")
    llvm_repo = github.Github().get_repo("llvm/llvm-project")
    pull_request = llvm_repo.get_pull(pr_number)
    return review_types.ReviewRequest(
        diff=pr_diff, title=pull_request.title, description=pull_request.body
    )


def main(arguments):
    if arguments.pr is None and arguments.commit is None:
        raise ValueError("Expected either a commit or a PR to review.")
    if arguments.pr and arguments.commit:
        raise ValueError("Only one of a PR or a commit can be specified.")
    review_request = (
        process_pull_request(arguments.pr)
        if arguments.pr
        else process_commit(arguments.commit)
    )
    review_responses = review_runner_lib.perform_review(review_request)
    print(review_responses)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A tool that will run agentic review against LLVM PRs/commits"
    )
    parser.add_argument("--pr", type=int, default=None, nargs="?")
    # TODO(boomanaiden154): We should have a flag here for specifying the base
    # commit of a PR once the checkout infrastructure is implemented.
    parser.add_argument("--commit", type=str, default=None, nargs="?")
    arguments = parser.parse_args()
    main(arguments)
