# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os 
import sys

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../src'))
sys.path.insert(0, os.path.abspath('../troubleshoot'))


project = 'Browsermon'
copyright = '2023, Eunomatix'
author = 'Eunomatix'
release = '1.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.todo','sphinx.ext.viewcode','sphinx.ext.autodoc',]

autodoc_modules  = [
    'src.rst',
    'src.utils.rst',
    'src.controller',
    'src.readers.edge_reader',
    'src.readers.firefox_reader',
    'src.utils.caching',
    'src.utils.launcher',
    'src.utils.metadata',
    'src.utils.handlers',
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


autodoc_mock_imports = ["browsermon"]
autodoc_default_options = {
    'members': True,
}
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
