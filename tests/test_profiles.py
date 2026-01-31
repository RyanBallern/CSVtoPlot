#!/usr/bin/env python3
"""Tests for Analysis Profiles (Part 7)."""

import unittest
import tempfile
import shutil
from pathlib import Path

from src.neuromorpho_analyzer.core.profiles import AnalysisProfile, ProfileManager


class TestAnalysisProfile(unittest.TestCase):
    """Test AnalysisProfile dataclass."""

    def test_create_default_profile(self):
        """Test creating a default profile."""
        profile = AnalysisProfile.default_profile("Test")
        self.assertEqual(profile.name, "Test")
        self.assertEqual(profile.alpha, 0.05)
        self.assertTrue(profile.export_excel)
        self.assertEqual(profile.image_area_um2, 12.2647)  # 3.5021²

    def test_create_custom_profile(self):
        """Test creating a custom profile."""
        profile = AnalysisProfile(
            name="Custom Analysis",
            description="My custom analysis",
            import_parameters=['Length', 'Volume'],
            alpha=0.01,
            calculate_density=True
        )
        self.assertEqual(profile.name, "Custom Analysis")
        self.assertEqual(profile.import_parameters, ['Length', 'Volume'])
        self.assertEqual(profile.alpha, 0.01)
        self.assertTrue(profile.calculate_density)

    def test_to_dict(self):
        """Test converting profile to dictionary."""
        profile = AnalysisProfile(name="Test", description="Test profile")
        data = profile.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['name'], "Test")
        self.assertEqual(data['description'], "Test profile")

    def test_to_json(self):
        """Test converting profile to JSON."""
        profile = AnalysisProfile(name="Test")
        json_str = profile.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn('"name": "Test"', json_str)

    def test_from_dict(self):
        """Test loading profile from dictionary."""
        data = {
            'name': 'Loaded Profile',
            'description': 'From dict',
            'alpha': 0.01
        }
        profile = AnalysisProfile.from_dict(data)
        self.assertEqual(profile.name, 'Loaded Profile')
        self.assertEqual(profile.alpha, 0.01)

    def test_from_json(self):
        """Test loading profile from JSON."""
        json_str = '{"name": "JSON Profile", "description": "From JSON", "alpha": 0.05}'
        profile = AnalysisProfile.from_json(json_str)
        self.assertEqual(profile.name, 'JSON Profile')

    def test_roundtrip(self):
        """Test JSON roundtrip preserves data."""
        original = AnalysisProfile(
            name="Roundtrip Test",
            import_parameters=['A', 'B', 'C'],
            alpha=0.01,
            frequency_bin_size=20.0
        )
        json_str = original.to_json()
        restored = AnalysisProfile.from_json(json_str)

        self.assertEqual(original.name, restored.name)
        self.assertEqual(original.import_parameters, restored.import_parameters)
        self.assertEqual(original.alpha, restored.alpha)
        self.assertEqual(original.frequency_bin_size, restored.frequency_bin_size)

    def test_get_active_plot_types(self):
        """Test getting active plot types."""
        profile = AnalysisProfile(name="Test")
        active = profile.get_active_plot_types()
        self.assertIn('barplot_relative', active)
        self.assertIn('boxplot_total', active)

    def test_set_plot_type(self):
        """Test enabling/disabling plot types."""
        profile = AnalysisProfile(name="Test")
        profile.set_plot_type('barplot_relative', False)
        self.assertFalse(profile.plot_types['barplot_relative'])
        self.assertNotIn('barplot_relative', profile.get_active_plot_types())

    def test_is_condition_selected(self):
        """Test condition selection check."""
        # All conditions selected (None)
        profile = AnalysisProfile(name="Test")
        self.assertTrue(profile.is_condition_selected('Control'))
        self.assertTrue(profile.is_condition_selected('Treatment'))

        # Specific conditions selected
        profile.selected_conditions = ['Control']
        self.assertTrue(profile.is_condition_selected('Control'))
        self.assertFalse(profile.is_condition_selected('Treatment'))


