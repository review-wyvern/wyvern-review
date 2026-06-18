# Wyvern Review

Agentic review infrastructure for LLVM.

https://discourse.llvm.org/t/rfc-upstream-infrastructure-for-ai-review-of-prs/91042

## Architecture

There are two main components:

1. `review-coordinator` - Responsible for polling GitHub for new PRs/commits to
   run agents against, distributing review jobs onto the cluster, recieving
   results, storing them in the DB, and hosting the review UI.
2. `review-runner` - Responsible for actually running the review. Once launched
   by the review coordinator, it will run all of the specified agents and
   coordinate any dependencies like an LLVM build.

