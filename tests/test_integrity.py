"""Test the integrity of the datasources references."""

import csv
import unittest
from pathlib import Path

import bioregistry
from bioregistry.external.miriam import get_miriam

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()
HEADERS_PATH = ROOT.joinpath("datasources_headers.tsv")
DATASOURCES_PATH = ROOT.joinpath("datasources.tsv")


class TestIntegrity(unittest.TestCase):
    """Test data integrity."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load the data sources rows."""
        with HEADERS_PATH.open() as file:
            _, *cls.columns = [row[1] for row in csv.reader(file, delimiter="\t")]
        with DATASOURCES_PATH.open() as file:
            cls.rows = list(csv.reader(file, delimiter="\t"))

    def test_lengths(self):
        """Test the row lengths."""
        for i, line in enumerate(self.rows, start=1):
            self.assertEqual(
                len(self.columns),
                len(line),
                msg=f"Row {i} has the wrong number of columns",
            )

    def test_valid_miriam(self):
        """Test that MIRIAM prefixes are valid."""
        valid_miriam_prefixes = set(get_miriam())
        for i, line in enumerate(self.rows, start=1):
            resource, uri = line[0], line[8]
            if not uri.startswith("urn:miriam"):
                continue
            miriam_prefix = uri.removeprefix("urn:miriam:")
            with self.subTest(resource=resource, miriam=miriam_prefix):
                self.assertIn(
                    miriam_prefix,
                    valid_miriam_prefixes,
                    msg=f"\n\t[line {i}] Invalid MIRIAM prefix for {resource}: {uri}",
                )

    def test_patterns(self):
        """Check the example identifiers pass the given regular expressions."""
        for i, line in enumerate(self.rows, start=1):
            resource, example, pattern = line[0], line[4], line[9]
            if not example or not pattern:
                continue
            with self.subTest(resource=resource, example=example, pattern=pattern):
                self.assertRegex(example, pattern)

    def test_valid_bioregistry(self):
        """Test that Bioregistry prefixes are valid."""
        for i, line in enumerate(self.rows, start=1):
            resource, bioregistry_prefix = line[0], line[12]
            if not bioregistry_prefix:
                continue
            with self.subTest(resource=resource, prefix=bioregistry_prefix):
                norm_prefix = bioregistry.normalize_prefix(bioregistry_prefix)
                self.assertIsNotNone(
                    norm_prefix,
                    msg=f"unrecognized Bioregistry prefix: {bioregistry_prefix} in {resource}",
                )
                self.assertEqual(
                    bioregistry_prefix,
                    norm_prefix,
                    msg="unstandardized Bioregistry prefix",
                )
