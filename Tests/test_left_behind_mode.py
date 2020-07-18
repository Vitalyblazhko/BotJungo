import concurrent.futures
import logging
import sys
import time
import pyautogui
import pytest
from pynput.keyboard import Controller, Key
from Manager.application_manager import ApplicationManager
from Manager.helper_base import HelperBase


class TestLeftBehindMode:
    @pytest.fixture(scope="class", autouse=True)
    def session_initializing(self):
        global application_manager
        application_manager = ApplicationManager()
        global LOGGER
        LOGGER = logging.getLogger(__name__)
        LOGGER.info(HelperBase.get_message("info_start_suit"))
        yield
        LOGGER.info(HelperBase.get_message("info_finish_suit"))

    @pytest.fixture()
    def set_up(self):
        application_manager.get_helper_base().set_default_yml()
        application_manager.get_helper_base().remove_window_position_files()
        application_manager.get_helper_base().set_left_behind_mode()
        application_manager.get_helper_base().enable_events_csv()
        application_manager.get_helper_base().set_new_flag("show_fps: false")
        application_manager.get_helper_base().set_new_flag("show_cpu: false")
        application_manager.get_helper_base().set_new_flag("show_memory: false")
        application_manager.get_helper_base().set_new_flag("show_resolution: false")
        application_manager.get_helper_base().set_new_flag("processing_fps_limit: true")
        application_manager.get_helper_base().set_new_flag("processing_fps: 30")
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "#    app_video_file: 'Full path to video file'",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() + "/data/video_files/left_behind.mp4'")
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "show_licensed_to: true",
                                                                 "show_licensed_to: false")
        yield
        application_manager.get_helper_base().clear_saved_data()

    @pytest.mark.basic
    def test_left_behind_mode_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))
        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert future.result() == 0

    @pytest.mark.basic
    def test_left_behind_mode_esc_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)
            time.sleep(10)
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

    @pytest.mark.basic
    def test_left_behind_mode_end_ride_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            keyboard = Controller()
            future = executor.submit(application_manager.run_codriver_sample, True)
            time.sleep(8)
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
    def test_left_behind_mode_csv(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        found_expectation = 0
        application_manager.run_codriver_sample(False)

        found_expectation = HelperBase.read_csv_return_found_expectations_after_frame(application_manager.get_helper_base().get_saved_data_csv("_events.csv"), 0, "Event Name", "LEFT BEHIND")

        if found_expectation < 5:
            LOGGER.critical(HelperBase.get_message("failed_condition: Event LEFT BEHIND raised " + str(found_expectation) + " times from min 5"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert found_expectation >= 5

    @pytest.mark.gui
    def test_left_behind_mode_gui(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        counter = 0
        array_templates = [HelperBase.get_project_dir() + "/data/images/left_behind/linux/case_glasses.png",
                           HelperBase.get_project_dir() + "/data/images/left_behind/linux/case_glass.png",
                           HelperBase.get_project_dir() + "/data/images/left_behind/linux/case_phone.png",
                           HelperBase.get_project_dir() + "/data/images/left_behind/linux/case_pen.png",
                           HelperBase.get_project_dir() + "/data/images/left_behind/linux/case_cup.png",
                           HelperBase.get_project_dir() + "/data/images/left_behind/linux/case_keys.png"]
        p = application_manager.run_codriver_sample_return_process()

        while p.poll() is None:
            if len(array_templates) > 0:
                counter, array_templates = HelperBase.get_template_from_array_return_counter_with_array(counter, [450, 0, 1200, 900], array_templates, 0.99)
            else:
                p.kill()

        if counter < 5:
            LOGGER.critical(HelperBase.get_message("failed_condition: LEFT BEHIND image found " + str(counter) + " times from min 5"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert counter >= 5