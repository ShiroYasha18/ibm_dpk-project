import ast
import os
import sys

sys.path.append(os.path.abspath('/Users/tanishta/Desktop/ibm_dpk-proj'))
sys.path.append(os.path.abspath('/Users/tanishta/Desktop/ibm_dpk-proj/pdf2parquet'))
sys.path.append(os.path.abspath('/Users/tanishta/Desktop/ibm_dpk-proj/data_processing'))
print("sys.path:", sys.path)

try:
    import data_processing
    print("data_processing module found!")
except ModuleNotFoundError:
    print("data_processing module not found!")

sys.path.append('/Users/tanishta/Desktop/ibm_dpk-proj/pdf2parquet')
from data_processing.runtime.pure_python import PythonTransformLauncher
from pdf2parquet.dpk_pdf2parquet.transform_python import Pdf2ParquetPythonTransformConfiguration
from typing_extensions import runtime
from data_processing.utils import ParamsUtils
import logging

def convert_pdf_to_parquet(input_folder, output_folder):
    # Local configuration for input and output folder
    local_conf = {
        "input_folder": input_folder,
        "output_folder": output_folder,
    }

    # Parameters for the conversion process
    params = {
        "data_local_config": ParamsUtils.convert_to_ast(local_conf),
        "data_files_to_use": ast.literal_eval("['.pdf' , '.jpeg']"),
        "runtime_pipeline_id": "pipeline_id",
        "runtime_job_id": "job_id",
        "pdf2parquet_double_precision": 0,
    }

    # Logging parsed local configuration
    print("Parsed data_local_config:", ParamsUtils.convert_to_ast(local_conf))

    # Set up arguments and initialize the launcher
    sys.argv = ParamsUtils.dict_to_req(d=params)
    launcher = PythonTransformLauncher(runtime_config=Pdf2ParquetPythonTransformConfiguration())
    launcher.launch()