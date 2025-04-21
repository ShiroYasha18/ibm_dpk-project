import ast
import os
import sys

from data_processing.runtime.pure_python import PythonTransformLauncher
from data_processing.utils import ParamsUtils
from pdf2parquet_transform_python import Pdf2ParquetPythonTransformConfiguration

input_folder = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerSheet/Handwritten/"
output_folder = "/Users/ayrafraihan/Desktop/pythonProject1/out"

local_conf = {
    "input_folder": input_folder,
    "output_folder": output_folder,
}

params = {
    "data_local_config": ParamsUtils.convert_to_ast(local_conf),
    "data_files_to_use": ast.literal_eval("['.pdf', '.jpeg']"),
    "pdf2parquet_do_ocr": True,
    "pdf2parquet_ocr_engine": "tesseract_cli",
    "runtime_pipeline_id": "pipeline_id",
    "runtime_job_id": "job_id",
    "pdf2parquet_double_precision": 0,
}

sys.argv = ParamsUtils.dict_to_req(d=params)

launcher = PythonTransformLauncher(runtime_config=Pdf2ParquetPythonTransformConfiguration())
launcher.launch()
