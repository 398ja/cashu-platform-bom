#!/usr/bin/env bash
set -euo pipefail

# This script helps you check out all Cashu projects under ./modules as git submodules.
# Fill in the correct repository URLs before running.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
MODULES_DIR="$ROOT_DIR/modules"

mkdir -p "$MODULES_DIR"
cd "$ROOT_DIR"

echo "Preparing to add submodules under: $MODULES_DIR"
echo "NOTE: Using GitHub org 398ja for all repos."

GIT_BASE="https://github.com/398ja"

declare -A REPOS=(
  [cashu-lib]="$GIT_BASE/cashu-lib.git"
  [cashu-gateway]="$GIT_BASE/cashu-gateway.git"
  [cashu-vault]="$GIT_BASE/cashu-vault.git"
  [cashu-mint]="$GIT_BASE/cashu-mint.git"
  [cashu-wallet]="$GIT_BASE/cashu-wallet.git"
  [cashu-client]="$GIT_BASE/cashu-client.git"
  [nostr-cashu]="$GIT_BASE/nostr-cashu.git"
)

for name in "${!REPOS[@]}"; do
  url="${REPOS[$name]}"
  # URL already set to your GitHub org
  target="modules/$name"
  if [[ -d "$target/.git" ]]; then
    echo "Already present: $target"
    continue
  fi
  echo "Adding $name from $url -> $target"
  git submodule add "$url" "$target"
done

echo "Submodule initialization complete. You can now run:"
echo "  mvn -f aggregate/pom.xml -T 1C clean install"