class TestProfileManager(unittest.TestCase):
    """Test ProfileManager class."""

    def setUp(self):
        """Create temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ProfileManager(Path(self.temp_dir))

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_save_profile(self):
        """Test saving a profile."""
        profile = AnalysisProfile(name="Save Test")
        path = self.manager.save_profile(profile)
        self.assertTrue(path.exists())
        self.assertEqual(path.name, "Save_Test.json")

    def test_save_profile_no_overwrite(self):
        """Test that saving without overwrite raises error."""
        profile = AnalysisProfile(name="No Overwrite")
        self.manager.save_profile(profile)

        with self.assertRaises(FileExistsError):
            self.manager.save_profile(profile, overwrite=False)

    def test_save_profile_with_overwrite(self):
        """Test saving with overwrite."""
        profile = AnalysisProfile(name="Overwrite Test", description="Original")
        self.manager.save_profile(profile)

        profile.description = "Updated"
        path = self.manager.save_profile(profile, overwrite=True)

        loaded = self.manager.load_profile("Overwrite Test")
        self.assertEqual(loaded.description, "Updated")

    def test_load_profile(self):
        """Test loading a profile."""
        profile = AnalysisProfile(name="Load Test", alpha=0.01)
        self.manager.save_profile(profile)

        loaded = self.manager.load_profile("Load Test")
        self.assertEqual(loaded.name, "Load Test")
        self.assertEqual(loaded.alpha, 0.01)

    def test_load_nonexistent_profile(self):
        """Test loading nonexistent profile raises error."""
        with self.assertRaises(FileNotFoundError):
            self.manager.load_profile("Does Not Exist")

    def test_list_profiles(self):
        """Test listing profiles."""
        self.manager.save_profile(AnalysisProfile(name="Profile A"))
        self.manager.save_profile(AnalysisProfile(name="Profile B"))
        self.manager.save_profile(AnalysisProfile(name="Profile C"))

        profiles = self.manager.list_profiles()
        self.assertEqual(len(profiles), 3)
        self.assertIn("Profile A", profiles)
        self.assertIn("Profile B", profiles)

    def test_delete_profile(self):
        """Test deleting a profile."""
        self.manager.save_profile(AnalysisProfile(name="Delete Me"))
        self.assertTrue(self.manager.profile_exists("Delete Me"))

        result = self.manager.delete_profile("Delete Me")
        self.assertTrue(result)
        self.assertFalse(self.manager.profile_exists("Delete Me"))

    def test_delete_nonexistent_profile(self):
        """Test deleting nonexistent profile returns False."""
        result = self.manager.delete_profile("Does Not Exist")
        self.assertFalse(result)

    def test_duplicate_profile(self):
        """Test duplicating a profile."""
        original = AnalysisProfile(name="Original", alpha=0.01)
        self.manager.save_profile(original)

        duplicate = self.manager.duplicate_profile("Original", "Copy")
        self.assertEqual(duplicate.name, "Copy")
        self.assertEqual(duplicate.alpha, 0.01)
        self.assertTrue(self.manager.profile_exists("Copy"))

    def test_profile_exists(self):
        """Test checking if profile exists."""
        self.assertFalse(self.manager.profile_exists("Test"))
        self.manager.save_profile(AnalysisProfile(name="Test"))
        self.assertTrue(self.manager.profile_exists("Test"))

    def test_current_profile(self):
        """Test current profile tracking."""
        self.assertIsNone(self.manager.get_current_profile())

        profile = AnalysisProfile(name="Current")
        self.manager.save_profile(profile)
        self.manager.load_profile("Current")

        current = self.manager.get_current_profile()
        self.assertIsNotNone(current)
        self.assertEqual(current.name, "Current")

    def test_timestamps(self):
        """Test that timestamps are set on save."""
        profile = AnalysisProfile(name="Timestamp Test")
        self.assertIsNone(profile.created_date)

        self.manager.save_profile(profile)
        loaded = self.manager.load_profile("Timestamp Test")

        self.assertIsNotNone(loaded.created_date)
        self.assertIsNotNone(loaded.modified_date)


if __name__ == '__main__':
    print("=" * 60)
    print("Testing Analysis Profiles (Part 7)")
    print("=" * 60)
    unittest.main(verbosity=2)
