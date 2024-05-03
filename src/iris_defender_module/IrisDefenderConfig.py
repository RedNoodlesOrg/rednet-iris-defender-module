#   -------------------------------------------------------------
#   Copyright (c) RedNoodles. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
module_name = "IrisDefender"
module_description = "Pipeline for Defender Logs"
interface_version = "1.2.0"
module_version = "0.1.0"

pipeline_support = True
pipeline_info = {
    "pipeline_internal_name": "defender_pipeline",
    "pipeline_human_name": "Defender Pipeline",
    "pipeline_args": ["testarg1"],
    "pipeline_update_support": True,
    "pipeline_import_support": True,
}


module_configuration: list[dict] = []
