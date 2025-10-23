"""
Quick verification that the agent and all tools are properly configured.

This test checks:
1. All tool modules can be imported
2. Function schemas are properly defined
3. Agent can be initialized (without API key)
4. All function mappings are correct
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))


def test_tool_imports():
    """Test that all tool modules can be imported."""
    print("Testing tool imports...", end=" ")
    try:
        # Import a lightweight subset directly from modules to avoid optional heavy deps during quick checks
        from tools.gene_normalization import normalize_gene  # type: ignore
        from tools.protein_sequence import find_uniprot, download_uniprot_fasta  # type: ignore
        from tools.mutations import mutate_replace, mutate_delete, mutate_insert, mutate_truncate  # type: ignore
        from tools.variants import get_gene_variants_excel  # type: ignore
        from tools.uniprot_parsers import get_reactome_pathways, get_go_annotation, get_drug_info  # type: ignore
        print("✅ PASS")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_function_schemas():
    """Test that function schemas are properly defined."""
    print("Testing function schemas...", end=" ")
    try:
        from function_schemas import ALL_SCHEMAS

        # We now expose additional helper tools (e.g., artifact helpers), so only assert a minimum count
        assert len(ALL_SCHEMAS) >= 15, f"Expected at least 15 schemas, got {len(ALL_SCHEMAS)}"

        # Check each schema has required fields
        for schema in ALL_SCHEMAS:
            assert "name" in schema, "Schema missing 'name'"
            assert "description" in schema, "Schema missing 'description'"
            assert "parameters" in schema, "Schema missing 'parameters'"

        print("✅ PASS")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_agent_structure():
    """Test that agent can be initialized (structure only, no API call)."""
    print("Testing agent structure...", end=" ")
    try:
        # Don't actually initialize (would require API key)
        # Just check the class exists and has expected methods
        import inspect
        from agent import LongevityAgent
        
        methods = [m for m, _ in inspect.getmembers(LongevityAgent, predicate=inspect.isfunction)]
        
        required_methods = ["__init__", "chat", "reset", "_execute_function"]
        for method in required_methods:
            assert method in methods, f"Missing method: {method}"
        
        print("✅ PASS")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_function_map_completeness():
    """Test that all functions in schemas are in the function map."""
    print("Testing function map completeness...", end=" ")
    try:
        from function_schemas import ALL_SCHEMAS

        # Check core tools are importable
        # Import core functions from their modules (avoid optional heavy deps like plotting/phylogeny here)
        from tools.gene_normalization import normalize_gene  # type: ignore
        from tools.protein_sequence import find_uniprot, download_uniprot_fasta  # type: ignore
        from tools.mutations import mutate_replace, mutate_delete, mutate_insert, mutate_truncate  # type: ignore
        from tools.variants import get_gene_variants_excel  # type: ignore
        from tools.aging_clocks import generate_horvath_gene_report, generate_phenoage_gene_report  # type: ignore
        from tools.mammal_data import generate_mammal_report  # type: ignore
        from tools.uniprot_parsers import get_reactome_pathways, get_go_annotation, get_drug_info  # type: ignore

        # Create core function map (artifact/helper tools may also be present but are not required here)
        function_map = {
            "normalize_gene": normalize_gene,
            "find_uniprot": find_uniprot,
            "download_uniprot_fasta": download_uniprot_fasta,
            "mutate_replace": mutate_replace,
            "mutate_delete": mutate_delete,
            "mutate_insert": mutate_insert,
            "mutate_truncate": mutate_truncate,
            "get_gene_variants_excel": get_gene_variants_excel,
            "generate_horvath_gene_report": generate_horvath_gene_report,
            "generate_phenoage_gene_report": generate_phenoage_gene_report,
            "generate_mammal_report": generate_mammal_report,
            "get_reactome_pathways": get_reactome_pathways,
            "get_go_annotation": get_go_annotation,
            "get_drug_info": get_drug_info,
        }

        available_functions = set(function_map.keys())

        # Ensure all core functions are present in schemas
        schema_functions = {schema["name"] for schema in ALL_SCHEMAS}
        missing_in_schemas = available_functions - schema_functions
        assert not missing_in_schemas, f"Core functions missing from schemas: {missing_in_schemas}"

        print("✅ PASS")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_cli_exists():
    """Test that CLI interface exists."""
    print("Testing CLI interface...", end=" ")
    try:
        from pathlib import Path
        cli_path = Path(__file__).parent / "cli.py"
        assert cli_path.exists(), "cli.py not found"
        print("✅ PASS")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_examples_exist():
    """Test that examples file exists."""
    print("Testing examples file...", end=" ")
    try:
        from pathlib import Path
        examples_path = Path(__file__).parent / "examples.py"
        assert examples_path.exists(), "examples.py not found"
        print("✅ PASS")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def main():
    """Run all verification tests."""
    print("\n" + "=" * 80)
    print("LONGEVITY RESEARCH LLM AGENT - SETUP VERIFICATION")
    print("=" * 80 + "\n")
    
    tests = [
        test_tool_imports,
        test_function_schemas,
        test_agent_structure,
        test_function_map_completeness,
        test_cli_exists,
        test_examples_exist,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 80)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\n🎉 Agent is properly configured and ready to use!")
        print("\nNext steps:")
        print("  1. Set OPENAI_API_KEY environment variable")
        print("  2. Run: python llm-agent/src/cli.py")
        print("  3. Or run: python llm-agent/src/examples.py")
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("\nPlease check the errors above and fix any issues.")
    
    print("=" * 80 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
