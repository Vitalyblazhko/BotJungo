import concurrent.futures
import logging
import sys
import time
from argparse import ArgumentParser
from smtpd import usage

import pytest
from pynput.keyboard import Controller, Key
from Manager.application_manager import ApplicationManager
from Manager.helper_base import HelperBase
from testlink import TestlinkAPIClient, TestLinkHelper, TestGenReporter, TestlinkAPIGeneric
from testlink.testlinkerrors import TLResponseError
from conftest import option

class TestCompilation:
    @pytest.fixture(scope="class", autouse=True)
    def session_initializing(self):
        global application_manager
        application_manager = ApplicationManager()
        global LOGGER
        LOGGER = logging.getLogger(__name__)
        global my_test_link
        my_test_link = ApplicationManager.get_my_test_link()

        LOGGER.info(HelperBase.get_message("info_start_suit"))
        yield
        LOGGER.info(HelperBase.get_message("info_finish_suit"))

    @pytest.fixture()
    def set_up(self):
        application_manager.get_helper_base().set_default_yml()
        application_manager.get_helper_base().remove_window_position_files()
        application_manager.get_helper_base().enable_person_result_csv()
        application_manager.get_helper_base().set_new_flag("processing_fps_limit: true")
        application_manager.get_helper_base().set_new_flag("processing_fps: 25")
        application_manager.get_helper_base().replace_flag_value("application:", "show_gui: true", "show_gui: false")
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "#    app_video_file: 'Full path to video file'",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() + "/data/video_files/dms_male.mp4'")
        yield
        application_manager.get_helper_base().clear_saved_data()

    @pytest.mark.basic
    def test_compilation_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert future.result() == 0

    @pytest.mark.basic
    def test_compilation_testlink(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))

        # response = my_test_link.getTestProjectByName("CoDriver_test")
        # print("!!!!!!! getTestProjectByName" + str(response))
        #
        # response = my_test_link.getProjectTestPlans(my_test_link.getTestProjectByName("CoDriver_test")['id'])
        # print("$$$$$$$ getProjectTestPlans", response)
        #
        # response = my_test_link.getTestCasesForTestPlan("33857")
        # print("^^^^^^ getTestCasesForTestPlan A failed ", response)
        #
        # response = my_test_link.getBuildsForTestPlan("33857")
        # print("%%%%%% getBuildsForTestPlan", response)
        #
        # response = my_test_link.getTestPlanByName(option.testlink_project, option.testlink_plan)
        # print("@@@@@@@@@ getTestPlanByName", response)
        #
        # response = my_test_link.getTestPlanByName(option.testlink_project, option.testlink_plan)[0]['id']
        # print("&&&&&&&& getTestPlanByName", response)

        p = application_manager.run_make_codriver_sample()

        flag_exit_state = True

        if p.wait() != 0:
            flag_exit_state = False
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(p.returncode) + " code"))
            my_test_link.reportTCResult(testcaseexternalid="CDT-1772", testplanid=my_test_link.getTestPlanByName(option.testlink_project, option.testlink_plan)[0]['id'], buildname=option.testlink_build,
                                                    status='f', platformname=option.testlink_platform)

        else:
            my_test_link.reportTCResult(testcaseexternalid="CDT-1772", testplanid=my_test_link.getTestPlanByName(option.testlink_project, option.testlink_plan)[0]['id'], buildname=option.testlink_build,
                                        status='p', platformname=option.testlink_platform)

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert flag_exit_state

    @pytest.mark.basic
    def test_head_pose_info_end_ride_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            keyboard = Controller()
            future = executor.submit(application_manager.run_codriver_sample, True)
            time.sleep(10)
            if future.running():
                keyboard.press("t")
                keyboard.release("t")
                time.sleep(5)
                if future.running():
                    keyboard.press("t")
                    keyboard.release("t")
                else:
                    LOGGER.error(HelperBase.get_message("failed_run"))
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))
        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert future.result() == 0

    @pytest.mark.basic
    def test_head_pose_info_csv_pitch(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        application_manager.run_codriver_sample(False)

        flag_accepted_results = application_manager.get_helper_head_pose_info().compare_results("head_pose_2.2.3.csv", "Headpose Pitch (deg)", 0.5, 50)

        if not flag_accepted_results:
            LOGGER.critical(HelperBase.get_message("failed_condition: Head pose Pitch validation failed"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert flag_accepted_results

    @pytest.mark.basic
    def test_head_pose_info_csv_yaw(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        application_manager.run_codriver_sample(False)

        flag_accepted_results = application_manager.get_helper_head_pose_info().compare_results("head_pose_2.2.3.csv", "Headpose Yaw (deg)", 3, 50)

        if not flag_accepted_results:
            LOGGER.critical(HelperBase.get_message("failed_condition: Head pose Yaw validation failed"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert flag_accepted_results

    @pytest.mark.basic
    def test_head_pose_info_csv_roll(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        application_manager.run_codriver_sample(False)

        flag_accepted_results = application_manager.get_helper_head_pose_info().compare_results("head_pose_2.2.3.csv", "Headpose Roll (deg)", 3, 50)

        if not flag_accepted_results:
            LOGGER.critical(HelperBase.get_message("failed_condition: Head pose Roll validation failed"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert flag_accepted_results