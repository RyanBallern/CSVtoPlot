"""Calculate density of structures per image based on pixel-to-area conversion."""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class DensityConfig:
    """Configuration for density calculations.

    Attributes:
        image_area_um2: Area of each image in µm² (default: 3.5021² = 12.2647 µm²)
        pixel_size: Size of one pixel in micrometers (optional, for pixel-based calculations)
        image_width: Image width in pixels (optional, for total area calculation)
        image_height: Image height in pixels (optional, for total area calculation)
    """
    image_area_um2: float = 3.5021 ** 2  # Default: 12.2647 µm² per image
    pixel_size: Optional[float] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None

    @property
    def pixel_area(self) -> Optional[float]:
        """Area of one pixel in μm², if pixel_size is set."""
        if self.pixel_size is not None:
            return self.pixel_size ** 2
        return None

    @property
    def image_area(self) -> float:
        """Total image area in μm²."""
        # If pixel dimensions are provided, calculate from those
        if (self.pixel_size is not None and
            self.image_width is not None and
            self.image_height is not None):
            return self.image_width * self.image_height * self.pixel_area
        # Otherwise use the configured image area
        return self.image_area_um2


@dataclass
class DensityResult:
    """Result of density calculation.

    Attributes:
        count: Number of structures
        area: Total area in μm²
        density: Density (structures per μm²)
        density_per_mm2: Density (structures per mm²)
        density_per_100um2: Density (structures per 100 μm²)
        source_file: Source file name (if applicable)
        condition: Condition name (if applicable)
    """
    count: int
    area: float
    density: float  # per μm²
    density_per_mm2: float
    density_per_100um2: float
    source_file: Optional[str] = None
    condition: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'count': self.count,
            'area_um2': self.area,
            'density_per_um2': self.density,
            'density_per_mm2': self.density_per_mm2,
            'density_per_100um2': self.density_per_100um2,
            'source_file': self.source_file,
            'condition': self.condition
        }


