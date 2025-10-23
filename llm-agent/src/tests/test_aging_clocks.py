import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.aging_clocks import generate_horvath_gene_report, generate_phenoage_gene_report

class TestAgingClocks(unittest.TestCase):
    def test_generate_horvath_gene_report_basic(self):
        """Test basic Horvath report generation"""
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Horvath.csv'))
        output = generate_horvath_gene_report('NPPB', csv_filename=data_path)
        self.assertTrue(os.path.exists(output))
        self.assertTrue(output.endswith('Horvath_Report_NPPB.txt'))
        # Verify content exists
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn('Horvath', content)
            self.assertIn('NPPB', content)
        if os.path.exists(output):
            os.remove(output)

    def test_generate_horvath_gene_report_multiple_genes(self):
        """Test Horvath reports for multiple genes"""
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Horvath.csv'))
        genes = ['REEP1', 'CXADR']
        outputs = []
        try:
            for gene in genes:
                output = generate_horvath_gene_report(gene, csv_filename=data_path)
                self.assertTrue(os.path.exists(output))
                outputs.append(output)
        finally:
            for output in outputs:
                if os.path.exists(output):
                    os.remove(output)

    def test_generate_horvath_gene_report_not_found(self):
        """Test Horvath report when gene is not in the model"""
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Horvath.csv'))
        output = generate_horvath_gene_report('NONEXISTENTGENE123', csv_filename=data_path)
        self.assertTrue(os.path.exists(output))
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn('not found', content.lower())
        if os.path.exists(output):
            os.remove(output)

    def test_generate_phenoage_gene_report_basic(self):
        """Test basic PhenoAge report generation"""
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'PhenoAge.csv'))
        output = generate_phenoage_gene_report('OXSM', csv_filename=data_path)
        self.assertTrue(os.path.exists(output))
        self.assertTrue(output.endswith('PhenoAge_Report_OXSM.txt'))
        # Verify content
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn('PhenoAge', content)
            self.assertIn('OXSM', content)
        if os.path.exists(output):
            os.remove(output)

    def test_generate_phenoage_gene_report_multiple_genes(self):
        """Test PhenoAge reports for multiple genes"""
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'PhenoAge.csv'))
        genes = ['SLC44A1', 'HSPA2']
        outputs = []
        try:
            for gene in genes:
                output = generate_phenoage_gene_report(gene, csv_filename=data_path)
                self.assertTrue(os.path.exists(output))
                outputs.append(output)
        finally:
            for output in outputs:
                if os.path.exists(output):
                    os.remove(output)

    def test_generate_phenoage_gene_report_not_found(self):
        """Test PhenoAge report when gene is not in the model"""
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'PhenoAge.csv'))
        output = generate_phenoage_gene_report('NONEXISTENTGENE456', csv_filename=data_path)
        self.assertTrue(os.path.exists(output))
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn('not found', content.lower())
        if os.path.exists(output):
            os.remove(output)

    def test_generate_horvath_gene_report_custom_output_dir(self):
        """Test Horvath report with custom output directory"""
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Horvath.csv'))
        output_dir = 'test_output'
        os.makedirs(output_dir, exist_ok=True)
        try:
            output = generate_horvath_gene_report('NPPB', csv_filename=data_path, output_dir=output_dir)
            self.assertTrue(os.path.exists(output))
            self.assertTrue(output.startswith(output_dir))
        finally:
            if os.path.exists(output):
                os.remove(output)
            if os.path.exists(output_dir):
                os.rmdir(output_dir)

    def test_generate_phenoage_gene_report_custom_output_dir(self):
        """Test PhenoAge report with custom output directory"""
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'PhenoAge.csv'))
        output_dir = 'test_output2'
        os.makedirs(output_dir, exist_ok=True)
        try:
            output = generate_phenoage_gene_report('OXSM', csv_filename=data_path, output_dir=output_dir)
            self.assertTrue(os.path.exists(output))
            self.assertTrue(output.startswith(output_dir))
        finally:
            if os.path.exists(output):
                os.remove(output)
            if os.path.exists(output_dir):
                os.rmdir(output_dir)

if __name__ == "__main__":
    unittest.main()
