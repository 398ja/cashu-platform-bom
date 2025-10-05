# Cashu Platform CI/CD

## Overview
- GitHub Actions workflows build and deploy aggregated Cashu projects using the platform BOM.
- Requires modules checked out under `modules/` (submodules recommended for CI).

## Workflows
- Build: `.github/workflows/build.yml`
  - Triggers: `push` (all branches), `pull_request`.
  - Steps:
    - Checkout with submodules.
    - Setup Java 21 with Maven cache.
    - Install the BOM (`mvn -f pom.xml clean install`).
    - Build/verify aggregated modules (`mvn -f aggregate/pom.xml -T 1C clean verify`).

- Deploy: `.github/workflows/deploy.yml`
  - Triggers:
    - Manual: `workflow_dispatch` with `channel` input (`releases` or `snapshots`).
    - Tag push: `v*` (deploys to `releases`).
  - Steps:
    - Checkout with submodules.
    - Determine target channel → set `SERVER_ID` and `REPO_URL`.
    - Validate tag format for push events (expects `vMAJOR.MINOR.PATCH`, optional suffix).
    - Setup Java 21 and inject Maven server credentials (and optional GPG key).
    - Install the BOM.
    - Deploy aggregated modules with `-DaltDeploymentRepository` to unify the target repo.

## Required GitHub Secrets
- `REPO_USER`: username for `https://maven.398ja.xyz`.
- `REPO_TOKEN`: password or token for `https://maven.398ja.xyz`.
- Optional for signing:
  - `GPG_PRIVATE_KEY`: ASCII-armored private key content.
  - `GPG_PASSPHRASE`: passphrase for the private key.

## Repository IDs and URLs
- Releases: `SERVER_ID = reposilite-releases`, `REPO_URL = https://maven.398ja.xyz/releases`.
- Snapshots: `SERVER_ID = reposilite-snapshots`, `REPO_URL = https://maven.398ja.xyz/snapshots`.

## Usage
- Build runs automatically on pushes and PRs.
- Manual deploy:
  - In GitHub → Actions → `Deploy` → `Run workflow` → choose `releases` or `snapshots`.
- Tag-based deploy:
  - Create tag `vX.Y.Z` and push it; the workflow deploys to `releases`.

## Notes
- Ensure submodules in `modules/` point to the desired commit SHAs for reproducible builds.
- Each module should import `cashu-platform-bom` to align dependency versions.
- If some modules are absent, the aggregator builds only those present (profiles auto-activate).

## GitHub Environments (Recommended)
- Create two environments in your repository: `releases` and `snapshots`.
- Why: environment-scoped secrets and optional approvals for production deployments.

## Setup Steps
1) In GitHub → Settings → Environments → New environment → create `snapshots` and `releases`.
2) For each environment, add secrets with the same names used in the workflow:
   - `REPO_USER`, `REPO_TOKEN`, optionally `GPG_PRIVATE_KEY`, `GPG_PASSPHRASE`.
3) (Optional) Add protection rules for `releases`:
   - Required reviewers: select maintainers who must approve before the job runs.
   - Wait timer: add a delay if desired.
4) The workflow assigns the environment dynamically based on the chosen channel:
   - Manual `channel=releases` → environment `releases`.
   - Manual `channel=snapshots` → environment `snapshots`.
   - Tag push (`v*`) → environment `releases`.

## Notes on Secrets Resolution
- The workflow references `secrets.REPO_USER` and `secrets.REPO_TOKEN`.
- When a job targets an environment, GitHub exposes environment-level secrets to the `secrets` context.
- You can keep the same secret names across environments; values differ per environment.
