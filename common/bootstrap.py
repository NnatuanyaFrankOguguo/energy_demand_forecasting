# common/bootstrap.py

import sys
import os

def setup_project_path():
    """
    Adds the project root directory to sys.path
    so that internal packages like 'common', 'pipeline', and 'quality'
    can be imported no matter where the script is run from.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)