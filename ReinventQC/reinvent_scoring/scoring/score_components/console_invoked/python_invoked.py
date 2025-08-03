import importlib
import json
import os
import shutil
import subprocess
from sys import stdout
import tempfile
import time
# import django
import datetime
import copy

from ReinventQC.reinvent_scoring.scoring.score_summary import ComponentSummary


import numpy as np
from typing import List, Tuple

# from ReinventQC.reinvent_scoring.scoring.utils import _is_development_environment

from ReinventQC.reinvent_scoring.scoring.component_parameters import ComponentParameters
from ReinventQC.reinvent_scoring.scoring.score_components.console_invoked.base_console_invoked_component import \
    BaseConsoleInvokedComponent

class PythonInvoked(BaseConsoleInvokedComponent):
    def __init__(self, parameters: ComponentParameters, module_function="main"):
        super().__init__(parameters)
        python_function = self.parameters.specific_parameters.get(
            self.component_specific_parameters.CUSTOM_FUNCTION, "main"
        )
        if isinstance(python_function, str):
            module_pkg = self.parameters.specific_parameters[self.component_specific_parameters.CUSTOM_MODULE]
            if isinstance(module_pkg, str):
                module_pkg = importlib.import_module(module_pkg)
            python_function = getattr(module_pkg, python_function, parameters)
        self.caller = python_function

    def _calculate_score(self, smiles: List[str], step) -> np.array:
        config = self.parameters.specific_parameters.get(
            self.component_specific_parameters.CUSTOM_FUNCTION_CONFIG, {}
        )
        smiles_ids, scores = self.caller(smiles, config=config)

        # apply transformation
        transform_params = self.parameters.specific_parameters.get(
            self.component_specific_parameters.TRANSFORMATION, {}
        )
        transformed_scores = self._transformation_function(scores, transform_params)

        return np.array(transformed_scores), np.array(scores)

    def _create_command(self, step, input_json_path, output_json_path):
        return []
