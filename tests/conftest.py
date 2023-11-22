import pytest


@pytest.fixture
def acct1(accounts):
    return accounts[0]


@pytest.fixture
def homework3_contract(acct1, project):
    return acct1.deploy(project.Homework3)

@pytest.fixture
def homework4_contract(acct1, project):
    return acct1.deploy(project.Homework4)

@pytest.fixture
def homework6_contract(acct1, project):
    return acct1.deploy(project.Homework6)
