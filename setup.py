from setuptools import setup, find_packages

setup(
    name="energy_demand_forecasting",
    version="0.1",
    packages=find_packages(),  # includes pipeline/
    py_modules=["loggerInfo"],  # includes loggerInfo.py
)