class DensityCalculator:
    """Calculate density of structures per image.

    Example usage:
        # Basic calculation with default pixel size (3.5021 μm)
        calc = DensityCalculator()
        density = calc.calculate_density(count=50, image_area_pixels=1024*1024)

        # With custom pixel size
        config = DensityConfig(pixel_size=2.5)
        calc = DensityCalculator(config)

        # Calculate for specific image dimensions
        config = DensityConfig(pixel_size=3.5021, image_width=1024, image_height=1024)
        calc = DensityCalculator(config)
        density = calc.calculate_density_from_count(count=50)
    """

    def __init__(self, config: Optional[DensityConfig] = None):
        """Initialize density calculator.

        Args:
            config: Density calculation configuration
        """
        self.config = config or DensityConfig()

    def calculate_density(self, count: int,
                          image_area_um2: Optional[float] = None,
                          num_images: int = 1,
                          source_file: Optional[str] = None,
                          condition: Optional[str] = None) -> DensityResult:
        """Calculate structure density.

        Default uses image area of 3.5021² = 12.2647 µm² per image.

        Args:
            count: Number of structures
            image_area_um2: Total image area in μm² (overrides default)
            num_images: Number of images (multiplies the per-image area)
            source_file: Source file name for tracking
            condition: Condition name for tracking

        Returns:
            DensityResult with calculated densities
        """
        # Determine total area
        if image_area_um2 is not None:
            total_area_um2 = image_area_um2
        else:
            # Use configured image area × number of images
            total_area_um2 = self.config.image_area * num_images

        # Calculate densities
        density_per_um2 = count / total_area_um2 if total_area_um2 > 0 else 0
        density_per_mm2 = density_per_um2 * 1_000_000  # 1 mm² = 1,000,000 μm²
        density_per_100um2 = density_per_um2 * 100

        return DensityResult(
            count=count,
            area=total_area_um2,
            density=density_per_um2,
            density_per_mm2=density_per_mm2,
            density_per_100um2=density_per_100um2,
            source_file=source_file,
            condition=condition
        )

    def calculate_density_from_count(self, count: int,
                                      num_images: int = 1,
                                      source_file: Optional[str] = None,
                                      condition: Optional[str] = None) -> DensityResult:
        """Calculate density using configured image area (default: 3.5021² µm²).

        Args:
            count: Number of structures
            num_images: Number of images (total area = image_area × num_images)
            source_file: Source file name
            condition: Condition name

        Returns:
            DensityResult with calculated densities
        """
        return self.calculate_density(
            count=count,
            num_images=num_images,
            source_file=source_file,
            condition=condition
        )

    def calculate_densities_from_dataframe(self,
                                            df: pd.DataFrame,
                                            count_column: str = 'count',
                                            image_area_column: Optional[str] = None,
                                            source_column: Optional[str] = 'source_file',
                                            condition_column: Optional[str] = 'condition',
                                            num_images_column: Optional[str] = None) -> pd.DataFrame:
        """Calculate densities for multiple images from a DataFrame.

        Args:
            df: DataFrame with count data
            count_column: Column name containing structure counts
            image_area_column: Column name containing image areas in µm² (optional)
            source_column: Column name for source file
            condition_column: Column name for condition
            num_images_column: Column name for number of images per row

        Returns:
            DataFrame with added density columns
        """
        results = []

        for idx, row in df.iterrows():
            count = row[count_column]

            # Get area
            if image_area_column and image_area_column in df.columns:
                area = row[image_area_column]
            else:
                # Use default image area, optionally multiplied by num_images
                num_images = 1
                if num_images_column and num_images_column in df.columns:
                    num_images = row[num_images_column]
                area = self.config.image_area * num_images

            result = self.calculate_density(
                count=count,
                image_area_um2=area,
                source_file=row.get(source_column) if source_column else None,
                condition=row.get(condition_column) if condition_column else None
            )
            results.append(result.to_dict())

        return pd.DataFrame(results)

    def calculate_density_per_image(self,
                                     df: pd.DataFrame,
                                     value_column: str = 'value',
                                     source_column: str = 'source_file',
                                     condition_column: Optional[str] = 'condition',
                                     image_area_um2: Optional[float] = None) -> pd.DataFrame:
        """Calculate density for each unique image based on structure count.

        This counts the number of rows (structures) per image and calculates density.
        Default image area is 3.5021² = 12.2647 µm².

        Args:
            df: DataFrame with one row per structure
            value_column: Column with measurement values (used to identify structures)
            source_column: Column identifying the source image
            condition_column: Column with condition information
            image_area_um2: Image area in µm² (default: 3.5021² = 12.2647 µm²)

        Returns:
            DataFrame with density per image
        """
        # Count structures per image
        group_cols = [source_column]
        if condition_column and condition_column in df.columns:
            group_cols.append(condition_column)

        counts = df.groupby(group_cols).size().reset_index(name='count')

        results = []
        for idx, row in counts.iterrows():
            count = row['count']

            # Get area (use provided or default from config)
            area = image_area_um2 if image_area_um2 is not None else self.config.image_area

            result = self.calculate_density(
                count=count,
                image_area_um2=area,
                source_file=row[source_column],
                condition=row.get(condition_column) if condition_column in row.index else None
            )
            results.append(result.to_dict())

        return pd.DataFrame(results)

    @staticmethod
    def pixel_area_from_size(pixel_size_um: float) -> float:
        """Calculate pixel area from pixel size.

        Args:
            pixel_size_um: Pixel size in micrometers

        Returns:
            Pixel area in μm²
        """
        return pixel_size_um ** 2

    @staticmethod
    def convert_area(value: float, from_unit: str, to_unit: str) -> float:
        """Convert area between units.

        Args:
            value: Area value
            from_unit: Source unit ('um2', 'mm2', 'nm2', 'pixel')
            to_unit: Target unit ('um2', 'mm2', 'nm2')

        Returns:
            Converted area value
        """
        # Convert to μm² first
        conversions_to_um2 = {
            'um2': 1,
            'mm2': 1_000_000,
            'nm2': 1e-6,
        }

        if from_unit not in conversions_to_um2 or to_unit not in conversions_to_um2:
            raise ValueError(f"Unknown unit. Use: {list(conversions_to_um2.keys())}")

        # Convert to μm² then to target unit
        um2_value = value * conversions_to_um2[from_unit]
        return um2_value / conversions_to_um2[to_unit]
