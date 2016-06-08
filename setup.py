from pip.req import parse_requirements
from setuptools import setup, find_packages

requirements = parse_requirements("requirements_python2.txt", session=False)
requirements_list = [str(module.req) for module in requirements]

setup(
    name='smart_grid_controller',
    version="0.0.1",
    packages=find_packages(),
    install_requires=requirements_list
)
