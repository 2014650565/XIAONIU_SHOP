import pytest


@pytest.fixture(autouse=True)
def reset_data():
    print("ORDER: reset")


@pytest.fixture
def login():
    print("ORDER: login")


def test_order(login):
    print("ORDER: test")
