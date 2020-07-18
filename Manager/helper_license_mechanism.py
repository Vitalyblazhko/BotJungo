import getpass
import platform

from Manager.helper_base import HelperBase

class HelperLicenseMechanism:

    def __init__(self):
        global user_name
        user_name = getpass.getuser()
        global platform_name
        platform_name = platform.system()

    def confirm_string_existence(self, string_to_check):
        return HelperBase.read_text_file_return_result(HelperBase.create_test_dir("output") + "/sdt_out.txt", string_to_check)