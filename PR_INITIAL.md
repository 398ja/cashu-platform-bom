## Summary
Create `cashu-platform-bom` (Bill of Materials) for centralized version management across the entire Cashu ecosystem and related projects.

## What changed?
- Created new Maven BOM project: `cashu-platform-bom:1.0.0`
- Centralized version management for:
  - **Cashu ecosystem modules**:
    - cashu-lib (0.4.1): cashu-lib-entities, cashu-lib-crypto, cashu-lib-common
    - cashu-gateway (0.3.2): all gateway modules (model, rest, client, phoenixd, webhook, dummy, common)
    - cashu-vault (0.2.4): cashu-vault-jpa, cashu-vault-api
    - cashu-mint (0.2.4): cashu-mint-tools, cashu-mint-protocol, cashu-mint-rest
    - cashu-wallet (0.1.2): cashu-wallet-protocol, cashu-wallet-client
    - cashu-client (0.3.0-M2): wallet-core, wallet-storage-file, wallet-storage-h2, wallet-cli
    - nostr-cashu (0.2.1): nostr-cashu-nips
  - **Imported BOMs**:
    - nostr-java-bom (1.0.0) - provides shared dependencies
    - spring-boot-dependencies (3.5.5)
  - **Cashu-specific dependencies**: PostgreSQL (42.7.7), H2 (2.2.224), Flyway (11.2.0), Hibernate Envers, Picocli (4.7.6), Argon2, Jakarta Validation, Resilience4j, Logback, WireMock
  - **External tools**: phoenixd-java (0.1.4), phoenixd-mock (0.1.0)
  - **Maven plugins**: All standard plugins with consistent versions

## Breaking changes
- [ ] BREAKING: this change introduces breaking API or behavior

## Review focus
- Verify all Cashu ecosystem module versions match current releases
- Confirm nostr-java-bom import provides shared dependencies (BouncyCastle, Jackson, Lombok, test deps)
- Check Spring Boot BOM version (3.5.5) is appropriate
- Validate Cashu-specific dependency versions

## Checklist
- [x] Tests added or updated (N/A - BOM project has no code)
- [x] `mvn clean deploy` passes
- [ ] Documentation updated (README, docs, etc.)
- [x] No unused imports (N/A - BOM project)

## Benefits
- **Single source of truth**: All Cashu ecosystem versions in one place
- **Layered architecture**: Imports nostr-java-bom for shared dependencies, avoiding duplication
- **Consistency**: All Cashu projects get identical dependency versions
- **Simplified updates**: Bump cashu-lib version once, all dependent projects inherit it
- **Cross-project compatibility**: Ensures compatible versions across the entire ecosystem

## Architecture
```
cashu-platform-bom (this)
  ├─ imports nostr-java-bom (shared: Jackson, Lombok, BouncyCastle, test deps)
  ├─ imports spring-boot-dependencies
  ├─ defines all Cashu module versions
  └─ defines Cashu-specific dependencies
```

## Usage
Cashu projects import this BOM:

```xml
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

Bridge projects (e.g., nostr-cashu) can import both:
```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>xyz.tcheeric</groupId>
      <artifactId>nostr-java-bom</artifactId>
      <version>1.0.0</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
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

## Deployment
- Deployed to: https://maven.398ja.xyz/releases/xyz/tcheeric/cashu-platform-bom/1.0.0/
- Available for immediate use by all Cashu ecosystem projects

## Next Steps
1. Migrate cashu-vault to use this BOM
2. Migrate cashu-wallet to use this BOM
3. Migrate cashu-client to use this BOM
4. Migrate nostr-cashu to use both nostr-java-bom and cashu-platform-bom
