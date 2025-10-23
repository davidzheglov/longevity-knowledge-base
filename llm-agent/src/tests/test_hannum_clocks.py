"""
Unit tests for Hannum aging clocks module
"""

import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.hannum_clocks import generate_hannum_gene_report
from tools.gene_normalization import initialize_gene_map


@pytest.fixture(scope="session", autouse=True)
def init_gene_map():
    """Initialize gene map once for all tests"""
    initialize_gene_map()


class TestHannumClocks:
    """Test suite for Hannum aging clock functions"""
    
    def test_generate_report_basic(self):
        """Test basic report generation for a known gene"""
        result = generate_hannum_gene_report("ELOVL2")
        
        assert result is not None
        assert 'canonical_symbol' in result
        assert result['canonical_symbol'] == 'ELOVL2'
        assert 'report_file' in result
        assert os.path.exists(result['report_file'])
        assert 'cpg_models' in result
        assert 'transcription' in result
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_with_gene_alias(self):
        """Test report generation using a gene alias"""
        result = generate_hannum_gene_report("p53")
        
        assert result is not None
        assert result['canonical_symbol'] == 'TP53'
        assert result['gene_query'] == 'p53'
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_with_entrez_id(self):
        """Test report generation using Entrez ID"""
        result = generate_hannum_gene_report("54898")  # ELOVL2
        
        assert result is not None
        assert result['canonical_symbol'] == 'ELOVL2'
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_invalid_gene(self):
        """Test handling of invalid gene name"""
        result = generate_hannum_gene_report("NOTAREALGENE456")
        
        assert result is not None
        assert result['canonical_symbol'] is None
        assert result['gene_query'] == "NOTAREALGENE456"
        assert 'report_file' in result
        assert os.path.exists(result['report_file'])
        
        # Check report content
        with open(result['report_file'], 'r', encoding='utf-8') as f:
            content = f.read()
            assert "not recognized" in content.lower()
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_all_models_present(self):
        """Test that results include all expected CpG models"""
        result = generate_hannum_gene_report("FHL2")
        
        expected_models = ['Blood', 'Breast', 'Kidney', 'Lung']
        
        for model in expected_models:
            assert model in result['cpg_models']
            assert 'present' in result['cpg_models'][model]
            assert 'total' in result['cpg_models'][model]
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_transcription_model(self):
        """Test that transcription model is included"""
        result = generate_hannum_gene_report("ELOVL2")
        
        assert 'transcription' in result
        # Transcription result can be None or a dict
        if result['transcription'] is not None:
            assert 'coefficient' in result['transcription']
            assert 'effect' in result['transcription']
            assert 'rank' in result['transcription']
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_cpg_site_structure(self):
        """Test structure of CpG site data"""
        result = generate_hannum_gene_report("ELOVL2")
        
        # Find a model where the gene is present
        for model_name, model_data in result['cpg_models'].items():
            if model_data['present']:
                assert 'sites' in model_data
                assert 'positive' in model_data
                assert 'negative' in model_data
                
                # Check site structure
                if len(model_data['sites']) > 0:
                    site = model_data['sites'][0]
                    assert 'cpg' in site
                    assert 'coefficient' in site
                    assert 'effect' in site
                    assert 'rank' in site
                    assert 'total' in site
                
                break
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_cross_tissue_analysis(self):
        """Test cross-tissue analysis structure"""
        result = generate_hannum_gene_report("ELOVL2")
        
        assert 'cross_tissue' in result
        assert 'shared' in result['cross_tissue']
        assert 'unique' in result['cross_tissue']
        
        # Check structure of shared sites
        if len(result['cross_tissue']['shared']) > 0:
            shared = result['cross_tissue']['shared'][0]
            assert 'cpg' in shared
            assert 'models' in shared
            assert isinstance(shared['models'], list)
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_output_directory(self):
        """Test that reports are saved to custom output directory"""
        test_dir = "test_hannum_output"
        os.makedirs(test_dir, exist_ok=True)
        
        try:
            result = generate_hannum_gene_report("ELOVL2", output_dir=test_dir)
            
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
        result = generate_hannum_gene_report("ELOVL2")
        
        with open(result['report_file'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key sections
        assert "Hannum Epigenetic Aging Clock Report" in content
        assert "Canonical symbol: ELOVL2" in content
        assert "CpG METHYLATION MODELS" in content
        assert "Blood:" in content
        assert "TRANSCRIPTION" in content
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_gene_not_in_model(self):
        """Test gene that might not be in all models"""
        result = generate_hannum_gene_report("APOE")
        
        assert result is not None
        assert result['canonical_symbol'] == 'APOE'
        
        # Check that some models might not have the gene
        has_not_present = False
        for model_name, model_data in result['cpg_models'].items():
            if not model_data['present']:
                has_not_present = True
                assert model_data['total'] == 0
                assert len(model_data['sites']) == 0
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_hypermethylation_detection(self):
        """Test detection of hypermethylation vs hypomethylation"""
        result = generate_hannum_gene_report("ELOVL2")
        
        # Check that positive/negative counts are tracked
        found_data = False
        for model_name, model_data in result['cpg_models'].items():
            if model_data['present']:
                found_data = True
                assert model_data['positive'] + model_data['negative'] == model_data['total']
                
                # Check that sites have proper effect labels
                for site in model_data['sites']:
                    if site['coefficient'] > 0:
                        assert "hypermethylation" in site['effect']
                    else:
                        assert "hypomethylation" in site['effect']
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_multiple_genes_sequential(self):
        """Test generating reports for multiple genes sequentially"""
        genes = ["ELOVL2", "FHL2", "PENK"]
        results = []
        
        try:
            for gene in genes:
                result = generate_hannum_gene_report(gene)
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
        result1 = generate_hannum_gene_report("elovl2")
        result2 = generate_hannum_gene_report("ELOVL2")
        result3 = generate_hannum_gene_report("Elovl2")
        
        assert result1['canonical_symbol'] == result2['canonical_symbol'] == result3['canonical_symbol']
        
        # Clean up
        for result in [result1, result2, result3]:
            if os.path.exists(result['report_file']):
                os.remove(result['report_file'])
    
    def test_return_structure(self):
        """Test that return dictionary has expected structure"""
        result = generate_hannum_gene_report("ELOVL2")
        
        # Check top-level keys
        assert isinstance(result, dict)
        assert 'gene_query' in result
        assert 'canonical_symbol' in result
        assert 'report_file' in result
        assert 'cpg_models' in result
        assert 'transcription' in result
        assert 'cross_tissue' in result
        
        # Check cpg_models structure
        assert isinstance(result['cpg_models'], dict)
        for model_name, model_data in result['cpg_models'].items():
            assert isinstance(model_data, dict)
            assert 'present' in model_data
            assert isinstance(model_data['present'], bool)
        
        # Clean up
        if os.path.exists(result['report_file']):
            os.remove(result['report_file'])
    
    def test_data_files_exist(self):
        """Test that required data files are accessible"""
        from tools.hannum_clocks import (
            BLOOD_FILE, BREAST_FILE, KIDNEY_FILE, 
            LUNG_FILE, TRANSCRIPTION_FILE
        )
        
        assert os.path.exists(BLOOD_FILE), f"Blood data file not found: {BLOOD_FILE}"
        assert os.path.exists(BREAST_FILE), f"Breast data file not found: {BREAST_FILE}"
        assert os.path.exists(KIDNEY_FILE), f"Kidney data file not found: {KIDNEY_FILE}"
        assert os.path.exists(LUNG_FILE), f"Lung data file not found: {LUNG_FILE}"
        assert os.path.exists(TRANSCRIPTION_FILE), f"Transcription data file not found: {TRANSCRIPTION_FILE}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
