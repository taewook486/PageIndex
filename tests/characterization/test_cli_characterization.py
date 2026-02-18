"""
Characterization tests for PageIndex CLI functionality.

These tests capture the EXISTING behavior of the CLI to ensure
that GUI addition does not break any existing functionality.
"""

import os
import json
import tempfile
from pathlib import Path
import pytest
from typing import Dict, Any


class TestCLICharacterization:
    """Characterization tests for CLI - documents WHAT IS, not what SHOULD BE."""

    @pytest.fixture
    def sample_pdf_path(self) -> str:
        """Path to a sample PDF file for testing."""
        # In real implementation, this would be a test fixture
        # For now, we'll skip if file doesn't exist
        pdf_path = Path(__file__).parent.parent / "fixtures" / "sample.pdf"
        if not pdf_path.exists():
            pytest.skip(f"Sample PDF not found at {pdf_path}")
        return str(pdf_path)

    @pytest.fixture
    def sample_md_path(self) -> str:
        """Path to a sample Markdown file for testing."""
        md_path = Path(__file__).parent.parent / "fixtures" / "sample.md"
        if not md_path.exists():
            pytest.skip(f"Sample Markdown not found at {md_path}")
        return str(md_path)

    @pytest.fixture
    def temp_output_dir(self, tmp_path: Path) -> Path:
        """Temporary directory for output files."""
        output_dir = tmp_path / "results"
        output_dir.mkdir(exist_ok=True)
        return output_dir

    def test_cli_config_loading_behavior(self):
        """Characterize how CLI loads configuration from config.yaml."""
        from pageindex.utils import ConfigLoader

        loader = ConfigLoader()

        # Document default behavior
        default_config = loader.load(None)

        # These are the ACTUAL defaults from config.yaml
        assert hasattr(default_config, 'model')
        assert hasattr(default_config, 'toc_check_page_num')
        assert hasattr(default_config, 'max_page_num_each_node')
        assert hasattr(default_config, 'max_token_num_each_node')
        assert hasattr(default_config, 'if_add_node_id')
        assert hasattr(default_config, 'if_add_node_summary')
        assert hasattr(default_config, 'if_add_doc_description')
        assert hasattr(default_config, 'if_add_node_text')

        # Document actual values (this captures current behavior)
        actual_values = {
            'model': default_config.model,
            'toc_check_page_num': default_config.toc_check_page_num,
            'max_page_num_each_node': default_config.max_page_num_each_node,
            'max_token_num_each_node': default_config.max_token_num_each_node,
            'if_add_node_id': default_config.if_add_node_id,
            'if_add_node_summary': default_config.if_add_node_summary,
            'if_add_doc_description': default_config.if_add_doc_description,
            'if_add_node_text': default_config.if_add_node_text,
        }

        # Save characterization data
        characterization_file = Path(__file__).parent / "cli_config_characterization.json"
        with open(characterization_file, 'w') as f:
            json.dump(actual_values, f, indent=2)

    def test_cli_config_merging_behavior(self):
        """Characterize how CLI merges user options with defaults."""
        from pageindex.utils import ConfigLoader

        loader = ConfigLoader()

        # Document merging behavior
        user_options = {
            'model': 'gpt-4',
            'toc_check_page_num': 30,
        }

        merged_config = loader.load(user_options)

        # User options should override defaults
        assert merged_config.model == 'gpt-4'
        assert merged_config.toc_check_page_num == 30

        # Non-specified options should use defaults
        assert merged_config.max_page_num_each_node == 10  # From config.yaml
        assert merged_config.max_token_num_each_node == 20000  # From config.yaml

    def test_cli_validation_behavior(self):
        """Characterize CLI validation behavior."""
        from pageindex.utils import ConfigLoader

        loader = ConfigLoader()

        # Test unknown key rejection
        with pytest.raises(ValueError, match="Unknown config keys"):
            loader.load({'unknown_key': 'value'})

    def test_page_index_api_exists(self):
        """Characterize that page_index_main function exists and is callable."""
        from pageindex.page_index import page_index_main
        from pageindex import config

        # Function should exist
        assert callable(page_index_main)

        # Should accept a file path and config object
        import inspect
        sig = inspect.signature(page_index_main)
        params = list(sig.parameters.keys())

        assert 'doc' in params
        assert 'opt' in params

    def test_md_to_tree_api_exists(self):
        """Characterize that md_to_tree function exists and is callable."""
        from pageindex.page_index_md import md_to_tree

        # Function should exist
        assert callable(md_to_tree)

        # Should be an async function
        import inspect
        assert inspect.iscoroutinefunction(md_to_tree)

    def test_models_importable(self):
        """Characterize that data models are importable."""
        from pageindex.models import (
            PageIndexConfig,
            Node,
            DocumentStructure,
            TocItem
        )

        # Models should be importable
        assert PageIndexConfig is not None
        assert Node is not None
        assert DocumentStructure is not None
        assert TocItem is not None

    def test_constants_defined(self):
        """Characterize that constants are properly defined."""
        from pageindex.constants import (
            EnvKeys,
            Defaults,
            ErrorMessages,
            Paths,
            JsonFields
        )

        # Constant classes should exist
        assert EnvKeys.CHATGPT_API_KEY == "CHATGPT_API_KEY"
        assert Defaults.MODEL == "glm-5"
        assert Paths.RESULTS_DIR == "./results"

    def test_utils_functions_exist(self):
        """Characterize that utility functions exist."""
        from pageindex.utils import (
            count_tokens,
            extract_json,
            ConfigLoader,
            get_page_tokens,
            JsonLogger
        )

        # Functions should be callable
        assert callable(count_tokens)
        assert callable(extract_json)
        assert callable(get_page_tokens)

        # Classes should be instantiable
        assert ConfigLoader is not None
        assert JsonLogger is not None

    def test_environment_variable_loading(self):
        """Characterize environment variable loading behavior."""
        from pageindex.utils import CHATGPT_API_KEY, OPENAI_BASE_URL

        # Environment variables should be loaded
        assert isinstance(CHATGPT_API_KEY, str)
        # OPENAI_BASE_URL can be None
        assert OPENAI_BASE_URL is None or isinstance(OPENAI_BASE_URL, str)


