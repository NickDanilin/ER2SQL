import pytest
import os

if __name__ == "__main__":
    pytest.main(["-v", "--tb=short", "-m", "not slow"])