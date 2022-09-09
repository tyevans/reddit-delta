import json
from pathlib import Path

import pytest


@pytest.fixture
def data_fixture_path():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def popular_data_001(data_fixture_path):
    with open(data_fixture_path / "001-popular.json") as fd:
        return json.load(fd)
