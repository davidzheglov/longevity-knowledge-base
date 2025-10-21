"""
Unit tests for the gene normalization module.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.gene_normalization import (
    build_gene_alias_map,
    normalize_gene,
    initialize_gene_map,
    GENE_ALIAS_MAP
)


class TestGeneNormalization(unittest.TestCase):
    """Test suite for gene normalization functions."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures - create a mock gene_info.txt file."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.gene_info_path = os.path.join(cls.temp_dir, 'gene_info.txt')
        
        # Create mock gene info file
        mock_data = """symbol\tsynonyms\tentrez_id\ttype\thgnc_id\tensembl_id
POU5F1\tOCT3|OCT4|OCT3/4|OTF3\t5460\tprotein-coding\tHGNC:9221\tENSG00000204531
TP53\tp53|P53|TRP53\t7157\tprotein-coding\tHGNC:11998\tENSG00000141510
MYCN\tN-MYC|NMYC|bHLHe37\t4613\tprotein-coding\tHGNC:7559\tENSG00000134323
SPP1\tOPN|BNSP|BSSP\t6696\tprotein-coding\tHGNC:11255\tENSG00000118785
APOE\tAD2|LPG|ApoE4\t348\tprotein-coding\tHGNC:613\tENSG00000130203"""
        
        with open(cls.gene_info_path, 'w') as f:
            f.write(mock_data)
        
        # Initialize the gene map
        initialize_gene_map(cls.gene_info_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(cls.temp_dir)
    
    def test_build_gene_alias_map(self):
        """Test building the gene alias map."""
        alias_map = build_gene_alias_map(self.gene_info_path)
        
        # Check that map is not empty
        self.assertGreater(len(alias_map), 0)
        
        # Check that canonical symbols are in the map
        self.assertIn('POU5F1', alias_map)
        self.assertIn('TP53', alias_map)
        
        # Check that normalized versions are in the map
        self.assertIn('POU5F1', alias_map)
        self.assertIn('OCT4', alias_map)
    
    def test_normalize_gene_canonical_symbol(self):
        """Test normalization with canonical gene symbol."""
        result = normalize_gene('POU5F1')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['canonical_symbol'], 'POU5F1')
        self.assertEqual(result['entrez_id'], '5460')
        self.assertEqual(result['type'], 'protein-coding')
        self.assertIn('OCT4', result['all_names'])
    
    def test_normalize_gene_alias(self):
        """Test normalization with gene alias."""
        result = normalize_gene('OCT4')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['canonical_symbol'], 'POU5F1')
        self.assertEqual(result['query'], 'OCT4')
    
    def test_normalize_gene_with_special_chars(self):
        """Test normalization with special characters."""
        result = normalize_gene('OCT3/4')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['canonical_symbol'], 'POU5F1')
    
    def test_normalize_gene_case_insensitive(self):
        """Test that normalization is case-insensitive."""
        result1 = normalize_gene('oct4')
        result2 = normalize_gene('OCT4')
        result3 = normalize_gene('Oct4')
        
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertIsNotNone(result3)
        
        self.assertEqual(result1['canonical_symbol'], result2['canonical_symbol'])
        self.assertEqual(result2['canonical_symbol'], result3['canonical_symbol'])
    
    def test_normalize_gene_by_entrez_id(self):
        """Test normalization by Entrez ID."""
        result = normalize_gene('5460')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['canonical_symbol'], 'POU5F1')
        self.assertEqual(result['entrez_id'], '5460')
    
    def test_normalize_gene_p53_alias(self):
        """Test normalization of p53 variants."""
        result = normalize_gene('p53')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['canonical_symbol'], 'TP53')
    
    def test_normalize_gene_with_hyphen(self):
        """Test normalization with hyphenated names."""
        result = normalize_gene('N-MYC')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['canonical_symbol'], 'MYCN')
    
    def test_normalize_gene_not_found(self):
        """Test normalization with non-existent gene."""
        result = normalize_gene('FAKEGENE123')
        
        self.assertIsNone(result)
    
    def test_normalize_gene_empty_string(self):
        """Test normalization with empty string."""
        result = normalize_gene('')
        
        self.assertIsNone(result)
    
    def test_normalize_gene_none(self):
        """Test normalization with None."""
        result = normalize_gene(None)
        
        self.assertIsNone(result)
    
    def test_normalize_gene_whitespace(self):
        """Test normalization with whitespace."""
        result = normalize_gene('  POU5F1  ')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['canonical_symbol'], 'POU5F1')
    
    def test_gene_map_not_initialized_error(self):
        """Test that using normalize_gene without initialization raises error."""
        import tools.gene_normalization as gn
        
        # Save current state
        saved_map = gn.GENE_ALIAS_MAP
        
        # Set to None to simulate uninitialized state
        gn.GENE_ALIAS_MAP = None
        
        with self.assertRaises(RuntimeError):
            normalize_gene('TP53')
        
        # Restore state
        gn.GENE_ALIAS_MAP = saved_map


class TestGeneNormalizationIntegration(unittest.TestCase):
    """Integration tests for gene normalization."""
    
    def setUp(self):
        """Set up for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.gene_info_path = os.path.join(self.temp_dir, 'gene_info.txt')
        
        # Create more comprehensive mock data
        mock_data = """symbol\tsynonyms\tentrez_id\ttype\thgnc_id\tensembl_id
POU5F1\tOCT3|OCT4|OCT3/4|OTF3\t5460\tprotein-coding\tHGNC:9221\tENSG00000204531
TP53\tp53|P53|TRP53\t7157\tprotein-coding\tHGNC:11998\tENSG00000141510"""
        
        with open(self.gene_info_path, 'w') as f:
            f.write(mock_data)
        
        initialize_gene_map(self.gene_info_path)
    
    def tearDown(self):
        """Clean up after each test."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_multiple_aliases_same_gene(self):
        """Test that multiple aliases resolve to the same gene."""
        aliases = ['POU5F1', 'OCT4', 'OCT3', 'OTF3', 'oct4', 'Oct-4']
        results = [normalize_gene(alias) for alias in aliases]
        
        # Filter out None results
        valid_results = [r for r in results if r is not None]
        
        # All should resolve to POU5F1
        self.assertTrue(all(r['canonical_symbol'] == 'POU5F1' for r in valid_results))
    
    def test_ensembl_id_present(self):
        """Test that Ensembl IDs are properly stored."""
        result = normalize_gene('POU5F1')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['ensembl_id'], 'ENSG00000204531')


if __name__ == '__main__':
    unittest.main()
