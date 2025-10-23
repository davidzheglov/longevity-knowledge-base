"""
Unit tests for Brunet aging clocks module
"""

import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.brunet_clocks import generate_brunet_gene_report
from tools.gene_normalization import initialize_gene_map


@pytest.fixture(scope="session", autouse=True)
def init_gene_map():
    """Initialize gene map once for all tests"""
    initialize_gene_map()


class TestBrunetClocks:
    """Test suite for Brunet aging clock functions"""
    
    def test_generate_report_basic(self):
        """Test basic report generation for a known gene"""
        result = generate_brunet_gene_report("SPP1")
        
        assert result is not None
        assert 'canonical_symbol' in result
        assert result['canonical_symbol'] == 'SPP1'
        assert 'report_file' in result
        assert os.path.exists(result['report_file'])
        assert 'results' in result
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_with_gene_alias(self):
        """Test report generation using a gene alias"""
        result = generate_brunet_gene_report("p53")
        
        assert result is not None
        assert result['canonical_symbol'] == 'TP53'
        assert result['gene_query'] == 'p53'
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_with_entrez_id(self):
        """Test report generation using Entrez ID"""
        result = generate_brunet_gene_report("7157")  # TP53
        
        assert result is not None
        assert result['canonical_symbol'] == 'TP53'
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_invalid_gene(self):
        """Test handling of invalid gene name"""
        result = generate_brunet_gene_report("NOTAREALGENE123")
        
        assert result is not None
        assert result['canonical_symbol'] is None
        assert result['gene_query'] == "NOTAREALGENE123"
        assert 'report_file' in result
        assert os.path.exists(result['report_file'])
        
        # Check report content
        with open(result['report_file'], 'r') as f:
            content = f.read()
            assert "not recognized" in content.lower()
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_all_cell_types_present(self):
        """Test that results include all expected cell types"""
        result = generate_brunet_gene_report("APOE")
        
        expected_cells = [
            'Oligodendro',
            'Microglia',
            'Endothelial',
            'Astrocyte_qNSC',
            'aNSC_NPC',
            'Neuroblast'
        ]
        
        for cell in expected_cells:
            assert cell in result['results']
            assert 'chronological' in result['results'][cell]
            assert 'biological' in result['results'][cell]
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_output_directory(self):
        """Test that reports are saved to custom output directory"""
        test_dir = "test_brunet_output"
        os.makedirs(test_dir, exist_ok=True)
        
        try:
            result = generate_brunet_gene_report("APOE", output_dir=test_dir)
            
            assert result['report_file'].startswith(test_dir)
            assert os.path.exists(result['report_file'])
            
        finally:
            # Clean up
            if os.path.exists(result['report_file']):
                os.remove(result['report_file'])
            if os.path.exists(test_dir):
                os.rmdir(test_dir)
    
    def test_report_file_content(self):
        """Test that report file contains expected sections"""
        result = generate_brunet_gene_report("APOE")
        
        with open(result['report_file'], 'r') as f:
            content = f.read()
        
        # Check for key sections
        assert "Brunet Aging Clock Report" in content
        assert "Canonical symbol: APOE" in content
        assert "Oligodendrocytes:" in content
        assert "Microglia:" in content
        assert "Chronological:" in content
        assert "Biological:" in content
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_gene_not_in_model(self):
        """Test gene that might not be in all cell types"""
        # Use a gene that exists but might not be in all models
        result = generate_brunet_gene_report("TTN")  # Titin - muscle-specific
        
        assert result is not None
        assert result['canonical_symbol'] == 'TTN'
        
        # Check that we get "Not involved" messages for some cell types
        has_not_involved = False
        for cell_type in result['results'].values():
            if "Not involved" in cell_type['chronological'] or "Not involved" in cell_type['biological']:
                has_not_involved = True
                break
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_coefficient_format(self):
        """Test that coefficients are properly formatted in results"""
        result = generate_brunet_gene_report("APOE")
        
        # Check for at least one cell type with data
        found_coefficient = False
        for cell_type, data in result['results'].items():
            chrono = data['chronological']
            bio = data['biological']
            
            # If gene is present, check coefficient format
            if "Not involved" not in chrono:
                found_coefficient = True
                assert ("accelerating" in chrono or "decelerating" in chrono)
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_multiple_genes_sequential(self):
        """Test generating reports for multiple genes sequentially"""
        genes = ["APOE", "APP", "MAPT"]
        results = []
        
        try:
            for gene in genes:
                result = generate_brunet_gene_report(gene)
                results.append(result)
                assert result['canonical_symbol'] == gene
                assert os.path.exists(result['report_file'])
        
        finally:
            # Clean up all reports
            for result in results:
                if os.path.exists(result['report_file']):
                    os.remove(result['report_file'])
    
    def test_case_insensitive_gene_query(self):
        """Test that gene queries are case-insensitive"""
        result1 = generate_brunet_gene_report("apoe")
        result2 = generate_brunet_gene_report("APOE")
        result3 = generate_brunet_gene_report("Apoe")
        
        assert result1['canonical_symbol'] == result2['canonical_symbol'] == result3['canonical_symbol']
        
        # Clean up
        for result in [result1, result2, result3]:
            if os.path.exists(result['report_file']):
                os.remove(result['report_file'])
    
    def test_return_structure(self):
        """Test that return dictionary has expected structure"""
        result = generate_brunet_gene_report("APOE")
        
        # Check top-level keys
        assert isinstance(result, dict)
        assert 'gene_query' in result
        assert 'canonical_symbol' in result
        assert 'report_file' in result
        assert 'results' in result
        
        # Check results structure
        assert isinstance(result['results'], dict)
        for cell_type, data in result['results'].items():
            assert isinstance(data, dict)
            assert 'chronological' in data
            assert 'biological' in data
            assert isinstance(data['chronological'], str)
            assert isinstance(data['biological'], str)
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_data_files_exist(self):
        """Test that required data files are accessible"""
        from tools.brunet_clocks import CHRONOLOGICAL_FILE, BIOLOGICAL_FILE
        
        assert os.path.exists(CHRONOLOGICAL_FILE), f"Chronological data file not found: {CHRONOLOGICAL_FILE}"
        assert os.path.exists(BIOLOGICAL_FILE), f"Biological data file not found: {BIOLOGICAL_FILE}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
