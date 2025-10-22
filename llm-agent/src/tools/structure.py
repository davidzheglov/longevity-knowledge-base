"""
Structural analysis utilities:
- structural_alignment: RMSD-based superposition of two PDBs (optional save of aligned files)
- simple_stability_score / compare_stability_simple: crude hydrophobic/charge heuristic
- download_pdb_structures_for_protein: fetch experimental PDBs for a UniProt entry
- smart_visualize (optional): generates a lightweight HTML with 3Dmol.js if available
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple
import json
import requests

from Bio.PDB import PDBParser, Superimposer, PDBIO


def structural_alignment(
    pdb1_path: str,
    pdb2_path: str,
    save_aligned: bool = True,
    out1: str = "aligned_ref.pdb",
    out2: str = "aligned_mob.pdb",
) -> Tuple[float, Optional[str], Optional[str]]:
    """
    Align two structures by CA atoms; return (RMSD, out_ref, out_mob).
    Writes aligned PDBs if save_aligned is True.
    """
    p1, p2 = Path(pdb1_path), Path(pdb2_path)
    if not p1.is_file() or not p2.is_file():
        raise FileNotFoundError("Both pdb1_path and pdb2_path must exist")

    parser = PDBParser(QUIET=True)
    s1 = parser.get_structure("ref", str(p1))
    s2 = parser.get_structure("mob", str(p2))

    def get_ca(struct):
        atoms = []
        for model in struct:
            for chain in model:
                for res in chain:
                    if "CA" in res:
                        atoms.append(res["CA"])
        return atoms

    ca1 = get_ca(s1)
    ca2 = get_ca(s2)
    if not ca1 or not ca2:
        raise ValueError("No CA atoms found in one or both structures")

    n = min(len(ca1), len(ca2))
    ca1 = ca1[:n]
    ca2 = ca2[:n]

    sup = Superimposer()
    sup.set_atoms(ca1, ca2)
    rmsd = sup.rms
    rot, tran = sup.rotran
    s2.transform(rot, tran)

    out_ref = out_mob = None
    if save_aligned:
        io = PDBIO()
        io.set_structure(s1)
        io.save(out1)
        out_ref = str(Path(out1).resolve())
        io.set_structure(s2)
        io.save(out2)
        out_mob = str(Path(out2).resolve())

    return rmsd, out_ref, out_mob


# Rough stability heuristic
HYDROPATHY = {
    'I': 4.5, 'V': 4.2, 'L': 3.8, 'F': 2.8, 'C': 2.5,
    'M': 1.9, 'A': 1.8, 'G': -0.4, 'T': -0.7, 'S': -0.8,
    'W': -0.9, 'Y': -1.3, 'P': -1.6, 'H': -3.2, 'E': -3.5,
    'Q': -3.5, 'D': -3.5, 'N': -3.5, 'K': -3.9, 'R': -4.5
}
CHARGED = set('DEKHR')


def _collect_coords(structure):
    coords = []
    residues = []
    for model in structure:
        for chain in model:
            for res in chain:
                if res.get_resname().strip() not in [
                    'ALA','ARG','ASN','ASP','CYS','GLU','GLN','GLY','HIS','ILE',
                    'LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL']:
                    continue
                residues.append(res)
                for atom in res.get_atoms():
                    coords.append(atom.get_coord())
    return residues, coords


def simple_stability_score(pdb_path: str, probe_radius: float = 10.0) -> float:
    """Very rough stability estimate: hydrophobic core (good) vs buried charge (bad)."""
    p = Path(pdb_path)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    parser = PDBParser(QUIET=True)
    s = parser.get_structure("protein", str(p))
    residues, coords = _collect_coords(s)
    if not residues:
        raise ValueError("No standard residues found in PDB")
    import numpy as np
    coords = np.array(coords)
    score = 0.0

    three_to_one = {
        'ALA': 'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLU':'E','GLN':'Q','GLY':'G','HIS':'H','ILE':'I',
        'LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'
    }
    for res in residues:
        if not res.has_id('CA'):
            continue
        ca = res['CA'].get_coord()
        dists = ((coords - ca) ** 2).sum(axis=1) ** 0.5
        neighbors = (dists < probe_radius) & (dists > 0)
        nbh = neighbors.sum()
        burial = min(nbh / 20.0, 1.0)
        one = three_to_one.get(res.get_resname().strip())
        if not one:
            continue
        hydro = HYDROPATHY.get(one, 0.0)
        if hydro > 0:
            score -= hydro * burial
        if one in CHARGED and burial > 0.7:
            score += 5.0
    return score


def compare_stability_simple(
    pdb_wt: str,
    pdb_mut: str,
    output_dir: Optional[str] = None,
    report_name: str = "stability_comparison.txt",
) -> str:
    """Compare stability scores for WT vs MUT; write a report and return its path."""
    p_wt, p_mut = Path(pdb_wt), Path(pdb_mut)
    if not output_dir:
        output_dir = str(p_wt.parent)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    report_path = Path(output_dir) / report_name

    wt = simple_stability_score(str(p_wt))
    mu = simple_stability_score(str(p_mut))
    ddg = mu - wt
    if ddg > 0.5:
        effect = "Destabilizing"
    elif ddg < -0.5:
        effect = "Stabilizing"
    else:
        effect = "Neutral (within noise threshold)"

    lines = [
        "THERMODYNAMIC STABILITY COMPARISON (SIMPLE HEURISTIC)",
        "=" * 55,
        f"Wild-type PDB:      {str(p_wt.resolve())}",
        f"Mutant PDB:         {str(p_mut.resolve())}",
        "",
        "Stability Scores (lower = more stable):",
        f"  WT:   {wt:8.2f}",
        f"  MUT:  {mu:8.2f}",
        "",
        "Approximate ΔΔG (MUT - WT):",
        f"  ΔΔG ≈ {ddg:6.2f} kcal/mol",
        f"  Effect: {effect}",
        "",
        "NOTE: Crude heuristic based on hydrophobicity and buried charges.",
        "Not a substitute for physics-based or ML predictors.",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return str(report_path.resolve())


def download_pdb_structures_for_protein(
    protein_name: str,
    organism: str = "human",
    output_dir: str = ".",
) -> Optional[str]:
    """Download experimental PDBs for a gene/protein; returns folder path or None."""
    # Normalize symbol
    try:
        from .gene_normalization import normalize_gene
        norm = normalize_gene(protein_name)
        symbol = norm.get("canonical_symbol") if norm else protein_name
    except Exception:
        symbol = protein_name

    # Query UniProt to get accession
    try:
        from .protein_sequence import find_uniprot as _find
        info = _find(symbol, organism=organism, save_to_file=False)
        if not info or isinstance(info, dict) and info.get("error"):
            return None
        uniprot_id = info.get("uniprot_id")
        if not uniprot_id:
            return None
    except Exception:
        return None

    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return None

    pdb_ids = []
    for ref in data.get("uniProtKBCrossReferences", []):
        if ref.get("database") == "PDB":
            pdb_ids.append(ref["id"])
    if not pdb_ids:
        return None

    folder = Path(output_dir) / f"{symbol}_pdb"
    folder.mkdir(parents=True, exist_ok=True)
    count = 0
    for pid in pdb_ids:
        pdb_url = f"https://files.rcsb.org/download/{pid}.pdb"
        try:
            resp = requests.get(pdb_url, timeout=15)
            if resp.status_code == 200 and resp.content[:4] in (b"ATOM", b"HETA", b"REMA", b"HEAD"):
                (folder / f"{pid}.pdb").write_bytes(resp.content)
                count += 1
        except Exception:
            continue
    return str(folder.resolve())


def smart_visualize(
    pdb_file: str,
    output_html: str = "viewer.html",
    background: str = "white",
) -> str:
    """
    Generate a minimal HTML file that loads 3Dmol.js and shows the PDB.
    Requires internet access to fetch 3Dmol.js. Returns the HTML path.
    """
    p = Path(pdb_file)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    html = f"""
<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <script src=\"https://3dmol.org/build/3Dmol.js\"></script>
  <style>html,body,#viewer {{height:100%; margin:0; background:{background};}}</style>
  <title>3D Viewer</title>
  </head>
  <body>
  <div id=\"viewer\"></div>
  <script>
    var element = document.getElementById('viewer');
            var config = {{ backgroundColor: '{background}' }};
    var viewer = $3Dmol.createViewer(element, config);
    var pdb = `{p.read_text().replace('`','\\`')}`;
    viewer.addModel(pdb, 'pdb');
    viewer.setStyle({{}}, {{cartoon: {{}}}});
    viewer.zoomTo();
    viewer.render();
  </script>
  </body>
</html>
"""
    out = Path(output_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return str(out.resolve())
