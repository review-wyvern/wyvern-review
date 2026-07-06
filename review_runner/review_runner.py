import argparse

import review_runner_lib
import review_types


def process_commit(commit_sha: str) -> review_types.ReviewRequest:
    pass


def process_pull_request(pr_number: int) -> review_types.ReviewRequest:
    pass


def main(arguments):
    if arguments.pr is None and arguments.commit is None:
        raise ValueError("Expected either a commit or a PR to review.")


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
