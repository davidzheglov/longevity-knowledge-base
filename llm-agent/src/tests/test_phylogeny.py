import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.phylogeny import plot_mammalian_tree, _normalize_user_name, _extract_pretty_name

class TestPhylogeny(unittest.TestCase):
    def test_plot_mammalian_tree_basic(self):
        """Test basic tree plotting with two species"""
        species = ['Homo sapiens', 'Mus musculus']
        output_file = 'test_tree.png'
        try:
            result = plot_mammalian_tree(species, output_file)
            self.assertTrue(os.path.exists(result))
            self.assertEqual(result, output_file)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_plot_mammalian_tree_multiple_species(self):
        """Test tree plotting with multiple species"""
        species = ['Homo sapiens', 'Mus musculus', 'Rattus norvegicus', 'Sus scrofa']
        output_file = 'test_tree_multi.png'
        try:
            result = plot_mammalian_tree(species, output_file)
            self.assertTrue(os.path.exists(result))
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_plot_mammalian_tree_radial_layout(self):
        """Test tree plotting with radial layout"""
        species = ['Homo sapiens', 'Pan troglodytes', 'Gorilla gorilla']
        output_file = 'test_tree_radial.png'
        try:
            result = plot_mammalian_tree(species, output_file, layout='r')
            self.assertTrue(os.path.exists(result))
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_plot_mammalian_tree_rectangular_layout(self):
        """Test tree plotting with rectangular layout"""
        species = ['Homo sapiens', 'Mus musculus']
        output_file = 'test_tree_rect.png'
        try:
            result = plot_mammalian_tree(species, output_file, layout='u')
            self.assertTrue(os.path.exists(result))
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_plot_mammalian_tree_invalid_species(self):
        """Test that invalid species raises appropriate error"""
        species = ['NonExistentSpecies123']
        output_file = 'test_tree_invalid.png'
        try:
            with self.assertRaises(ValueError):
                plot_mammalian_tree(species, output_file)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_normalize_user_name(self):
        """Test normalization of user input names"""
        self.assertEqual(_normalize_user_name('Homo sapiens'), 'Homo_sapiens')
        self.assertEqual(_normalize_user_name('  Mus  musculus  '), 'Mus_musculus')
        self.assertEqual(_normalize_user_name('Rattus\tnorvegicus'), 'Rattus_norvegicus')

    def test_extract_pretty_name(self):
        """Test extraction of pretty display names"""
        self.assertEqual(_extract_pretty_name('Homo_sapiens_HOMINIDAE_PRIMATES'), 'Homo sapiens')
        self.assertEqual(_extract_pretty_name('Mus_musculus_MURIDAE'), 'Mus musculus')
        self.assertEqual(_extract_pretty_name('Single'), 'Single')

if __name__ == "__main__":
    unittest.main()
