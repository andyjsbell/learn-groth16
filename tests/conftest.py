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

@pytest.fixture
def homework7_contract(acct1, project):
    return acct1.deploy(project.Homework7)

@pytest.fixture
def homework8_contract(acct1, project):
    return acct1.deploy(project.Homework8)