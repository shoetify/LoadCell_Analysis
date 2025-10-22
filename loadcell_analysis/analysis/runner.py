from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Optional

import yaml

from .data_analyzer import DataAnalyzer
from .utils import LoadCell_Util

if TYPE_CHECKING:
    import pandas as pd

ProgressCallback = Optional[Callable[[str], None]]


@dataclass
class AnalysisResult:
    name: str
    dataframe: "pd.DataFrame"
    mean_table: List[List[float]]
    rms_table: List[List[float]]
    output_path: Optional[Path]


def run_analysis(config_path, log_path, data_root, output_dir=None, auto_export=True,
                progress: ProgressCallback = None):
    """
    Execute the full analysis pipeline.

    Parameters
    ----------
    config_path : str or Path
        Path to the YAML configuration file.
    log_path : str or Path
        Path to the experiment log excel file.
    data_root : str or Path
        Directory that contains the raw load cell data files referenced in the log.
    output_dir : str or Path, optional
        Directory to store generated Excel reports. Defaults to the directory of each data file.
    auto_export : bool, optional
        Whether to automatically write Excel summaries. Defaults to True.
    progress : callable, optional
        Callback that receives status messages.

    Returns
    -------
    dict
        Dictionary containing parsed configuration and a list of AnalysisResult entries.
    """
    config_path = Path(config_path).resolve()
    log_path = Path(log_path).resolve()
    data_root = Path(data_root).resolve() if data_root else log_path.parent.resolve()
    output_dir = Path(output_dir).resolve() if output_dir else None

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    if not log_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_path}")
    if not data_root.exists():
        raise FileNotFoundError(f"Data directory not found: {data_root}")
    if output_dir and not output_dir.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")

    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    LoadCell_Util.emit_message("Config file reading successfully ...", progress)

    log_table = LoadCell_Util.parse_excel(str(log_path))
    wind_speed_a, wind_speed_b = LoadCell_Util.extract_numbers_from_string(
        config['Data_reading']['WindSpeed_relationship'])

    stable_time_0Hz = config['Data_reading']['Stable_time_0Hz']
    stable_time_others = config['Data_reading']['Stable_time_others']
    gap_before_next_wind_speed = config['Data_reading']['Gap_before_next_wind_speed']
    sample_rate = config['Data_reading']['Sample_rate']

    average = config['Data_calculation']['smoothy_average_points']
    deg = config['Data_calculation']['polynomial_fitting_degree']
    filter_freq = config['Data_calculation']['lowpass_filtered_frequency']

    test_condition = {
        'projective_area': config['Data_calculation']['cylinder_diameter'] *
                           config['Data_calculation']['test_section_length']
    }

    if not test_condition['projective_area'] > 0:
        raise TypeError('Projective area of the module should be larger than 0')

    proceeded_tables = LoadCell_Util.proceed_table(
        log_table,
        stable_time_0Hz,
        stable_time_others,
        gap_before_next_wind_speed,
        wind_speed_a,
        wind_speed_b,
        progress=progress
    )

    results: List[AnalysisResult] = []

    for proceeded_table in proceeded_tables:
        mean_table, rms_table = DataAnalyzer.analyze(
            proceeded_table,
            sample_rate,
            stable_time_others,
            stable_time_0Hz,
            deg,
            average,
            filter_freq,
            data_root=data_root,
            progress=progress
        )

        dataframe = LoadCell_Util.build_result_dataframe(proceeded_table, mean_table, rms_table, test_condition)

        output_path = None
        if auto_export:
            output_path = LoadCell_Util.toExcel(
                proceeded_table,
                mean_table,
                rms_table,
                test_condition,
                proceeded_table[5][0],
                output_dir=output_dir,
                data_root=data_root,
                progress=progress
            )

        result_name = Path(proceeded_table[5][0]).stem
        results.append(AnalysisResult(result_name, dataframe, mean_table, rms_table, output_path))

    return {
        "config": config,
        "results": results,
        "test_condition": test_condition,
        "proceeded_tables": proceeded_tables
    }
