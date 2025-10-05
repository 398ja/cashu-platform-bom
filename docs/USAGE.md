Cashu Platform: Build and Deploy Guide

**Purpose**
- Build and deploy multiple Cashu projects from a single workspace using the platform BOM and aggregator.

**Prerequisites**
- JDK `21` on PATH (`java -version`).
- Maven `3.8+` (`mvn -v`).
- Git with access to the `398ja` organization.
- Credentials for `https://maven.398ja.xyz` configured in `~/.m2/settings.xml`.

**Repository Layout**
- BOM POM: `pom.xml` (at repo root)
- Aggregator POM: `aggregate/pom.xml`
- Helper scripts: `scripts/add-submodules.sh`, `scripts/deploy-all.sh`
- Modules checkout location: `modules/`

**Get Sources**
- Option A — submodules (recommended):
  - `scripts/add-submodules.sh`
  - This creates: `modules/cashu-lib`, `modules/cashu-gateway`, `modules/cashu-vault`, `modules/cashu-mint`, `modules/cashu-wallet`, `modules/cashu-client`, `modules/nostr-cashu`.
- Option B — plain clones:
  - `git clone https://github.com/398ja/cashu-lib.git modules/cashu-lib`
  - Repeat for the remaining projects listed above.

**Build**
- Install the BOM locally:
  - `mvn -f pom.xml clean install`
- Build all present modules via the aggregator (parallel):
  - `mvn -f aggregate/pom.xml -T 1C clean install`
- Notes:
  - Profiles in `aggregate/pom.xml` auto-activate when `modules/<name>/pom.xml` exists, allowing partial builds.

**Deploy**
- Releases repository:
  - `scripts/deploy-all.sh releases`
- Snapshots repository:
  - `scripts/deploy-all.sh snapshots`
- The script passes `-DaltDeploymentRepository` so all modules deploy to a single target (`reposilite-releases` or `reposilite-snapshots`).

**Maven Settings**
- Add credentials in `~/.m2/settings.xml` with matching IDs:

  ```
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
  ```

**Version Alignment**
- The aggregator does not become the parent POM of module projects.
- For consistent dependency versions, each module should import the platform BOM in its own POM:

  ```
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>xyz.tcheeric</groupId>
        <artifactId>cashu-platform-bom</artifactId>
        <version>1.0.0</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>
  ```

**Partial Builds**
- Only need `cashu-lib`? Check out `modules/cashu-lib` and run:
  - `mvn -f aggregate/pom.xml clean install`
- The aggregator will include only present modules.

**Troubleshooting**
- Missing credentials error when deploying:
  - Ensure `~/.m2/settings.xml` contains `reposilite-releases`/`reposilite-snapshots` with valid credentials.
- BOM not found during aggregator build:
  - Run `mvn -f pom.xml clean install` to install `cashu-platform-bom` locally first.
- GPG/signing failures:
  - If any module enforces signing, configure keys via `maven-gpg-plugin` and your environment. You can temporarily add `-Dgpg.skip=true` if policy allows.
- Network timeouts:
  - Re-run with `-e -X` for debug; verify repository endpoints are reachable.

**FAQ**
- Can I deploy to both releases and snapshots in one run?
  - No; run the deploy script separately for each channel.
- Do I have to use submodules?
  - No; plain clones in `modules/` work. Submodules help pin exact commits for reproducible builds.

