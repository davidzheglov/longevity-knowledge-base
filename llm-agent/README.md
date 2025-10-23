# Longevity Research LLM Agent

An OpenAI-powered conversational AI agent with specialized tools for longevity research, genomics, and bioinformatics.

## Overview

This agent provides natural language access to 15+ bioinformatics tools covering:
- **Gene & Protein Analysis**: Normalization, sequence retrieval, mutations, variants
- **Evolutionary Biology**: Phylogenetic trees, mammalian longevity data
- **Aging Research**: Epigenetic clocks (Horvath, PhenoAge), aging rate analysis
- **Functional Annotations**: Pathways, Gene Ontology, drug targets

## Quick Start

### 1. Installation

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Set OpenAI API Key

```powershell
$env:OPENAI_API_KEY = "your-api-key-here"
```

### 3. Run the Agent

```python
from src.agent import LongevityAgent

agent = LongevityAgent()
response = agent.chat("What pathways is TP53 involved in?")
print(response)
```

## Available Tools

### Gene & Protein Tools

#### `normalize_gene(query: str)`
Normalizes gene names, aliases, or Entrez IDs to canonical HGNC symbols.
```python
# Examples: 'p53' → 'TP53', 'Oct4' → 'POU5F1'
result = normalize_gene("p53")
# Returns: {'symbol': 'TP53', 'entrez_id': '7157', 'type': 'protein-coding', ...}
```

#### `find_uniprot(query: str, organism: str = "human")`
Searches UniProt for protein sequences in any organism.
```python
result = find_uniprot("TP53", organism="human")
# Returns: {'canonical_symbol': 'TP53', 'uniprot_id': 'P04637', 'fasta': '>', ...}
```

#### `get_gene_variants_excel(query: str)`
Retrieves all known protein variants (SNPs, disease mutations) from UniProt.
```python
get_gene_variants_excel("BRCA1")
# Creates Excel file with variant data
```

#### Mutation Tools
```python
# Point mutation: TP53 R175H
mutate_replace("TP53", pos=175, new_aa="H")

# Deletion: Remove residue at position 273
mutate_delete("TP53", pos=273)

# Insertion: Add glycines after position 100
mutate_insert("TP53", pos=100, ins_aa="GGG")

# Truncation: Keep only first 300 residues
mutate_truncate("TP53", pos=300)
```

### Evolutionary Biology Tools

#### `plot_mammalian_tree(species_list: List[str])`
Visualizes phylogenetic relationships between mammal species.
```python
species = ["Homo sapiens", "Pan troglodytes", "Mus musculus", "Loxodonta africana"]
plot_mammalian_tree(species, layout="r")  # 'r' for radial, 'u' for rectangular
```

#### `generate_mammal_report(species_query: str)`
Comprehensive longevity report combining AnAge and AROCM databases.
```python
generate_mammal_report("Homo sapiens")
# Returns: {'species': 'Homo sapiens', 'max_longevity': 122.5, 'body_mass_g': 62000, ...}
```

### Aging Clock Tools

#### `generate_horvath_gene_report(gene_symbol: str)`
Analyzes a gene's role in Horvath's multi-tissue epigenetic aging clock.
```python
generate_horvath_gene_report("NPPB")
# Shows CpG sites, coefficients, rankings (353 sites total)
```

#### `generate_phenoage_gene_report(gene_symbol: str)`
Analyzes a gene's role in DNAm PhenoAge mortality predictor.
```python
generate_phenoage_gene_report("SLC44A1")
# Shows CpG sites, coefficients, rankings (513 sites total)
```

### Functional Annotation Tools

#### `get_reactome_pathways(query: str)`
Retrieves biological pathways from Reactome database.
```python
pathways = get_reactome_pathways("TP53")
# Returns: [{'pathway_id': 'R-HSA-6804754', 'pathway_name': 'Regulation of TP53 Activity'}, ...]
```

#### `get_go_annotation(query: str)`
Retrieves Gene Ontology annotations (Molecular Function, Biological Process, Cellular Component).
```python
go_terms = get_go_annotation("TP53")
# Returns: {'molecular_function': [...], 'biological_process': [...], 'cellular_component': [...]}
```

#### `get_drug_info(query: str)`
Retrieves DrugBank information for drugs targeting the gene/protein.
```python
drugs = get_drug_info("EGFR")
# Returns: [{'drug_id': 'DB00530', 'drug_name': 'Erlotinib'}, ...]
```

## Agent Usage Examples

### Example 1: Basic Gene Query
```python
agent = LongevityAgent()
response = agent.chat("What is the role of FOXO3 in aging?")
```
The agent will:
1. Normalize "FOXO3" to canonical symbol
2. Query Reactome pathways
3. Check GO annotations
4. Look for aging clock associations
5. Synthesize a comprehensive answer

### Example 2: Cross-Species Analysis
```python
response = agent.chat("Compare TP53 protein sequences between human, mouse, and elephant")
```
The agent will:
1. Download sequences for all three organisms
2. Perform multiple sequence alignment
3. Identify conserved and divergent regions
4. Explain evolutionary significance

### Example 3: Mutation Impact
```python
response = agent.chat("Create the TP53 R175H mutation and analyze its pathways")
```
The agent will:
1. Create the R175H mutation
2. Save mutated FASTA
3. Query pathways affected by TP53
4. Explain the clinical significance of R175H

## Data Files

The agent requires several data files in `llm-agent/data/`:

