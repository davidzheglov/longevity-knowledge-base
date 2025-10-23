import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.mammal_data import generate_mammal_report, _normalize_user_name, _extract_pretty_name

class TestMammalData(unittest.TestCase):
    def test_generate_mammal_report_human(self):
        """Test mammal report generation for Homo sapiens"""
        output = generate_mammal_report('Homo sapiens')
        self.assertTrue(os.path.exists(output))
        self.assertTrue(output.endswith('Homo_sapiens_report.txt'))
        # Verify content
        with open(output, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('Homo sapiens', content)
            self.assertIn('PHYLOGENY', content)
            self.assertIn('LIFESPAN', content)
        if os.path.exists(output):
            os.remove(output)

    def test_generate_mammal_report_elephant(self):
        """Test mammal report for Loxodonta africana"""
        output = generate_mammal_report('Loxodonta africana')
        self.assertTrue(os.path.exists(output))
        with open(output, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('Loxodonta africana', content)
        if os.path.exists(output):
            os.remove(output)

    def test_generate_mammal_report_mouse(self):
        """Test mammal report for Mus musculus"""
        output = generate_mammal_report('Mus musculus')
        self.assertTrue(os.path.exists(output))
        with open(output, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('Mus musculus', content)
        if os.path.exists(output):
            os.remove(output)

    def test_generate_mammal_report_invalid_species(self):
        """Test that invalid species raises ValueError"""
        with self.assertRaises(ValueError):
            generate_mammal_report('NonExistentSpecies123')

    def test_normalize_user_name(self):
        """Test user name normalization"""
        self.assertEqual(_normalize_user_name('Homo sapiens'), 'Homo_sapiens')
        self.assertEqual(_normalize_user_name('  Mus  musculus  '), 'Mus_musculus')
        self.assertEqual(_normalize_user_name('Loxodonta\tafricana'), 'Loxodonta_africana')

    def test_extract_pretty_name(self):
        """Test extraction of pretty display names"""
        self.assertEqual(_extract_pretty_name('Homo_sapiens_HOMINIDAE_PRIMATES'), 'Homo sapiens')
        self.assertEqual(_extract_pretty_name('Mus_musculus_MURIDAE'), 'Mus musculus')
        self.assertEqual(_extract_pretty_name('Single'), 'Single')

if __name__ == "__main__":
    unittest.main()
