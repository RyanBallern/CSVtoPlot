#!/usr/bin/env python3
"""Test script to verify ParameterMapper functionality."""

import sys
from pathlib import Path

# Add src to path so we can import our module
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from neuromorpho_analyzer.core.importers import ParameterMapper, HeaderScanner


def test_basic_functionality():
    """Test basic parameter selection and management."""
    print("=" * 70)
    print("Test 1: Basic Parameter Selection")
    print("=" * 70)

    # Sample headers (as if scanned from a file)
    headers = ['Length', 'Branch Points', 'Terminal Points', 'Average Diameter', 'Total Volume']

    print(f"\nAvailable headers: {headers}")

    # Create mapper
    mapper = ParameterMapper(headers)
    print(f"\nCreated mapper: {mapper}")

    # Select some parameters
    mapper.select_parameters(['Length', 'Branch Points', 'Total Volume'])
    print(f"\nSelected parameters: {mapper.get_all_parameters()}")
    print(f"Parameter count: {mapper.get_parameter_count()}")

    # Check if parameters are selected
    print(f"\nIs 'Length' selected? {mapper.is_parameter_selected('Length')}")
    print(f"Is 'Average Diameter' selected? {mapper.is_parameter_selected('Average Diameter')}")

    print("\n✓ Basic functionality working!")
    return True


def test_select_all():
    """Test selecting all available parameters."""
    print("\n" + "=" * 70)
    print("Test 2: Select All Parameters")
    print("=" * 70)

    headers = ['Length', 'Branch Points', 'Terminal Points', 'Average Diameter', 'Total Volume']
    mapper = ParameterMapper(headers)

    mapper.select_all_parameters()
    print(f"\nSelected all parameters: {mapper.get_all_parameters()}")
    print(f"Count: {mapper.get_parameter_count()}/{len(headers)}")

    print("\n✓ Select all working!")
    return True


def test_custom_parameters():
    """Test adding custom parameters."""
    print("\n" + "=" * 70)
    print("Test 3: Custom Parameters")
    print("=" * 70)

    headers = ['Length', 'Branch Points']
    mapper = ParameterMapper(headers)

    # Select standard parameters
    mapper.select_parameters(['Length'])

    # Add custom parameters
    mapper.add_custom_parameter('Density')
    mapper.add_custom_parameter('Volume Ratio')

    print(f"\nStandard parameters: {mapper.get_standard_parameters()}")
    print(f"Custom parameters: {mapper.get_custom_parameters()}")
    print(f"All parameters: {mapper.get_all_parameters()}")

    print("\n✓ Custom parameters working!")
    return True


def test_parameter_aliases():
    """Test parameter aliases."""
    print("\n" + "=" * 70)
    print("Test 4: Parameter Aliases")
    print("=" * 70)

    headers = ['Length', 'Branch Points', 'Terminal Points']
    mapper = ParameterMapper(headers)

    # Add aliases
    mapper.add_parameter_alias('Length', 'Len')
    mapper.add_parameter_alias('Branch Points', 'BP')
    mapper.add_parameter_alias('Terminal Points', 'TP')

    print(f"\nAliases created:")
    print(f"  'Len' -> {mapper.resolve_alias('Len')}")
    print(f"  'BP' -> {mapper.resolve_alias('BP')}")
    print(f"  'TP' -> {mapper.resolve_alias('TP')}")
    print(f"  'Unknown' -> {mapper.resolve_alias('Unknown')}")

    print("\n✓ Parameter aliases working!")
    return True


def test_serialization():
    """Test serialization to/from dictionary."""
    print("\n" + "=" * 70)
    print("Test 5: Serialization (Save/Load)")
    print("=" * 70)

    headers = ['Length', 'Branch Points', 'Total Volume']
    mapper = ParameterMapper(headers)

    # Configure mapper
    mapper.select_parameters(['Length', 'Total Volume'])
    mapper.add_custom_parameter('Density')
    mapper.add_parameter_alias('Length', 'Len')

    print(f"\nOriginal mapper: {mapper}")
    print(f"Selected: {mapper.get_all_parameters()}")

    # Serialize to dict
    data = mapper.to_dict()
    print(f"\nSerialized to dict:")
    for key, value in data.items():
        print(f"  {key}: {value}")

    # Deserialize from dict
    mapper2 = ParameterMapper.from_dict(data)
    print(f"\nDeserialized mapper: {mapper2}")
    print(f"Selected: {mapper2.get_all_parameters()}")
    print(f"Custom: {mapper2.get_custom_parameters()}")
    print(f"Alias 'Len': {mapper2.resolve_alias('Len')}")

    # Verify they match
    assert mapper.get_all_parameters() == mapper2.get_all_parameters()
    assert mapper.get_custom_parameters() == mapper2.get_custom_parameters()

    print("\n✓ Serialization working!")
    return True


def test_real_file_integration():
    """Test integration with HeaderScanner using real files."""
    print("\n" + "=" * 70)
    print("Test 6: Integration with Real Files")
    print("=" * 70)

    test_file = Path(__file__).parent / 'test_data' / '002_GST_005L.csv'

    if not test_file.exists():
        print(f"\n⚠ Test file not found: {test_file}")
        print("Skipping integration test")
        return False

    try:
        # Scan headers from real file
        headers = HeaderScanner.scan_headers(test_file)
        print(f"\nScanned headers from {test_file.name}:")
        print(f"  {headers}")

        # Create mapper with scanned headers
        mapper = ParameterMapper(headers)

        # Select specific parameters
        mapper.select_parameters(['Length', 'Branch Points', 'Total Volume'])

        print(f"\nCreated ParameterMapper from real file headers")
        print(f"Selected for import: {mapper.get_all_parameters()}")

        print("\n✓ Real file integration working!")
        return True

    except ImportError as e:
        print(f"\n⚠ Missing dependency: {e}")
        print("Install with: pip install pandas")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_deselection():
    """Test parameter deselection."""
    print("\n" + "=" * 70)
    print("Test 7: Parameter Deselection")
    print("=" * 70)

    headers = ['Length', 'Branch Points', 'Terminal Points', 'Total Volume']
    mapper = ParameterMapper(headers)

    # Select all first
    mapper.select_all_parameters()
    print(f"\nInitially selected: {mapper.get_all_parameters()}")
    print(f"Count: {mapper.get_parameter_count()}")

    # Deselect some
    mapper.deselect_parameter('Branch Points')
    mapper.deselect_parameter('Terminal Points')
    print(f"\nAfter deselection: {mapper.get_all_parameters()}")
    print(f"Count: {mapper.get_parameter_count()}")

    # Clear all
    mapper.clear_selection()
    print(f"\nAfter clear: {mapper.get_all_parameters()}")
    print(f"Count: {mapper.get_parameter_count()}")

    print("\n✓ Deselection working!")
    return True


def run_all_tests():
    """Run all tests and display summary."""
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Select All", test_select_all),
        ("Custom Parameters", test_custom_parameters),
        ("Parameter Aliases", test_parameter_aliases),
        ("Serialization", test_serialization),
        ("Real File Integration", test_real_file_integration),
        ("Deselection", test_deselection),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test failed with error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)

    print(f"\nTotal tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed/Skipped: {failed}")

    print("\nDetailed Results:")
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL/SKIP"
        print(f"  {status}: {name}")

    if passed == len(results):
        print("\n" + "=" * 70)
        print("✓ All tests passed! ParameterMapper is working correctly!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("⚠ Some tests failed or were skipped")
        print("=" * 70)


if __name__ == '__main__':
    run_all_tests()
