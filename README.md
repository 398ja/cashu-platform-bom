Cashu Platform BOM and Aggregator

Overview
- This repository contains the `cashu-platform-bom` at the root (`pom.xml`) and an optional aggregator at `aggregate/pom.xml` to build/deploy multiple Cashu projects in one go.

Quick Start
- Step 1: Install the BOM locally so the aggregator can import it offline:
  - `mvn -f pom.xml clean install`
- Step 2: Check out the Cashu projects under `modules/` (use git submodules or plain clones).
  - Helper script: `scripts/add-submodules.sh` (edit repo URLs first, then run)
- Step 3: Build all present modules via aggregator (profiles auto-activate when a module exists):
  - `mvn -f aggregate/pom.xml -T 1C clean install`
- Deploy all present modules:
  - Releases: `scripts/deploy-all.sh releases` (to https://maven.398ja.xyz/releases)
  - Snapshots: `scripts/deploy-all.sh snapshots` (to https://maven.398ja.xyz/snapshots)

Modules
- Expected module roots (each is a separate repository checked out under `modules/`):
  - `modules/cashu-lib`
  - `modules/cashu-gateway`
  - `modules/cashu-vault`
  - `modules/cashu-mint`
  - `modules/cashu-wallet`
  - `modules/cashu-client`
  - `modules/nostr-cashu`

Notes
- The aggregator imports the platform BOM, so all modules inherit the aligned versions defined here.
- Profiles in `aggregate/pom.xml` activate only if the corresponding `modules/<name>/pom.xml` exists, allowing partial builds.
- Ensure `~/.m2/settings.xml` has `<server>` credentials for any `<distributionManagement>` repositories required by the individual modules.
- To force a unified target repo for deployment, this project’s script passes `-DaltDeploymentRepository`.

Maven settings
- Add credentials in `~/.m2/settings.xml` for the reposilite endpoints. The `<id>` must match the id used by the deploy command:

  ````
  <settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 https://maven.apache.org/xsd/settings-1.0.0.xsd">
    <servers>
      <server>
        <id>reposilite-releases</id>
        <username>YOUR_USER</username>
        <password>YOUR_TOKEN</password>
      </server>
      <server>
        <id>reposilite-snapshots</id>
        <username>YOUR_USER</username>
        <password>YOUR_TOKEN</password>
      </server>
    </servers>
  </settings>
  ````

Important
- The aggregator orchestrates builds but does not become the parent POM of the individual modules. For full version alignment, each module should import `cashu-platform-bom` or adopt it as a parent, as appropriate.

Further Reading
- Detailed guide: `docs/USAGE.md`
- CI/CD with GitHub Actions: `docs/CI.md`
- Aggregator POM: `aggregate/pom.xml`
- Submodule helper: `scripts/add-submodules.sh`
- Deploy helper: `scripts/deploy-all.sh`
