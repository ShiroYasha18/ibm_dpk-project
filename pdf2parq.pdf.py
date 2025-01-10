import ast
import os
import sys
from data_processing.runtime.pure_python import PythonTransformLauncher
from pdf2parquet.dpk_pdf2parquet.transform_python import Pdf2ParquetPythonTransformConfiguration
from typing_extensions import runtime
from data_processing.utils import ParamsUtils
input_folder = 'path/to/input/folder'

output_folder = 'path/to/output/folder'

local_conf= {
    "input_folder":input_folder,
    "output_folder":output_folder,
}

params = {
    "data_local_config":ParamsUtils.convert_to_ast(local_conf),
    "data_files_to_use":ast.literal_eval("['.pdf' , '.jpeg']"),
    "runtime_pipeline_id": "pipeline_id",
    "runtime_job_id":"job_id",
    "pdf2parquet_double_precision":0,

}

sys.argv =ParamsUtils.dict_to_req(d=params)
launcher = PythonTransformLauncher(runtime_config= Pdf2ParquetPythonTransformConfiguration())
launcher.launch()