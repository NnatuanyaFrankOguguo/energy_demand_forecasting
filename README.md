🛠️ Local Setup Guide
Follow the steps below to install and run this project correctly in any development environment.

✅ 1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/your-username/energy_demand_forecasting.git
cd energy_demand_forecasting
✅ 2. Create and Activate a Virtual Environment
On Windows:
bash
Copy
Edit
python -m venv .venv
.\.venv\Scripts\activate
On macOS/Linux:
bash
Copy
Edit
python3 -m venv .venv
source .venv/bin/activate
✅ 3. Install Project in Editable Mode
This step makes internal modules (like pipeline and loggerInfo) importable from anywhere in the project.

First, create a setup.py in the root folder with this content:
python
Copy
Edit
from setuptools import setup, find_packages

setup(
    name="energy_demand_forecasting",
    version="0.1",
    packages=find_packages(),      # includes subfolders like `pipeline/`
    py_modules=["loggerInfo"],     # includes top-level .py files
)
Then install it:
bash
Copy
Edit
pip install -e .
✅ 4. Install Project Dependencies
bash
Copy
Edit
pip install -r requirements.txt
✅ 5. Run Any Script Without Import Errors
You can now run any script, from anywhere:

From terminal:
bash
Copy
Edit
python -m pipeline.fetch_energy
python -m pipeline.transform
✅ Use the -m flag to run modules inside packages.

Or directly from VS Code or Jupyter:
python
Copy
Edit
from loggerInfo import get_logger
from pipeline.config import EIA_API_KEY
✅ 6. Optional: Jupyter Notebook Setup
If using notebooks:

bash
Copy
Edit
pip install notebook ipykernel
python -m ipykernel install --user --name=energy-env
Then select the energy-env kernel in Jupyter or VS Code.



Always run scripts using the `-m` flag from the project root:

```bash
python -m pipeline.fetch_energy