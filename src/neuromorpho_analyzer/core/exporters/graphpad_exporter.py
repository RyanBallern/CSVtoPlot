"""Export data in GraphPad Prism format."""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import pandas as pd

from .parameter_selector import ExportParameterSelector
from ..database.base import DatabaseBase


class GraphPadExporter:
    """Exports data in GraphPad Prism .pzfx format."""

    def __init__(self, parameter_selector: ExportParameterSelector):
        """Initialize GraphPad exporter.

        Args:
            parameter_selector: Parameter selector for export
        """
        self.param_selector = parameter_selector

    def export(self, assay_ids: List[int], output_dir: Path,
               database: DatabaseBase) -> Path:
        """Export .pzfx file for GraphPad Prism.

        Args:
            assay_ids: List of assay IDs to export
            output_dir: Output directory
            database: Database interface

        Returns:
            Path to created .pzfx file
        """
        # Get data from all assays
        parameters = self.param_selector.get_selected()
        dfs = []
        for assay_id in assay_ids:
            assay_df = database.get_measurements(assay_id, parameters=parameters)
            if not assay_df.empty:
                assay_df['assay_id'] = assay_id
                dfs.append(assay_df)

        # Combine all data
        if dfs:
            df = pd.concat(dfs, ignore_index=True)
        else:
            df = pd.DataFrame()

        # Create XML structure
        root = ET.Element('GraphPadPrismFile', {
            'xmlns': 'http://graphpad.com/prism/Prism.htm',
            'PrismXMLVersion': '5.00'
        })

        # Add created date
        created = ET.SubElement(root, 'Created')
        created_platform = ET.SubElement(created, 'OriginalVersion', {
            'CreatedByProgram': 'CSVtoPlot Analyzer',
            'CreatedByVersion': '1.0.0',
            'Login': 'User',
            'DateTime': datetime.now().isoformat()
        })

        # Add tables for each parameter
        for param in parameters:
            self._add_parameter_table(root, df, param)

        # Format and save
        xml_str = self._prettify_xml(root)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        assay_indices = '_'.join(str(aid) for aid in sorted(assay_ids))
        filename = f'graphpad_{timestamp}_assays{assay_indices}.pzfx'
        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)

        return output_path

    def _add_parameter_table(self, root: ET.Element,
                             df: pd.DataFrame, parameter: str) -> None:
        """Add a table for a specific parameter.

        Args:
            root: Root XML element
            df: DataFrame with measurement data
            parameter: Parameter name
        """
        # Filter data for this parameter
        param_data = df[df['parameter_name'] == parameter]
        conditions = sorted(param_data['condition'].unique())

        if len(conditions) == 0:
            return

        # Create table element
        table = ET.SubElement(root, 'Table', {
            'ID': f'Table_{parameter.replace(" ", "_")}',
            'XFormat': 'none',
            'TableType': 'OneWay',
            'EVFormat': 'AsteriskAfterNumber'
        })

        title = ET.SubElement(table, 'Title')
        title.text = parameter

        # Add columns for each condition
        for condition in conditions:
            cond_data = param_data[
                param_data['condition'] == condition
            ]['value']

            if len(cond_data) == 0:
                continue

            col = ET.SubElement(table, 'YColumn', {
                'Width': '81',
                'Decimals': '3',
                'Subcolumns': '1'
            })

            col_title = ET.SubElement(col, 'Title')
            col_title.text = condition

            # Add values
            for value in cond_data:
                subcolumn = ET.SubElement(col, 'Subcolumn')
                d = ET.SubElement(subcolumn, 'd')
                d.text = str(value)

    def _prettify_xml(self, elem: ET.Element) -> str:
        """Return a pretty-printed XML string.

        Args:
            elem: XML element to format

        Returns:
            Formatted XML string
        """
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
