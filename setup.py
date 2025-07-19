from setuptools import setup, find_packages

setup(
    name="energy_demand_forecasting",
    version="0.1",
    packages=["pipeline", "quality"],  # includes pipeline/
    py_modules=["loggerInfo"],  # includes loggerInfo.py
)