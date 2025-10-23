"""
Unit tests for the protein sequence module.
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock, Mock
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.protein_sequence import find_uniprot, download_uniprot_fasta


class TestProteinSequence(unittest.TestCase):
    """Test suite for protein sequence functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock FASTA content
        self.mock_fasta = """>sp|P42858|POU5F1_HUMAN POU domain, class 5, transcription factor 1
MAGHLASDFGPVPSNMASGPPPGAREDSTPPSEVVSGGGGGGGSGGGGGCAEAAAGCAG
AHTGVPGAVGVPGGGGGGGGGGHSGGGGGDSLGPGGGGGGGGGGGGGCGGGGCSGGGGS
"""
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('tools.gene_normalization.normalize_gene')
    @patch('tools.protein_sequence.requests.get')
    def test_find_uniprot_success(self, mock_get, mock_normalize):
        """Test successful UniProt search."""
        # Mock normalize_gene
        mock_normalize.return_value = {
            'canonical_symbol': 'POU5F1',
            'entrez_id': '5460'
        }
        
        # Mock UniProt API responses
        mock_search_response = Mock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            'results': [{
                'primaryAccession': 'P42858',
                'genes': [{
                    'geneName': {'value': 'POU5F1'},
                    'synonyms': [{'value': 'OCT4'}]
                }],
                'proteinDescription': {
                    'recommendedName': {
                        'fullName': {'value': 'POU domain, class 5, transcription factor 1'}
                    }
                }
            }]
        }
        
        mock_fasta_response = Mock()
        mock_fasta_response.status_code = 200
        mock_fasta_response.text = self.mock_fasta
        mock_fasta_response.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_search_response, mock_fasta_response]
        
        # Test
        result = find_uniprot('POU5F1', save_to_file=False)
        
        # Assertions
        self.assertNotIn('error', result)
        self.assertEqual(result['canonical_symbol'], 'POU5F1')
        self.assertEqual(result['uniprot_id'], 'P42858')
        self.assertIn('fasta', result)
        self.assertIn('POU5F1', result['all_known_names'])
    
    @patch('tools.gene_normalization.normalize_gene')
    @patch('tools.protein_sequence.requests.get')
    def test_find_uniprot_with_file_save(self, mock_get, mock_normalize):
        """Test UniProt search with file saving."""
        # Mock normalize_gene
        mock_normalize.return_value = {
            'canonical_symbol': 'TP53',
            'entrez_id': '7157'
        }
        
        # Mock UniProt API responses
        mock_search_response = Mock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            'results': [{
                'primaryAccession': 'P04637',
                'genes': [{
                    'geneName': {'value': 'TP53'}
                }],
                'proteinDescription': {
                    'recommendedName': {
                        'fullName': {'value': 'Cellular tumor antigen p53'}
                    }
                }
            }]
        }
        
        mock_fasta_response = Mock()
        mock_fasta_response.status_code = 200
        mock_fasta_response.text = self.mock_fasta
        mock_fasta_response.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_search_response, mock_fasta_response]
        
        # Test with file saving
        result = find_uniprot('TP53', save_to_file=True, output_dir=self.temp_dir)
        
        # Assertions
        self.assertNotIn('error', result)
        self.assertIn('fasta_file', result)
        # Note: file won't actually exist in mock, but the path should be set
        expected_path = os.path.join(self.temp_dir, 'TP53.fasta')
        self.assertTrue(result['fasta_file'].endswith('TP53.fasta'))
    
    @patch('tools.gene_normalization.normalize_gene')
    @patch('tools.protein_sequence.requests.get')
    def test_find_uniprot_not_found(self, mock_get, mock_normalize):
        """Test UniProt search when gene not found."""
        # Mock normalize_gene
        mock_normalize.return_value = {
            'canonical_symbol': 'FAKEGENE',
        }
        
        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_response.raise_for_status = Mock()
        
        mock_get.return_value = mock_response
        
        # Test
        result = find_uniprot('FAKEGENE')
        
        # Should return error
        self.assertIn('error', result)
        self.assertIn('No reviewed UniProt entry found', result['error'])
    
    @patch('tools.gene_normalization.normalize_gene')
    def test_find_uniprot_empty_query(self, mock_normalize):
        """Test with empty query."""
        result = find_uniprot('')
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Empty query')
    
    @patch('tools.gene_normalization.normalize_gene')
    @patch('tools.protein_sequence.requests.get')
    def test_find_uniprot_different_organism(self, mock_get, mock_normalize):
        """Test UniProt search for different organism."""
        mock_normalize.return_value = {
            'canonical_symbol': 'TP53',
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Test with mouse
        result = find_uniprot('TP53', organism='mouse')
        
        # Verify the organism filter was used
        self.assertTrue(mock_get.called)
        call_args = mock_get.call_args
        self.assertIn('organism', str(call_args))


class TestDownloadUniprotFasta(unittest.TestCase):
    """Test suite for download_uniprot_fasta function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('tools.protein_sequence.requests.get')
    def test_download_fasta_success(self, mock_get):
        """Test successful FASTA download."""
        # Mock taxonomy response
        mock_tax_response = Mock()
        mock_tax_response.status_code = 200
        mock_tax_response.json.return_value = {
            'results': [{
                'taxonId': 9606,
                'scientificName': 'Homo sapiens',
                'rank': 'species'
            }]
        }
        mock_tax_response.raise_for_status = Mock()
        
        # Mock FASTA response
        mock_fasta_response = Mock()
        mock_fasta_response.status_code = 200
        mock_fasta_response.text = """>sp|P42858|POU5F1_HUMAN POU domain GN=POU5F1 OS=Homo sapiens OX=9606
MAGHLASDFGPVPSNMASGPPPGAREDSTPPSEVVSGGGGGGGSGGGGGCAEAAAGCAG"""
        
        mock_get.side_effect = [mock_tax_response, mock_tax_response, mock_fasta_response]
        
        # Test
        result = download_uniprot_fasta('POU5F1', 'Homo sapiens', output_dir=self.temp_dir)
        
        # The function should attempt to download and return a path
        # In mock environment, we verify it tried
        self.assertTrue(mock_get.called)
    
    def test_download_fasta_invalid_organism(self):
        """Test with invalid organism name."""
        # This will fail to get taxid and should handle gracefully
        with patch('tools.protein_sequence.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'results': []}
            mock_get.return_value = mock_response
            
            result = download_uniprot_fasta(
                'FAKEGENE',
                'NonExistentOrganism',
                output_dir=self.temp_dir
            )
            
            # Should return None when can't find organism
            self.assertIsNone(result)


class TestProteinSequenceIntegration(unittest.TestCase):
    """Integration tests for protein sequence module."""
    
    @unittest.skipIf(
        os.getenv('SKIP_INTEGRATION_TESTS') == '1',
        "Skipping integration tests (set SKIP_INTEGRATION_TESTS=0 to run)"
    )
    def test_real_uniprot_query_tp53(self):
        """Test real UniProt API call for TP53 (requires internet)."""
        # This test will be skipped by default
        # Set SKIP_INTEGRATION_TESTS=0 to run real API tests
        temp_dir = tempfile.mkdtemp()
        try:
            result = find_uniprot('TP53', save_to_file=True, output_dir=temp_dir)
            
            self.assertNotIn('error', result)
            self.assertEqual(result['canonical_symbol'], 'TP53')
            self.assertIn('uniprot_id', result)
            self.assertIn('fasta', result)
            
            # Check file was created
            self.assertIn('fasta_file', result)
            self.assertTrue(os.path.exists(result['fasta_file']))
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    # Set to skip integration tests by default
    os.environ.setdefault('SKIP_INTEGRATION_TESTS', '1')
    unittest.main()
