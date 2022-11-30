"""
Minimal test to validate that the demo API package is successfully installed
"""
from demo.version import __version__


def test_installed():
    """
    Validate that the demo package can be imported
    """
    assert isinstance(__version__, str)
