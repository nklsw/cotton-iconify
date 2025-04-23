import tempfile
import shutil
import json
import filecmp
from pathlib import Path
import pytest
from cotton_iconify.cli import main
from cotton_iconify.generators import generate_icon_file, generate_all_icons


# Helper function to assert directories match
def assert_directories_equal(dir1, dir2, ignore=None):
    """
    Assert that two directories contain identical files.

    Args:
        dir1: First directory path
        dir2: Second directory path
        ignore: List of filenames to ignore
    """
    ignore = ignore or []
    dcmp = filecmp.dircmp(dir1, dir2, ignore=ignore)

    # Check for files that exist in both dirs but have different content
    different_files = dcmp.diff_files
    only_in_dir1 = dcmp.left_only
    only_in_dir2 = dcmp.right_only

    assert len(different_files) == 0, (
        f"Found {len(different_files)} files with different content: {different_files}"
    )
    assert len(only_in_dir1) == 0, (
        f"Found {len(only_in_dir1)} extra files in generated directory: {only_in_dir1}"
    )
    assert len(only_in_dir2) == 0, (
        f"Missing {len(only_in_dir2)} files in generated directory: {only_in_dir2}"
    )


# Helper to verify file content
def assert_file_content_equal(generated_path, expected_path, icon_name):
    """
    Assert that a generated file matches its expected content.

    Args:
        generated_path: Path to the generated file
        expected_path: Path to the expected file
        icon_name: Name of the icon being tested
    """
    assert generated_path.exists(), f"Generated file {generated_path} does not exist"
    assert expected_path.exists(), f"Expected file {expected_path} does not exist"

    with open(expected_path, "r") as expected_file:
        expected_content = expected_file.read()

    with open(generated_path, "r") as generated_file:
        generated_content = generated_file.read()

    assert generated_content == expected_content, (
        f"Generated content for {icon_name} doesn't match expected content"
    )


class TestCottonIconify:
    @pytest.fixture
    def test_data_path(self):
        """Return the path to the test data directory"""
        return Path(__file__).parent / "data"

    @pytest.fixture
    def brandico_json_path(self, test_data_path):
        """Return the path to the brandico.json test file"""
        return test_data_path / "brandico.json"

    @pytest.fixture
    def expected_output_dir(self, test_data_path):
        """Return the path to the expected output directory"""
        return test_data_path / "output"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files and clean it up after the test"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def icon_set(self, brandico_json_path):
        """Load the test icon set data"""
        with open(brandico_json_path, "r") as f:
            return json.load(f)

    @pytest.fixture
    def mock_brandico_request(self, requests_mock, brandico_json_path):
        """Set up mock for brandico.json HTTP request"""
        # Create the URL that will be requested (after GitHub conversion)
        json_url = "https://raw.githubusercontent.com/iconify/icon-sets/master/json/brandico.json"

        # Load the actual test data to use as response
        with open(brandico_json_path, "r") as f:
            json_content = f.read()

        # Register the mock URL
        requests_mock.get(json_url, text=json_content)

    def test_generate_single_icon(self, icon_set, temp_output_dir, expected_output_dir):
        """Test generating a single icon and compare with expected output"""
        # Choose a specific icon to test
        icon_name = "amex"

        # Generate the icon
        success, _ = generate_icon_file(
            icon_name, icon_set, temp_output_dir, overwrite_all=True
        )

        # Check that the file was created successfully
        assert success, f"Failed to generate icon {icon_name}"

        # Verify file content
        expected_file_path = expected_output_dir / f"{icon_name}.html"
        generated_file_path = Path(temp_output_dir) / f"{icon_name}.html"
        assert_file_content_equal(generated_file_path, expected_file_path, icon_name)

    def test_generate_all_icons(self, icon_set, temp_output_dir, expected_output_dir):
        """Test generating all icons and compare with expected output"""
        # Generate all icons
        generate_all_icons(icon_set, temp_output_dir, overwrite_all=True)

        # Compare generated files with expected output
        assert_directories_equal(temp_output_dir, expected_output_dir)

    def test_multiple_specific_icons(
        self, icon_set, temp_output_dir, expected_output_dir
    ):
        """Test generating multiple specific icons and compare with expected output"""
        # Choose a few icons to test
        icon_names = ["facebook", "youku", "box"]

        # Generate each icon
        for icon_name in icon_names:
            success, _ = generate_icon_file(
                icon_name, icon_set, temp_output_dir, overwrite_all=True
            )
            assert success, f"Failed to generate icon {icon_name}"

        # Check that all files were created and match expected content
        for icon_name in icon_names:
            expected_file_path = expected_output_dir / f"{icon_name}.html"
            generated_file_path = Path(temp_output_dir) / f"{icon_name}.html"
            assert_file_content_equal(
                generated_file_path, expected_file_path, icon_name
            )

    @pytest.mark.parametrize(
        "cli_args,icon_to_check",
        [
            (
                ["brandico", "facebook", "--force"],
                "facebook",  # Check specific icon
            ),
            (
                ["brandico", "--all", "--force"],
                None,  # Check all icons
            ),
        ],
    )
    def test_cli(
        self,
        mock_brandico_request,
        temp_output_dir,
        expected_output_dir,
        monkeypatch,
        cli_args,
        icon_to_check,
    ):
        """Test the CLI functionality using requests_mock"""
        # Prepare CLI arguments
        full_args = ["cotton-iconify"] + cli_args

        # Add output directory to CLI args
        output_idx = (
            full_args.index("--force") if "--force" in full_args else len(full_args)
        )
        full_args = (
            full_args[:output_idx]
            + ["--output", temp_output_dir]
            + full_args[output_idx:]
        )

        # Mock sys.argv using monkeypatch instead of unittest.mock
        monkeypatch.setattr("sys.argv", full_args)

        # Run the CLI
        main()

        # Verify results based on test case
        if icon_to_check:
            # Check specific icon
            expected_file_path = expected_output_dir / f"{icon_to_check}.html"
            generated_file_path = Path(temp_output_dir) / f"{icon_to_check}.html"
            assert_file_content_equal(
                generated_file_path, expected_file_path, icon_to_check
            )
        else:
            # Compare all files
            assert_directories_equal(temp_output_dir, expected_output_dir)
