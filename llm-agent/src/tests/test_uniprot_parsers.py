import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.uniprot_parsers import get_reactome_pathways, get_go_annotation, get_drug_info

class TestUniprotParsers(unittest.TestCase):
    def test_get_reactome_pathways_basic(self):
        """Test basic Reactome pathways retrieval"""
        pathways = get_reactome_pathways('TP53', verbose=False)
        self.assertIsInstance(pathways, list)
        if pathways:
            self.assertIn('id', pathways[0])
            self.assertIn('name', pathways[0])
        # Clean up report file
        if os.path.exists('TP53_Reactome.txt'):
            os.remove('TP53_Reactome.txt')

    def test_get_reactome_pathways_with_alias(self):
        """Test Reactome with gene alias"""
        pathways = get_reactome_pathways('p53', verbose=False)
        self.assertIsInstance(pathways, list)
        if os.path.exists('TP53_Reactome.txt'):
            os.remove('TP53_Reactome.txt')

    def test_get_reactome_pathways_empty_query(self):
        """Test Reactome with empty query"""
        pathways = get_reactome_pathways('', verbose=False)
        self.assertEqual(pathways, [])

    def test_get_reactome_pathways_invalid_gene(self):
        """Test Reactome with invalid gene"""
        pathways = get_reactome_pathways('NONEXISTENTGENE12345', verbose=False)
        self.assertEqual(pathways, [])

    def test_get_reactome_pathways_no_save(self):
        """Test Reactome without saving report"""
        pathways = get_reactome_pathways('TP53', save_report=False, verbose=False)
        self.assertIsInstance(pathways, list)
        self.assertFalse(os.path.exists('TP53_Reactome.txt'))

    def test_get_go_annotation_basic(self):
        """Test basic GO annotation retrieval"""
        go_entries = get_go_annotation('TP53', verbose=False)
        self.assertIsInstance(go_entries, list)
        if go_entries:
            self.assertIn('category', go_entries[0])
            self.assertIn('go_id', go_entries[0])
            self.assertIn('term', go_entries[0])
            self.assertIn('evidence', go_entries[0])
        # Clean up report file
        if os.path.exists('TP53_GO.txt'):
            os.remove('TP53_GO.txt')

    def test_get_go_annotation_with_alias(self):
        """Test GO annotation with gene alias"""
        go_entries = get_go_annotation('p53', verbose=False)
        self.assertIsInstance(go_entries, list)
        if os.path.exists('TP53_GO.txt'):
            os.remove('TP53_GO.txt')

    def test_get_go_annotation_empty_query(self):
        """Test GO annotation with empty query"""
        go_entries = get_go_annotation('', verbose=False)
        self.assertEqual(go_entries, [])

    def test_get_go_annotation_invalid_gene(self):
        """Test GO annotation with invalid gene"""
        go_entries = get_go_annotation('NONEXISTENTGENE12345', verbose=False)
        self.assertEqual(go_entries, [])

    def test_get_go_annotation_report_file_created(self):
        """Test that GO annotation creates report file"""
        go_entries = get_go_annotation('TP53', verbose=False)
        output_file = 'TP53_GO.txt'
        self.assertTrue(os.path.exists(output_file))
        # Verify content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('TP53', content)
            self.assertIn('UniProt Accession', content)
        if os.path.exists(output_file):
            os.remove(output_file)

    def test_get_drug_info_basic(self):
        """Test basic DrugBank info retrieval"""
        drugs = get_drug_info('EGFR', verbose=False)
        self.assertIsInstance(drugs, list)
        if drugs:
            self.assertIn('drugbank_id', drugs[0])
            self.assertIn('drug_name', drugs[0])
        # Clean up report file
        if os.path.exists('EGFR_Drugs.txt'):
            os.remove('EGFR_Drugs.txt')

    def test_get_drug_info_empty_query(self):
        """Test DrugBank with empty query"""
        drugs = get_drug_info('', verbose=False)
        self.assertEqual(drugs, [])

    def test_get_drug_info_invalid_gene(self):
        """Test DrugBank with invalid gene"""
        drugs = get_drug_info('NONEXISTENTGENE12345', verbose=False)
        self.assertEqual(drugs, [])

    def test_get_drug_info_report_file_created(self):
        """Test that DrugBank info creates report file"""
        drugs = get_drug_info('EGFR', verbose=False)
        output_file = 'EGFR_Drugs.txt'
        self.assertTrue(os.path.exists(output_file))
        # Verify content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('EGFR', content)
            self.assertIn('UniProt Accession', content)
        if os.path.exists(output_file):
            os.remove(output_file)

    def test_get_drug_info_gene_with_no_drugs(self):
        """Test gene that likely has no drug annotations"""
        drugs = get_drug_info('ZNF668', verbose=False)
        self.assertIsInstance(drugs, list)
        # Even if no drugs, should create report file
        if os.path.exists('ZNF668_Drugs.txt'):
            with open('ZNF668_Drugs.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                # Should indicate no drugs found
                self.assertTrue('No DrugBank annotations found' in content or 'DrugBank' in content)
            os.remove('ZNF668_Drugs.txt')

if __name__ == "__main__":
    unittest.main()
