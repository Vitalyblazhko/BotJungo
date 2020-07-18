import concurrent.futures
import logging
import sys
import time
import pytest
from pynput.keyboard import Controller, Key
from Manager.application_manager import ApplicationManager
from Manager.helper_base import HelperBase

class TestProcessingGender:
    @pytest.fixture(scope="class", autouse=True)
    def session_initializing(self):
        global application_manager
        application_manager = ApplicationManager()
        global LOGGER
        LOGGER = logging.getLogger(__name__)
        LOGGER.info(HelperBase.get_message("info_start_suit"))

        # global platform_name
        # platform_name = platform.system()
        # global user_name
        # user_name = getpass.getuser()
        #
        # global processing_gender_female
        # global processing_gender_male
        # if platform_name == "Linux":
        #     processing_gender_female = HelperBase.get_project_dir() + "/data/images/processing_gender/linux/processing_gender_female.png"
        #     processing_gender_male = HelperBase.get_project_dir() + "/data/images/processing_gender/linux/processing_gender_male.png"
        # elif platform_name == "Windows":
        #     pass
        yield
        LOGGER.info(HelperBase.get_message("info_finish_suit"))

    @pytest.fixture()
    def set_up(self):
        application_manager.get_helper_base().set_default_yml()
        application_manager.get_helper_base().remove_window_position_files()
        application_manager.get_helper_base().enable_person_result_csv()
        application_manager.get_helper_base().set_new_flag("processing_fps_limit: true")
        application_manager.get_helper_base().set_new_flag("processing_fps: 25")
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "#    app_video_file: 'Full path to video file'",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() + "/data/video_files/dms_male.mp4'")
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "processing_gender: false",
                                                                 "processing_gender: true")
        yield
        application_manager.get_helper_base().clear_saved_data()

    @pytest.mark.basic
    def test_processing_gender_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))
        assert future.result() == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_processing_gender_esc_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)

            time.sleep(20)
            if future.running():
                try:
                    keyboard = Controller()
                    keyboard.press(Key.esc)
                    keyboard.release(Key.esc)
                except KeyboardInterrupt:
                    sys.exit()
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))

        assert future.result() == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_processing_gender_end_ride_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)

            time.sleep(20)
            if future.running():
                keyboard = Controller()
                keyboard.press("t")
                keyboard.release("t")
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))

        assert future.result() == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_processing_gender_csv_male(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        application_manager.run_codriver_sample(False)

        counter = HelperBase.read_csv_return_found_expectations_after_frame(HelperBase.get_saved_data_csv("person_results.csv"), 0, "Gender", "Male")

        if counter < 1600:
            LOGGER.critical(HelperBase.get_message("failed_condition: Gender counted " + str(counter) + " times from min 1600"))

        assert counter >= 1600
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_processing_gender_csv_female(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() + "/data/video_files/dms_male.mp4'",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() + "/data/video_files/dms_female_ir.mp4'")
        application_manager.run_codriver_sample(False)

        counter = HelperBase.read_csv_return_found_expectations_after_frame(
            HelperBase.get_saved_data_csv("person_results.csv"), 0, "Gender", "Female")

        if counter < 1500:
            LOGGER.critical(
                HelperBase.get_message("failed_condition: Gender counted " + str(counter) + " times from min 1500"))

        assert counter >= 1200
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.gui
    def test_processing_gender_male_gui(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))

        counter = 0
        p = application_manager.run_codriver_sample_return_process()

        while p.poll() is None:
            counter = HelperBase.get_match_template_return_counter(counter, [350, 600, 800, 800], HelperBase.get_project_dir() +"/data/images/processing_gender/linux/processing_gender_male.png", 0.95)

        # while p.poll() is None:
        #     counter = HelperBase.return_templates_counter(counter, HelperBase.get_project_dir() + "/data/images/processing_gender/linux/processing_gender_male.png", [350, 600, 800, 800], 0.95)

        if counter < 80:
            LOGGER.critical(HelperBase.get_message("failed_condition: Gender Male detected " + str(counter) + " times from 80"))

        assert counter >= 80
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.gui
    def test_processing_gender_female_gui(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() + "/data/video_files/dms_male.mp4'",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() + "/data/video_files/dms_female_ir.mp4'")
        counter = 0
        p = application_manager.run_codriver_sample_return_process()

        while p.poll() is None:
            counter = HelperBase.get_match_template_return_counter(counter, [350, 600, 800, 800], HelperBase.get_project_dir() +"/data/images/processing_gender/linux/processing_gender_female.png", 0.99)

        # while p.poll() is None:
        #     counter = HelperBase.return_templates_counter(counter,HelperBase.get_project_dir() + "/data/images/processing_gender/linux/processing_gender_female.png", [350, 600, 800, 800], 0.99)

        if counter < 120:
            LOGGER.critical(
                HelperBase.get_message("failed_condition: Gender Female detected " + str(counter) + " times from 120"))

        assert counter >= 120
        LOGGER.info(HelperBase.get_message("info_finish_message"))