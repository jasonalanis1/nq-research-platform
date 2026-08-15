"""
conftest.py
============
pytest automatically loads this file before running any tests. Its only
job here is to make sure Python can find the code in src/ when the tests
try to import it -- since src/ isn't normally on Python's search path.

You don't need to understand pytest internals to use this project -- just
know that running `pytest` from the project folder will find and run
every test in tests/ automatically.
"""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))