| File | Description | Source |
|------|-------------|--------|
| `gene_info.txt` | Gene symbols, aliases, IDs | NCBI Gene |
| `Horvath.csv` | Horvath clock CpG sites | [Horvath 2013](https://genomebiology.biomedcentral.com/articles/10.1186/gb-2013-14-10-r115) |
| `PhenoAge.csv` | PhenoAge clock CpG sites | [Levine et al. 2018](https://www.aging-us.com/article/101414/text) |
| `Mammals_Tree.nwk` | Mammalian phylogeny | [TimeTree](http://www.timetree.org/) |
| `anage_mammals.csv` | Mammalian lifespan data | [AnAge Database](https://genomics.senescence.info/species/) |
| `AROCM.csv` | Aging rate coefficients | AROCM model |

## Function Calling Architecture

The agent uses OpenAI's function calling to intelligently decide which tools to use:

```
User Query → GPT-4 → Function Schema Selection → Tool Execution → Result → GPT-4 → Natural Language Response
```

Each tool has a function schema (`function_schemas.py`) that describes:
- Function name and purpose
- Required and optional parameters
- Parameter types and constraints
- Expected return format

## Testing

Run comprehensive unit tests:

```powershell
# All tests
python -m unittest discover -s llm-agent/src/tests

# Specific module
python -m unittest llm-agent/src/tests/test_gene_normalization.py -v

# With coverage
pip install coverage
coverage run -m unittest discover -s llm-agent/src/tests
coverage report
```

Current test coverage: **60+ tests across 9 modules**

## Advanced Usage

### Custom System Prompt
```python
agent = LongevityAgent()
agent.system_prompt = "You are an aging researcher specializing in mitochondrial biology..."
agent.reset()  # Apply new prompt
```

### Conversation History
```python
# Continue multi-turn conversation
agent.chat("Tell me about SIRT1")
agent.chat("What about its role in caloric restriction?")  # Maintains context
agent.chat("Compare it to SIRT6")

# Reset for new topic
agent.reset()
```

### Error Handling
```python
try:
    response = agent.chat("Analyze gene XYZ123")
except ValueError as e:
    print(f"Invalid gene: {e}")
```

## Troubleshooting

### Issue: "OpenAI API key not found"
**Solution**: Set environment variable
```powershell
$env:OPENAI_API_KEY = "sk-..."
```

### Issue: "Data file not found"
**Solution**: Ensure all data files are in `llm-agent/data/`
```powershell
ls llm-agent/data/
```

### Issue: "Ghostscript not found" (phylogeny visualization)
**Solution**: Install Ghostscript and add to PATH
```powershell
# Download from https://ghostscript.com/releases/
# Add to PATH: C:\Program Files\gs\gs10.04.0\bin
```

### Issue: Module import errors
**Solution**: Ensure you're running from the workspace root
```powershell
cd c:\Users\dgala\longevity-knowledge-base
python -c "from llm-agent.src.agent import LongevityAgent"
```

## Extending the Agent

### Adding a New Tool

1. **Implement the tool function** in `llm-agent/src/tools/`:
```python
# llm-agent/src/tools/my_tool.py
def my_new_tool(param1: str, param2: int) -> dict:
    """
    Clear description of what the tool does.
    
    Args:
        param1: Description of parameter
        param2: Description of parameter
        
    Returns:
        Dictionary with structured results
    """
    # Implementation
    return {"result": "data"}
```

2. **Add to `tools/__init__.py`**:
```python
from .my_tool import my_new_tool
__all__ = [..., "my_new_tool"]
```

3. **Create function schema** in `function_schemas.py`:
```python
MY_NEW_TOOL_SCHEMA = {
    "name": "my_new_tool",
    "description": "Clear description for the LLM",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "What param1 represents"
            },
            "param2": {
                "type": "integer",
                "description": "What param2 represents"
            }
        },
        "required": ["param1", "param2"]
    }
}

ALL_SCHEMAS.append(MY_NEW_TOOL_SCHEMA)
```

4. **Add to agent function map** in `agent.py`:
```python
self.function_map = {
    ...
    "my_new_tool": my_new_tool,
}
```

5. **Write unit tests** in `llm-agent/src/tests/test_my_tool.py`

### Best Practices for LLM-Compatible Tools

✅ **DO**:
- Use clear, descriptive function and parameter names
- Write comprehensive docstrings with Args/Returns
- Return structured data (dicts/lists, not complex objects)
- Include optional parameters with sensible defaults
- Validate inputs and provide informative error messages
- Log verbose output only when requested
- Use absolute file paths for file I/O

❌ **DON'T**:
- Return unstructured text blobs without JSON
- Use ambiguous parameter names like `data`, `x`, `tmp`
- Require too many mandatory parameters
- Raise cryptic exceptions
- Print directly to stdout (use return values)
- Hard-code file paths

## Performance Tips

- **Use specific queries**: "Get FOXO3 pathways" instead of "Tell me everything about FOXO3"
- **Break complex requests**: Multiple simple queries > one complex query
- **Reset between topics**: `agent.reset()` clears conversation history
- **Set max_iterations**: Limit function calling loops with `agent.chat(msg, max_iterations=3)`

## Citation

If you use this agent in your research, please cite:

```bibtex
@software{longevity_llm_agent,
  title = {Longevity Research LLM Agent},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/longevity-knowledge-base}
}
```

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new tools
4. Submit a pull request

## Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/longevity-knowledge-base/issues)
- Documentation: See `llm-agent/PROGRESS.md` for development notes

---

**Built with**: Python 3.12, OpenAI GPT-4, BioPython, Pandas, ToytTree
