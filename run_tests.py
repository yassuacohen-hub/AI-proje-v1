import os
import sys
import pytest

# Change to the Huginn Data Insights directory
os.chdir("c:/Huginn Data Projesi/Huginn Data Insights")

# Add the src directory to the path
src_path = os.path.join(os.getcwd(), "src")
sys.path.insert(0, src_path)

# Run the tests
result = pytest.main(["tests/test_gece_besleme.py", "-v"])
sys.exit(result)