"""Command-line interface for Neuromorpho Analyzer."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .core.database import SQLiteDatabase
from .core.importers import UnifiedImporter, FileScanner
from .core.processors import StatisticsEngine, DensityCalculator, RepresentativeFileAnalyzer
from .core.exporters import ExcelExporter, ExportParameterSelector, StatisticsTableExporter
from .core.profiles import AnalysisProfile, ProfileManager


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="neuromorpho-analyzer",
        description="Neuromorpho Analyzer - Neuromorphological data analysis tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import data from directory
  neuromorpho-analyzer import ./data -d analysis.db

  # Run statistics on database
  neuromorpho-analyzer stats -d analysis.db --assay 1

  # Export to Excel
  neuromorpho-analyzer export -d analysis.db -o ./output --format excel

  # Find representative files
  neuromorpho-analyzer representative -d analysis.db --assay 1

  # Launch GUI
  neuromorpho-analyzer gui
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # GUI command
    gui_parser = subparsers.add_parser("gui", help="Launch graphical interface")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import data files")
    import_parser.add_argument("path", help="File or directory to import")
    import_parser.add_argument("-d", "--database", required=True, help="Database file path")
    import_parser.add_argument("-n", "--name", help="Assay name (default: directory name)")
    import_parser.add_argument("--recursive", action="store_true", help="Scan subdirectories")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Run statistical analysis")
    stats_parser.add_argument("-d", "--database", required=True, help="Database file path")
    stats_parser.add_argument("--assay", type=int, required=True, help="Assay ID to analyze")
    stats_parser.add_argument("-p", "--parameters", nargs="+", help="Parameters to analyze")
    stats_parser.add_argument("-o", "--output", help="Output file for results")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export data")
    export_parser.add_argument("-d", "--database", required=True, help="Database file path")
    export_parser.add_argument("--assay", type=int, required=True, help="Assay ID to export")
    export_parser.add_argument("-o", "--output", required=True, help="Output directory")
    export_parser.add_argument("-f", "--format", choices=["excel", "csv", "stats"],
                               default="excel", help="Export format")
    export_parser.add_argument("-p", "--parameters", nargs="+", help="Parameters to export")

    # Representative command
    rep_parser = subparsers.add_parser("representative", help="Find representative files")
    rep_parser.add_argument("-d", "--database", required=True, help="Database file path")
    rep_parser.add_argument("--assay", type=int, required=True, help="Assay ID")
    rep_parser.add_argument("-p", "--parameters", nargs="+", help="Parameters for distance calculation")
    rep_parser.add_argument("-n", "--top", type=int, default=3, help="Number of top files per condition")
    rep_parser.add_argument("-o", "--output", help="Output CSV file")

    # Density command
    density_parser = subparsers.add_parser("density", help="Calculate structure density")
    density_parser.add_argument("-d", "--database", required=True, help="Database file path")
    density_parser.add_argument("--assay", type=int, required=True, help="Assay ID")
    density_parser.add_argument("--area", type=float, default=12.2647,
                                help="Image area in µm² (default: 3.5021² = 12.2647)")

    # List command
    list_parser = subparsers.add_parser("list", help="List database contents")
    list_parser.add_argument("-d", "--database", required=True, help="Database file path")
    list_parser.add_argument("--assays", action="store_true", help="List assays")
    list_parser.add_argument("--conditions", type=int, metavar="ASSAY_ID", help="List conditions for assay")
    list_parser.add_argument("--parameters", type=int, metavar="ASSAY_ID", help="List parameters for assay")

    return parser


def cmd_gui(args):
    """Launch GUI."""
    from .app import main as gui_main
    gui_main()


def cmd_import(args):
    """Import data files."""
    db = SQLiteDatabase(args.database)
    db.connect()

    path = Path(args.path)

    if path.is_file():
        files = [{'path': path, 'condition': path.stem.split('_')[1] if '_' in path.stem else 'Unknown'}]
    else:
        scanner = FileScanner(path)
        files = scanner.scan_files()

    if not files:
        print("No supported files found.")
        db.disconnect()
        return 1

    assay_name = args.name or path.name
    assay_id = db.insert_assay(assay_name)

    print(f"Created assay '{assay_name}' (ID: {assay_id})")

    total = 0
    for file_info in files:
        filepath = file_info['path'] if isinstance(file_info, dict) else file_info
        condition = file_info.get('condition', 'Unknown') if isinstance(file_info, dict) else 'Unknown'

        try:
            df = UnifiedImporter.import_file(str(filepath))
            count = db.insert_measurements(
                assay_id, df,
                source_file=filepath.name if hasattr(filepath, 'name') else str(filepath),
                condition=condition
            )
            total += count
            print(f"  Imported: {filepath.name if hasattr(filepath, 'name') else filepath} ({count} rows)")
        except Exception as e:
            print(f"  Error: {filepath}: {e}")

    print(f"\nTotal: {total} measurements imported")
    db.disconnect()
    return 0


def cmd_stats(args):
    """Run statistical analysis."""
    db = SQLiteDatabase(args.database)
    db.connect()

    df = db.get_measurements(args.assay)
    if df.empty:
        print("No data found for assay.")
        db.disconnect()
        return 1

    stats = StatisticsEngine()
    parameters = args.parameters or db.get_parameters(args.assay)

    print("=" * 60)
    print("STATISTICAL ANALYSIS")
    print("=" * 60)

    for param in parameters:
        param_df = df[df['parameter_name'] == param]
        if param_df.empty:
            continue

        print(f"\nParameter: {param}")
        print("-" * 40)

        try:
            result = stats.auto_compare(param_df, 'value', 'condition')
            main_test = result.get('main_test')

            if main_test:
                print(f"Test: {main_test.test_name}")
                print(f"Statistic: {main_test.statistic:.4f}")
                print(f"P-value: {main_test.p_value:.4e}")
                print(f"Significant: {'Yes' if main_test.significant else 'No'}")

                post_hoc = result.get('post_hoc_tests', [])
                if post_hoc:
                    print("\nPost-hoc comparisons:")
                    for test in post_hoc:
                        sig = '*' if test.p_value < 0.05 else ''
                        print(f"  {test.group1} vs {test.group2}: p={test.p_value:.4e} {sig}")

        except Exception as e:
            print(f"Error: {e}")

    db.disconnect()
    return 0


def cmd_export(args):
    """Export data."""
    db = SQLiteDatabase(args.database)
    db.connect()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    stats = StatisticsEngine()
    param_selector = ExportParameterSelector(db)

    if args.parameters:
        param_selector.select_parameters(args.parameters)
    else:
        param_selector.select_all(args.assay)

    if args.format == "excel":
        exporter = ExcelExporter(param_selector, stats)
        output_path = exporter.export([args.assay], output_dir, db)
        print(f"Exported to: {output_path}")

    elif args.format == "stats":
        df = db.get_measurements(args.assay)
        parameters = args.parameters or db.get_parameters(args.assay)

        if parameters:
            param = parameters[0]
            param_df = df[df['parameter_name'] == param]
            data_dict = {}
            for cond in param_df['condition'].unique():
                data_dict[cond] = param_df[param_df['condition'] == cond]['value']

            exporter = StatisticsTableExporter(stats)
            tables = exporter.create_statistics_tables(data_dict, param)
            output_path = output_dir / f"statistics_{param}.xlsx"
            exporter.export_to_excel(tables, output_path)
            print(f"Exported to: {output_path}")

    db.disconnect()
    return 0


def cmd_representative(args):
    """Find representative files."""
    db = SQLiteDatabase(args.database)
    db.connect()

    analyzer = RepresentativeFileAnalyzer(db)
    parameters = args.parameters or db.get_parameters(args.assay)

    results = analyzer.analyze([args.assay], parameters)

    print("=" * 60)
    print("REPRESENTATIVE FILES")
    print("=" * 60)

    for condition in sorted(results['condition'].unique()):
        print(f"\n{condition}:")
        cond_results = results[results['condition'] == condition].head(args.top)
        for _, row in cond_results.iterrows():
            print(f"  {row['rank']}. {row['file']} (distance: {row['distance_from_average']:.4f})")

    if args.output:
        analyzer.export_to_csv(results, Path(args.output))
        print(f"\nExported to: {args.output}")

    db.disconnect()
    return 0


def cmd_density(args):
    """Calculate structure density."""
    from .core.processors import DensityConfig

    db = SQLiteDatabase(args.database)
    db.connect()

    config = DensityConfig(image_area_um2=args.area)
    calc = DensityCalculator(config)

    df = db.get_measurements(args.assay)

    print("=" * 60)
    print("DENSITY ANALYSIS")
    print(f"Image area: {args.area:.4f} µm²")
    print("=" * 60)

    for condition in sorted(df['condition'].unique()):
        cond_df = df[df['condition'] == condition]
        count = len(cond_df)
        result = calc.calculate_density_from_count(count)

        print(f"\n{condition}:")
        print(f"  Count: {count}")
        print(f"  Density: {result.density:.6f} /µm²")
        print(f"  Density: {result.density_per_mm2:.2f} /mm²")

    db.disconnect()
    return 0


def cmd_list(args):
    """List database contents."""
    db = SQLiteDatabase(args.database)
    db.connect()

    if args.assays:
        assays = db.list_assays()
        print("Assays:")
        for assay in assays:
            print(f"  {assay['id']}: {assay['name']}")

    if args.conditions:
        conditions = db.get_conditions(args.conditions)
        print(f"Conditions for assay {args.conditions}:")
        for cond in conditions:
            print(f"  - {cond}")

    if args.parameters:
        parameters = db.get_parameters(args.parameters)
        print(f"Parameters for assay {args.parameters}:")
        for param in parameters:
            print(f"  - {param}")

    db.disconnect()
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "gui": cmd_gui,
        "import": cmd_import,
        "stats": cmd_stats,
        "export": cmd_export,
        "representative": cmd_representative,
        "density": cmd_density,
        "list": cmd_list,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        try:
            return cmd_func(args) or 0
        except KeyboardInterrupt:
            print("\nAborted.")
            return 130
        except Exception as e:
            print(f"Error: {e}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
