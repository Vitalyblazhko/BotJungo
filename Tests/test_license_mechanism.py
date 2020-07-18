import concurrent.futures
import logging
import platform
import sys
import time
import pyautogui
import pytest
from pynput.keyboard import Controller, Key
from Manager.application_manager import ApplicationManager
from Manager.helper_base import HelperBase
from Manager.helper_path import HelperPath


class TestLicenseMechanism:
    @pytest.fixture(scope="class", autouse=True)
    def session_initializing(self):
        global application_manager
        application_manager = ApplicationManager()
        global LOGGER
        LOGGER = logging.getLogger(__name__)
        LOGGER.info(HelperBase.get_message("info_start_suit"))
        global platform_name
        platform_name = platform.system()

        global missing_license_message
        global found_license_message
        if platform_name == "Linux":
            missing_license_message = "Missing license. Please make sure that you have copied your 'codriver.cfg' file to the '" + \
                                      HelperPath.detect_path()[5] + "/' folder"
            found_license_message = "Found license file [" + HelperPath.detect_path()[
                5] + "/codriver.cfg]\nValid license"
        elif platform_name == "Windows":
            pass
        yield
        LOGGER.info(HelperBase.get_message("info_finish_suit"))
        application_manager.get_helper_base().put_cfg_file("codriver.cfg")

    #@pytest.mark.run(order=2)
    @pytest.fixture()
    def set_up(self):
        application_manager.get_helper_base().set_default_yml()
        application_manager.get_helper_base().remove_window_position_files()
        application_manager.get_helper_base().remove_cfg_file()
        yield
        pass

    @pytest.mark.basic
    def test_license_mechanism_stdout(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample_write_stdout)
            time.sleep(10)
            if future.running():
                try:
                    keyboard = Controller()
                    keyboard.press(Key.esc)
                    keyboard.release(Key.esc)
                except KeyboardInterrupt:
                    sys.exit()
                time.sleep(2)
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))

            k = future.result()
            k.close()

        flag_string_exists = application_manager.get_helper_license_mechanism().confirm_string_existence(missing_license_message)

        if not flag_string_exists:
            LOGGER.critical(HelperBase.get_message("failed_condition: String \"" + str(missing_license_message) + "\" does not exists in std_output"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert flag_string_exists

    @pytest.mark.basic
    def test_license_mechanism_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)
            time.sleep(15)

            if future.running():
                try:
                    keyboard = Controller()
                    keyboard.press(Key.esc)
                    keyboard.release(Key.esc)
                except KeyboardInterrupt:
                    sys.exit()
                time.sleep(5)
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert future.result() == 0

    @pytest.mark.gui
    def test_license_mechanism_gui(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        counter = 0
        p = application_manager.run_codriver_sample_return_process()

        time.sleep(15)

        for x in range(5):
            if p.poll() is None:
                counter = HelperBase.get_match_template_return_counter(counter, [300, 100, 1400, 600], HelperBase.get_project_dir() + "/data/images/license_mechanism/linux/license_mechanism_run_without_license.png", 0.9)
            else:
                LOGGER.info(HelperBase.get_message("failed_run"))
            time.sleep(3)

        if p.poll() is None:
            try:
                keyboard = Controller()
                keyboard.press(Key.esc)
                keyboard.release(Key.esc)
                time.sleep(5)
                if p.poll() is None:
                    p.kill()
            except KeyboardInterrupt:
                sys.exit()
        else:
            LOGGER.error(HelperBase.get_message("failed_run"))

        if counter < 5:
            LOGGER.critical(HelperBase.get_message("failed_condition: License missing image counted " + str(counter) + " times from 5"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert counter == 5

    @pytest.mark.basic
    def test_license_put_license_stdout(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        fails = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample_write_stdout)
            time.sleep(10)
            HelperBase.put_cfg_file("codriver.cfg")
            time.sleep(15)
            if future.running():
                try:
                    keyboard = Controller()
                    keyboard.press(Key.esc)
                    keyboard.release(Key.esc)
                except KeyboardInterrupt:
                    sys.exit()
                time.sleep(5)
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))

            k = future.result()
            k.close()

        if not application_manager.get_helper_license_mechanism().confirm_string_existence(missing_license_message):
            fails.append("String \"" + str(missing_license_message) + "\" does not exists in std_output")
            LOGGER.critical(HelperBase.get_message("failed_condition: String \"" + str(missing_license_message) + "\" does not exists in std_output"))
        if not application_manager.get_helper_license_mechanism().confirm_string_existence(found_license_message):
            fails.append("String \"" + str(found_license_message) + "\" does not exists in std_output")
            LOGGER.critical(HelperBase.get_message("failed_condition: String \"" + str(found_license_message) + "\" does not exists in std_output"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert not fails, "errors occured:\n{}".format("\n".join(fails))

    @pytest.mark.basic
    def test_license_put_license_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)
            time.sleep(15)
            HelperBase.put_cfg_file("codriver.cfg")
            time.sleep(15)
            if future.running():
                try:
                    keyboard = Controller()
                    keyboard.press(Key.esc)
                    keyboard.release(Key.esc)
                except KeyboardInterrupt:
                    sys.exit()
                time.sleep(2)
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))
        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert future.result() == 0

    @pytest.mark.gui
    def test_license_put_license_gui(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        fails = []
        counter_without_license = 0
        counter_with_license = 0
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "#    app_video_file: 'Full path to video file'",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() +"/data/video_files/dms_hand_detection_activity.mp4'")
        application_manager.get_helper_base().set_new_flag("processing_fps_limit: true")
        application_manager.get_helper_base().set_new_flag("processing_fps: 25")

        p = application_manager.run_codriver_sample_return_process()

        time.sleep(5)

        for x in range(5):
            if p.poll() is None:
                counter_without_license = HelperBase.get_match_template_return_counter(counter_without_license, [300, 100, 1400, 600], HelperBase.get_project_dir() + "/data/images/license_mechanism/linux/license_mechanism_run_without_license.png", 0.9)
            else:
                LOGGER.info(HelperBase.get_message("failed_run"))
            time.sleep(2)

        HelperBase.put_cfg_file("codriver.cfg")
        time.sleep(8)

        for x in range(5):
            if p.poll() is None:
                counter_with_license = HelperBase.get_match_template_return_counter(counter_with_license, [450, 0, 1400, 500], HelperBase.get_project_dir() + "/data/images/license_mechanism/linux/license_mechanism_run_with_license.png", 0.9)
            else:
                LOGGER.info(HelperBase.get_message("failed_run"))
            time.sleep(3)

        if p.poll() is None:
            try:
                keyboard = Controller()
                keyboard.press(Key.esc)
                keyboard.release(Key.esc)
                time.sleep(5)
                if p.poll() is None:
                    p.kill()
            except KeyboardInterrupt:
                sys.exit()
        else:
            LOGGER.error(HelperBase.get_message("failed_run"))

        if not counter_without_license == 5:
            fails.append("License missing image counted " + str(counter_without_license) + " times from 5")
            LOGGER.critical(HelperBase.get_message("failed_condition: License missing image counted " + str(counter_without_license) + " times from 5"))
        if not counter_with_license == 5:
            fails.append("License found image counted " + str(counter_with_license) + " times from 5")
            LOGGER.critical(HelperBase.get_message("failed_condition: License found image counted " + str(counter_with_license) + " times from 5"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert not fails, "errors occured:\n{}".format("\n".join(fails))