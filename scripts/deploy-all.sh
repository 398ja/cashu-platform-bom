#!/usr/bin/env bash
set -euo pipefail

# Deploys all present modules via the aggregator to the given Maven repository.
# Usage:
#   scripts/deploy-all.sh [releases|snapshots]
# Defaults to releases: https://maven.398ja.xyz/releases

CHANNEL="${1:-releases}"
case "$CHANNEL" in
  releases) REPO_URL="https://maven.398ja.xyz/releases"; REPO_ID="reposilite-releases" ;;
  snapshots) REPO_URL="https://maven.398ja.xyz/snapshots"; REPO_ID="reposilite-snapshots" ;;
  *) echo "Unknown channel: $CHANNEL (use 'releases' or 'snapshots')"; exit 1 ;;
esac

echo "Using $CHANNEL repository: $REPO_URL (id=$REPO_ID)"

# Ensure the BOM is installed locally so aggregator builds can resolve it offline
mvn -f pom.xml -q clean install

# Deploy all present modules using altDeploymentRepository to force a unified target
mvn -f aggregate/pom.xml -T 1C -DskipTests \
  -DaltDeploymentRepository="${REPO_ID}::default::${REPO_URL}" \
  deploy

echo "Deployment complete to ${REPO_URL}"

