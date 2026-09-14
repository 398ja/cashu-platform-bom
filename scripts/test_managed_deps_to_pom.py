#!/usr/bin/env python3
"""Tests for the BOM-to-scannable-pom generator.

The generator exists so that a vulnerability scanner sees concrete
coordinate-plus-version facts. These tests pin the behaviour that makes that
true, because a silent regression here produces an empty pom and therefore a
scan that passes by examining nothing.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent / "managed-deps-to-pom.py"

BOM = """<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>g</groupId><artifactId>a</artifactId><version>1</version>
  <packaging>pom</packaging>
  <properties>
    <postgresql.version>42.7.12</postgresql.version>
  </properties>
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <version>${postgresql.version}</version>
      </dependency>
      <dependency>
        <groupId>com.example</groupId>
        <artifactId>literal</artifactId>
        <version>1.2.3</version>
      </dependency>
      <dependency>
        <groupId>xyz.tcheeric</groupId>
        <artifactId>cashu-lib-crypto</artifactId>
        <version>0.4.1</version>
      </dependency>
      <dependency>
        <groupId>com.example</groupId>
        <artifactId>some-bom</artifactId>
        <version>9.9.9</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>
</project>
"""


def render_with_message(bom_text):
    """Run the generator, returning (exit_code, output_pom, combined_output)."""
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "pom.xml"
        destination = Path(directory) / "out.xml"
        source.write_text(bom_text)
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(source), str(destination)],
            capture_output=True, text=True)
        rendered = destination.read_text() if destination.exists() else ""
        return (completed.returncode, rendered,
                completed.stdout + completed.stderr)


def render(bom_text):
    """Run the generator over bom_text, returning (exit_code, output_pom)."""
    exit_code, rendered, _ = render_with_message(bom_text)
    return exit_code, rendered


class ManagedDependencyRenderingTest(unittest.TestCase):

    # A version given as a ${property} reference must appear in the output fully
    # resolved: an unresolved reference is exactly what scanners cannot match.
    def test_resolves_property_versions(self):
        _, rendered = render(BOM)
        self.assertIn("<version>42.7.12</version>", rendered)
        self.assertNotIn("${", rendered)

    # A literal version needs no resolution but must still be carried across.
    def test_keeps_literal_versions(self):
        _, rendered = render(BOM)
        self.assertIn("<artifactId>literal</artifactId>", rendered)
        self.assertIn("<version>1.2.3</version>", rendered)

    # Managed entries must become real <dependencies>, since a scanner ignores
    # anything inside <dependencyManagement>.
    def test_emits_real_dependencies(self):
        _, rendered = render(BOM)
        self.assertNotIn("<dependencyManagement>", rendered)
        self.assertEqual(2, rendered.count("<dependency>"))

    # An imported BOM contributes no artifact of its own, so scanning it would
    # report a version that nothing actually resolves to.
    def test_skips_imported_boms(self):
        _, rendered = render(BOM)
        self.assertNotIn("some-bom", rendered)

    # A property whose value is itself a reference must be followed through. If
    # expansion stopped early the output would still contain a ${...} literal,
    # which no scanner can match -- so this must resolve or be dropped, never
    # emitted half-expanded.
    def test_resolves_indirect_properties(self):
        indirect = BOM.replace(
            "<postgresql.version>42.7.12</postgresql.version>",
            "<postgresql.version>${pg.actual}</postgresql.version>"
            "<pg.actual>42.7.12</pg.actual>")
        _, rendered = render(indirect)
        self.assertIn("<version>42.7.12</version>", rendered)
        self.assertNotIn("${", rendered)

    # A reference that cannot be resolved must abort the run. Dropping the entry
    # instead would remove a real coordinate from the scan and still report
    # success, which is the failure this script exists to prevent -- and silently
    # skipping one dependency is that same failure at a smaller scale.
    def test_fails_on_unresolvable_reference(self):
        exit_code, rendered, message = render_with_message(
            BOM.replace("${postgresql.version}", "${nope}-final"))
        self.assertNotEqual(0, exit_code)
        self.assertEqual("", rendered)
        self.assertIn("postgresql", message)
        self.assertIn("nope", message)

    # A malformed reference with no closing brace must be reported, not raised as
    # an unhandled ValueError from deep inside string handling.
    def test_fails_readably_on_malformed_reference(self):
        exit_code, _, message = render_with_message(
            BOM.replace("${postgresql.version}", "${unclosed"))
        self.assertNotEqual(0, exit_code)
        self.assertIn("malformed", message)
        self.assertNotIn("Traceback", message)

    # A scannable entry with no version at all cannot be scanned, so it must be
    # reported rather than skipped.
    def test_fails_on_missing_version(self):
        exit_code, _, message = render_with_message(
            BOM.replace("<version>1.2.3</version>", ""))
        self.assertNotEqual(0, exit_code)
        self.assertIn("literal", message)

    # Expansion is bounded at five rounds to avoid looping forever on a cyclic
    # property. If a chain is deeper than that, the value is still unresolved
    # when the loop gives up, and it must be dropped rather than emitted with a
    # ${...} still in it -- which is the one case the final guard exists for.
    def test_fails_on_chains_nested_deeper_than_the_bound(self):
        chain = "".join(f"<p{i}>${{p{i + 1}}}</p{i}>" for i in range(8))
        deep = BOM.replace(
            "<postgresql.version>42.7.12</postgresql.version>",
            f"<postgresql.version>${{p0}}</postgresql.version>{chain}"
            "<p8>42.7.12</p8>")
        exit_code, rendered, message = render_with_message(deep)
        self.assertNotEqual(0, exit_code)
        self.assertEqual("", rendered)
        self.assertIn("unresolved", message)

    # First-party artifacts are not published to public repositories, so a scanner
    # cannot resolve them; in bulk those failed lookups earn an HTTP 429 that aborts
    # the whole scan. They carry no public advisories either, so excluding them costs
    # no coverage.
    def test_excludes_first_party_artifacts(self):
        _, rendered = render(BOM)
        self.assertNotIn("cashu-lib-crypto", rendered)
        self.assertNotIn("<groupId>xyz.tcheeric</groupId>", rendered)
        self.assertEqual(2, rendered.count("<dependency>"))

    # The failure that matters most: if nothing resolves, the generator must
    # fail loudly rather than emit an empty pom that would scan clean.
    def test_fails_when_nothing_resolves(self):
        empty = BOM.replace("${postgresql.version}", "${undefined.version}") \
                   .replace("<version>1.2.3</version>", "<version>${also.undefined}</version>")
        exit_code, rendered = render(empty)
        self.assertNotEqual(0, exit_code)
        self.assertEqual("", rendered)

    # A BOM with no third-party entries at all must fail rather than emit a valid
    # but empty pom, which would scan clean and report success.
    def test_fails_on_empty_result(self):
        only_first_party = """<project xmlns="http://maven.apache.org/POM/4.0.0">
          <modelVersion>4.0.0</modelVersion>
          <groupId>g</groupId><artifactId>a</artifactId><version>1</version>
          <dependencyManagement><dependencies>
            <dependency>
              <groupId>xyz.tcheeric</groupId>
              <artifactId>internal</artifactId>
              <version>1.0</version>
            </dependency>
          </dependencies></dependencyManagement>
        </project>"""
        exit_code, rendered, message = render_with_message(only_first_party)
        self.assertNotEqual(0, exit_code)
        self.assertEqual("", rendered)
        self.assertIn("refusing", message)

    # Wrong invocation must produce usage text, not an IndexError traceback.
    def test_reports_usage_without_arguments(self):
        completed = subprocess.run([sys.executable, str(SCRIPT)],
                                   capture_output=True, text=True)
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("usage:", completed.stdout + completed.stderr)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
