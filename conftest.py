import platform
from pathlib import Path

import distro
import pytest

from Manager.application_manager import ApplicationManager
from Manager.helper_base import HelperBase
from Manager.helper_email_report import EmailReport


# @pytest.fixture(autouse=True)
# def env_setup(monkeypatch):
#     TEST_DIR = os.path.dirname(os.path.abspath(__file__))
#     PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
#     sys.path.insert(0, PROJECT_DIR)
#     monkeypatch.setenv('TEST_DIR', 'os.path.dirname(os.path.abspath(__file__))')
#     monkeypatch.setenv('PROJECT_DIR', 'os.path.abspath(os.path.join(TEST_DIR, os.pardir))')
# from Manager.application_manager import ApplicationManager
#
#

# @pytest.hookimpl(tryfirst=True)
# def pytest_configure(config):
#     config.option.htmlpath = '/out/report/report.html'

option = None

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    os_platform = platform.system()
    global os_version

    if os_platform == "Linux":
        os_version = distro.linux_distribution(full_distribution_name=False)[0] + \
                     distro.linux_distribution(full_distribution_name=False)[1]
    elif os_platform == "Windows":
        os_version = os_platform + platform.release()

    global option
    option = config.option

    config._links = None
    if not config.option.htmlpath:
        reports_dir = Path(HelperBase.get_project_dir()+"/outputs/", "reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        report = str(reports_dir)+"/"+ f"report_"+str(os_version)+".html"
        config.option.htmlpath = report
        config.option.self_contained_html = True

def pytest_html_results_table_header(cells):
    cells.pop()

def pytest_html_results_table_row(report, cells):
    cells.pop()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)

    # if call.when == 'call':
    #     outcome.result.my_data = "%(asctime)s [%(levelname)8s] (%(filename)s:%(lineno)s) %(message)s"

# Test arguments
@pytest.fixture
def email_pytest_report(request):
    return request.config.getoption("--email_pytest_report")

# Command line options:
def pytest_addoption(parser):
    parser.addoption("--email_pytest_report",
                     dest="email_pytest_report",
                     help="Email pytest report: Y or N",
                     default="N")
    parser.addoption("--testlink_project", action="store",
                     default=None)
    parser.addoption("--testlink_plan", action="store",
                     default=None)
    parser.addoption("--testlink_build", action="store",
                     default=None)
    parser.addoption("--testlink_platform", action="store",
                     default=None)

def pytest_terminal_summary(terminalreporter, exitstatus):
    if terminalreporter.config.getoption("--email_pytest_report").lower() == 'y':
        email_obj = EmailReport()
        # Send html formatted email body message with pytest report as an attachment
        email_obj.send_test_report_email(html_body_flag=True, attachment_flag=True, report_file_path='default')

    # if terminalreporter.config.getoption("--testlink_project") is not None \
    #         and terminalreporter.config.getoption("--testlink_plan") is not None \
    #         and terminalreporter.config.getoption("--testlink_build") is not None \
    #         and terminalreporter.config.getoption("--testlink_platform") is not None:
    #     testlink = TestLink(terminalreporter.config.getoption("--testlink_project"),
    #                         terminalreporter.config.getoption("--testlink_plan"),
    #                         terminalreporter.config.getoption("--testlink_build"),
    #                         terminalreporter.config.getoption("--testlink_platform"))



# @pytest.fixture(scope="session", autouse=True)
# def email_sending():
#     email_obj = EmailReport()
#     #1. Send html formatted email body message with pytest report as an attachment
#     #Here log/pytest_report.html is a default file. To generate pytest_report.html file use following command to the test e.g. py.test --html = log/pytest_report.html
#     yield
#
#     #email_obj.send_test_report_email(html_body_flag=True,attachment_flag=True,report_file_path= 'default')