class TestCLIDataFlow:
    """Characterization tests for CLI data flow."""

    def test_pdf_processing_returns_dict_structure(self, sample_pdf_path):
        """Characterize the structure of PDF processing results."""
        if not os.path.exists(sample_pdf_path):
            pytest.skip("Sample PDF not available")

        from pageindex.page_index import page_index_main, config
        from pageindex.utils import ConfigLoader

        loader = ConfigLoader()
        opt = loader.load({
            'if_add_node_id': 'no',  # Disable for faster testing
            'if_add_node_summary': 'no',
        })

        result = page_index_main(sample_pdf_path, opt)

        # Result should be a dict
        assert isinstance(result, dict)

        # Should have doc_name
        assert 'doc_name' in result

        # Should have structure
        assert 'structure' in result
        assert isinstance(result['structure'], list)

        # Document the structure format
        characterization_file = Path(__file__).parent / "pdf_result_structure_characterization.json"
        if result['structure']:
            with open(characterization_file, 'w') as f:
                json.dump(result['structure'][0], f, indent=2, default=str)

    def test_config_loader_yaml_path(self):
        """Characterize the default config.yaml location."""
        from pageindex.utils import ConfigLoader
        from pageindex import __file__ as package_init

        # ConfigLoader should look for config.yaml in pageindex package
        pageindex_dir = Path(package_init).parent
        expected_config_path = pageindex_dir / "config.yaml"

        loader = ConfigLoader()
        assert expected_config_path.exists()

    def test_results_directory_creation(self):
        """Characterize results directory handling."""
        from pageindex.constants import Paths

        results_dir = Paths.RESULTS_DIR

        # Document the expected results directory path
        assert results_dir == "./results"

        # If it doesn't exist, it should be creatable
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir) / results_dir
            test_path.mkdir(parents=True, exist_ok=True)
            assert test_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
