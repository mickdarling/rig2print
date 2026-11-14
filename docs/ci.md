# CI and pull requests

The `CI` workflow runs on every pull request targeting `main`, pushes to `main`, merge-queue checks, and manual dispatch after the workflow is on the default branch. Documentation-only PRs also run it so a required check is never left pending by a path filter.

## Checks

Four Linux jobs run the same `python scripts/check.py` command using Python 3.11, 3.12, 3.13 and 3.14. The command needs Git and the Python standard library; there are no pip installs. Rust jobs build and test the core on the minimum supported compiler 1.85.0 and current stable, using the committed Cargo.lock. Stable also runs rustfmt and Clippy with warnings treated as errors.

- Parse every tracked Python source file, including Blender scripts, without importing Blender.
- Parse tracked JSON with duplicate-key and non-finite-constant rejection.
- Check the portable Dollhouse manifest's dependency references, creation order, duplicate definitions, ensemble roles and template variables offline.
- Smoke-test the CLI and run the full unit suite.

The final `CI passed` check succeeds only when both language matrices succeed. It runs even if a dependency fails; failed, cancelled or skipped matrix results cannot count as success. Python jobs have five-minute timeouts, Rust jobs ten minutes, and the final check two minutes. New pushes cancel superseded runs for the same PR.

The additional required `Blender rig integration` job installs Ubuntu's Blender, verifies the pinned Ferris asset, inspects its actual rig and runs the Rust prototype command on its weighted left middle knee. It checks the exported binary STL independently and preserves source/inventory/prototype/report artifacts. The verified Blender version is recorded in the report. The aggregate check also requires this job to pass.

This job supplies source, adapter and limited geometry evidence. It does not contact a Dollhouse server, establish continuous collision freedom, run a slicer or certify a physical print. Report those separately. The Ferris specimen can pass basic geometry checks while still being flagged for shape review.

## Execution and dependencies

Public PR code runs on GitHub-hosted Ubuntu 24.04 runners, including fork PRs subject to GitHub's normal approval policy. The workflow uses `pull_request`, a read-only repository token and checkout without persisted credentials. It does not require repository secrets or use personal self-hosted runners.

Actions are pinned to full commit SHAs. Dependabot checks action and Cargo dependencies monthly and opens update PRs; review and CI apply to those PRs too. The Rust core uses serde_json; the Python tools have no third-party runtime dependency outside Blender.

## Merge protection

The default is to merge only a clean PR: required CI passes and review findings
are addressed. Wait for automated review of the final head commit, then inspect
review submissions, inline comments and unresolved threads immediately before
merging. No review yet is a pending review, not a clean result. If the head
changes, wait for review of the new head.

Fix P1 and P2 findings before merging under the normal workflow. An exception
authorized by the task context must have a separate linked issue for each
deferred finding before the merge, including priority, original review link,
impact, acceptance criteria and reason for deferral. Document the exception in
the PR. Issue creation is tracking, not a substitute for a clean review or a
reason to resolve an unfixed thread.

Workflow files alone do not enforce merge policy. Configure a `main` branch rule or ruleset to require a pull request and the `CI passed` status check, block force pushes/deletion, and require conversation resolution. Require branches to be up to date if using ordinary merges; use the merge queue's checks if a queue is enabled. The workflow supports either arrangement but does not enable a queue.

This document describes the intended settings, not proof that repository rules have been applied. Inspect the live GitHub branch settings for enforcement. A solo maintainer can require the PR and check without requiring an approval from a second person.

## Local verification

```sh
git add <new-files>
python3 scripts/check.py --all
git diff --check
```

The pull-request template captures the problem, resulting behavior and evidence. Keep source licenses and the distinction between unrun and verified physical checks explicit.

`--all` adds the same cargo fmt, clippy and test commands used by CI. Without it the script runs only Python/data checks, useful when working on the Blender adapter without a Rust toolchain installed.
