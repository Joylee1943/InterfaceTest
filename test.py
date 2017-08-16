
import allure
import pytest


def pytest_configure(config):
    allure.environment(report='Allure report', browser=u'Я.Браузер')


@pytest.fixture(scope="session")
def app_host_name():
    host_name = "my.host.local"
    allure.environment(hostname=host_name)
    return host_name


@pytest.mark.parametrize('country', ('USA', 'Germany', u'Россия', u'Япония'))
def test_minor(country):
    allure.environment(country=country)
    assert country