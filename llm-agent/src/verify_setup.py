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
        from tools import (
            normalize_gene,
            find_uniprot,
            download_uniprot_fasta,
            mutate_replace,
            mutate_delete,
            mutate_insert,
            mutate_truncate,
            get_gene_variants_excel,
            plot_mammalian_tree,
            generate_horvath_gene_report,
            generate_phenoage_gene_report,
            generate_mammal_report,
            get_reactome_pathways,
            get_go_annotation,
            get_drug_info,
        )
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
        
        assert len(ALL_SCHEMAS) == 15, f"Expected 15 schemas, got {len(ALL_SCHEMAS)}"
        
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
        
        # Get expected function names from schemas
        expected_functions = {schema["name"] for schema in ALL_SCHEMAS}
        
        # Check they're all importable
        from tools import (
            normalize_gene,
            find_uniprot,
            download_uniprot_fasta,
            mutate_replace,
            mutate_delete,
            mutate_insert,
            mutate_truncate,
            get_gene_variants_excel,
            plot_mammalian_tree,
            generate_horvath_gene_report,
            generate_phenoage_gene_report,
            generate_mammal_report,
            get_reactome_pathways,
            get_go_annotation,
            get_drug_info,
        )
        
        # Create function map
        function_map = {
            "normalize_gene": normalize_gene,
            "find_uniprot": find_uniprot,
            "download_uniprot_fasta": download_uniprot_fasta,
            "mutate_replace": mutate_replace,
            "mutate_delete": mutate_delete,
            "mutate_insert": mutate_insert,
            "mutate_truncate": mutate_truncate,
            "get_gene_variants_excel": get_gene_variants_excel,
            "plot_mammalian_tree": plot_mammalian_tree,
            "generate_horvath_gene_report": generate_horvath_gene_report,
            "generate_phenoage_gene_report": generate_phenoage_gene_report,
            "generate_mammal_report": generate_mammal_report,
            "get_reactome_pathways": get_reactome_pathways,
            "get_go_annotation": get_go_annotation,
            "get_drug_info": get_drug_info,
        }
        
        available_functions = set(function_map.keys())
        
        # Check all expected functions are available
        missing = expected_functions - available_functions
        assert not missing, f"Missing functions: {missing}"
        
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
