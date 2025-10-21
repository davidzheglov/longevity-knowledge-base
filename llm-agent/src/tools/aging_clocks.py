import pandas as pd
import os
from typing import Optional

def generate_horvath_gene_report(gene_symbol: str, csv_filename: str = "Horvath.csv", output_dir: str = ".") -> Optional[str]:
    if not os.path.isabs(csv_filename):
        csv_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', csv_filename))
    df_horvath = pd.read_csv(csv_filename)
    df_horvath['Symbol'] = df_horvath['Symbol'].astype(str).str.split(';').str[0].str.strip()
    positive_cpgs = df_horvath[df_horvath['CoefficientTraining'] > 0].copy()
    negative_cpgs = df_horvath[df_horvath['CoefficientTraining'] < 0].copy()
    positive_cpgs = positive_cpgs.sort_values('CoefficientTraining', ascending=False).reset_index(drop=True)
    negative_cpgs = negative_cpgs.sort_values('CoefficientTraining', ascending=True).reset_index(drop=True)
    df_horvath['Abs_Coefficient'] = df_horvath['CoefficientTraining'].abs()
    all_cpgs_ranked = df_horvath.sort_values('Abs_Coefficient', ascending=False).reset_index(drop=True)
    gene_cpgs = df_horvath[df_horvath['Symbol'] == gene_symbol]
    report_lines = []
    report_lines.append(f"Horvath Epigenetic Clock Gene Report")
    report_lines.append(f"Gene Symbol: {gene_symbol}")
    if gene_cpgs.empty:
        report_lines.append(f"The gene '{gene_symbol}' was not found in the Horvath model.")
    else:
        report_lines.append(f"The gene '{gene_symbol}' is associated with {len(gene_cpgs)} CpG site(s).")
        for _, row in gene_cpgs.iterrows():
            cpg_id = row['CpGmarker']
            coefficient = row['CoefficientTraining']
            effect = "increases" if coefficient > 0 else "decreases"
            all_rank = all_cpgs_ranked[all_cpgs_ranked['CpGmarker'] == cpg_id].index[0] + 1
            if coefficient > 0:
                group_rank = positive_cpgs[positive_cpgs['CpGmarker'] == cpg_id].index[0] + 1
                group_total = len(positive_cpgs)
            else:
                group_rank = negative_cpgs[negative_cpgs['CpGmarker'] == cpg_id].index[0] + 1
                group_total = len(negative_cpgs)
            report_lines.append(f"- CpG site: {cpg_id}")
            report_lines.append(f"  Coefficient: {coefficient:.4f}")
            report_lines.append(f"  Effect: {effect} predicted age.")
            report_lines.append(f"  Rank: #{all_rank} of 353 (abs strength), #{group_rank} of {group_total} in group.")
    output_filename = f"Horvath_Report_{gene_symbol}.txt"
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w') as f:
        f.write("\n".join(report_lines))
    return output_path

def generate_phenoage_gene_report(gene_symbol: str, csv_filename: str = "PhenoAge.csv", output_dir: str = ".") -> Optional[str]:
    if not os.path.isabs(csv_filename):
        csv_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', csv_filename))
    df_pheno = pd.read_csv(csv_filename)
    symbol_col = 'Gene Symbol' if 'Gene Symbol' in df_pheno.columns else 'Symbol'
    df_pheno[symbol_col] = df_pheno[symbol_col].astype(str).str.split(';').str[0].str.strip()
    positive_cpgs = df_pheno[df_pheno['CoefficientTraining'] > 0].copy()
    negative_cpgs = df_pheno[df_pheno['CoefficientTraining'] < 0].copy()
    positive_cpgs = positive_cpgs.sort_values('CoefficientTraining', ascending=False).reset_index(drop=True)
    negative_cpgs = negative_cpgs.sort_values('CoefficientTraining', ascending=True).reset_index(drop=True)
    df_pheno['Abs_Coefficient'] = df_pheno['CoefficientTraining'].abs()
    all_cpgs_ranked = df_pheno.sort_values('Abs_Coefficient', ascending=False).reset_index(drop=True)
    gene_cpgs = df_pheno[df_pheno[symbol_col] == gene_symbol]
    report_lines = []
    report_lines.append(f"DNAm PhenoAge Epigenetic Clock Gene Report")
    report_lines.append(f"Gene Symbol: {gene_symbol}")
    if gene_cpgs.empty:
        report_lines.append(f"The gene '{gene_symbol}' was not found in the PhenoAge model.")
    else:
        report_lines.append(f"The gene '{gene_symbol}' is associated with {len(gene_cpgs)} CpG site(s).")
        for _, row in gene_cpgs.iterrows():
            cpg_id = row['CpGmarker']
            coefficient = row['CoefficientTraining']
            effect = "increases" if coefficient > 0 else "decreases"
            all_rank = all_cpgs_ranked[all_cpgs_ranked['CpGmarker'] == cpg_id].index[0] + 1
            if coefficient > 0:
                group_rank = positive_cpgs[positive_cpgs['CpGmarker'] == cpg_id].index[0] + 1
                group_total = len(positive_cpgs)
            else:
                group_rank = negative_cpgs[negative_cpgs['CpGmarker'] == cpg_id].index[0] + 1
                group_total = len(negative_cpgs)
            report_lines.append(f"- CpG site: {cpg_id}")
            report_lines.append(f"  Coefficient: {coefficient:.4f}")
            report_lines.append(f"  Effect: {effect} predicted phenotypic age.")
            report_lines.append(f"  Rank: #{all_rank} of 513 (abs strength), #{group_rank} of {group_total} in group.")
    output_filename = f"PhenoAge_Report_{gene_symbol}.txt"
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w') as f:
        f.write("\n".join(report_lines))
    return output_path
