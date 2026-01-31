"""Profile manager for saving, loading, and managing analysis profiles."""

from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from .profile_schema import AnalysisProfile


class ProfileManager:
    """Manages analysis profiles (save/load/edit/delete).

    Profiles are stored as JSON files in a designated directory.
    Each profile contains complete pipeline configuration for
    reproducible analysis.

    Example usage:
        manager = ProfileManager(Path('./profiles'))

        # Create and save a profile
        profile = AnalysisProfile(
            name="My Analysis",
            description="Standard neuromorpho analysis",
            import_parameters=['Length', 'Volume'],
            alpha=0.05
        )
        manager.save_profile(profile)

        # List available profiles
        profiles = manager.list_profiles()

        # Load a profile
        loaded = manager.load_profile("My Analysis")

        # Delete a profile
        manager.delete_profile("My Analysis")
    """

    def __init__(self, profiles_dir: Path):
        """Initialize profile manager.

        Args:
            profiles_dir: Directory to store profile files
        """
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.current_profile: Optional[AnalysisProfile] = None

    def save_profile(self, profile: AnalysisProfile,
                     overwrite: bool = False) -> Path:
        """Save analysis profile to disk.

        Args:
            profile: AnalysisProfile to save
            overwrite: Allow overwriting existing profile

        Returns:
            Path to saved profile file

        Raises:
            FileExistsError: If profile exists and overwrite=False
        """
        # Set timestamps
        now = datetime.now().isoformat()
        if not profile.created_date:
            profile.created_date = now
        profile.modified_date = now

        # Generate filename (sanitize name)
        safe_name = self._sanitize_name(profile.name)
        filename = f'{safe_name}.json'
        filepath = self.profiles_dir / filename

        # Check if exists
        if filepath.exists() and not overwrite:
            raise FileExistsError(f"Profile already exists: {profile.name}")

        # Save
        with open(filepath, 'w') as f:
            f.write(profile.to_json())

        return filepath

    def load_profile(self, name: str) -> AnalysisProfile:
        """Load profile by name.

        Args:
            name: Profile name

        Returns:
            Loaded AnalysisProfile

        Raises:
            FileNotFoundError: If profile doesn't exist
        """
        safe_name = self._sanitize_name(name)
        filename = f'{safe_name}.json'
        filepath = self.profiles_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Profile not found: {name}")

        with open(filepath, 'r') as f:
            profile = AnalysisProfile.from_json(f.read())

        self.current_profile = profile
        return profile

    def list_profiles(self) -> List[str]:
        """Get list of available profile names.

        Returns:
            Sorted list of profile names
        """
        profiles = []
        for file_path in self.profiles_dir.glob('*.json'):
            # Convert filename back to readable name
            name = file_path.stem.replace('_', ' ')
            profiles.append(name)
        return sorted(profiles)

    def get_profile_info(self) -> List[Dict]:
        """Get detailed info about all profiles.

        Returns:
            List of dicts with name, description, dates
        """
        info_list = []
        for name in self.list_profiles():
            try:
                profile = self.load_profile(name)
                info_list.append({
                    'name': profile.name,
                    'description': profile.description,
                    'created_date': profile.created_date,
                    'modified_date': profile.modified_date,
                    'version': profile.version
                })
            except Exception:
                info_list.append({
                    'name': name,
                    'description': 'Error loading profile',
                    'created_date': None,
                    'modified_date': None,
                    'version': None
                })
        return info_list

    def delete_profile(self, name: str) -> bool:
        """Delete a profile.

        Args:
            name: Profile name to delete

        Returns:
            True if deleted, False if not found
        """
        safe_name = self._sanitize_name(name)
        filename = f'{safe_name}.json'
        filepath = self.profiles_dir / filename

        if filepath.exists():
            filepath.unlink()
            # Clear current if it was this profile
            if self.current_profile and self.current_profile.name == name:
                self.current_profile = None
            return True
        return False

    def duplicate_profile(self, source_name: str,
                          new_name: str) -> AnalysisProfile:
        """Duplicate an existing profile with new name.

        Args:
            source_name: Name of profile to duplicate
            new_name: Name for the new profile

        Returns:
            New AnalysisProfile instance
        """
        profile = self.load_profile(source_name)
        profile.name = new_name
        profile.created_date = None  # Will be set on save
        profile.modified_date = None
        self.save_profile(profile)
        return profile

    def profile_exists(self, name: str) -> bool:
        """Check if a profile exists.

        Args:
            name: Profile name to check

        Returns:
            True if profile exists
        """
        safe_name = self._sanitize_name(name)
        filename = f'{safe_name}.json'
        filepath = self.profiles_dir / filename
        return filepath.exists()

    def get_current_profile(self) -> Optional[AnalysisProfile]:
        """Get the currently loaded profile.

        Returns:
            Current profile or None
        """
        return self.current_profile

    def set_current_profile(self, profile: AnalysisProfile) -> None:
        """Set the current profile.

        Args:
            profile: Profile to set as current
        """
        self.current_profile = profile

    def create_default_profile(self, name: str = "Default",
                                save: bool = True) -> AnalysisProfile:
        """Create a default profile.

        Args:
            name: Profile name
            save: Whether to save to disk

        Returns:
            Default AnalysisProfile
        """
        profile = AnalysisProfile.default_profile(name)
        if save:
            self.save_profile(profile, overwrite=True)
        return profile

    def export_profile(self, name: str, output_path: Path) -> Path:
        """Export a profile to a specific location.

        Args:
            name: Profile name to export
            output_path: Destination path

        Returns:
            Path to exported file
        """
        profile = self.load_profile(name)
        with open(output_path, 'w') as f:
            f.write(profile.to_json())
        return output_path

    def import_profile(self, file_path: Path,
                       new_name: Optional[str] = None,
                       overwrite: bool = False) -> AnalysisProfile:
        """Import a profile from a file.

        Args:
            file_path: Path to profile JSON file
            new_name: Optional new name for the profile
            overwrite: Allow overwriting existing profile

        Returns:
            Imported AnalysisProfile
        """
        with open(file_path, 'r') as f:
            profile = AnalysisProfile.from_json(f.read())

        if new_name:
            profile.name = new_name

        self.save_profile(profile, overwrite=overwrite)
        return profile

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Convert profile name to safe filename.

        Args:
            name: Original name

        Returns:
            Sanitized name safe for filesystem
        """
        # Replace spaces and special chars with underscores
        safe = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        safe = safe.replace(':', '_').replace('*', '_').replace('?', '_')
        safe = safe.replace('"', '_').replace('<', '_').replace('>', '_')
        safe = safe.replace('|', '_')
        return safe
