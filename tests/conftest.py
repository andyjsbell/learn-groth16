import pytest


@pytest.fixture
def acct1(accounts):
    return accounts[0]


@pytest.fixture
def homework3_contract(acct1, project):
    return acct1.deploy(project.Homework3)
