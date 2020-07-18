import concurrent.futures
import logging
import sys
import time
import pytest
from pynput.keyboard import Controller, Key

from Manager.application_manager import ApplicationManager
from Manager.helper_base import HelperBase


class TestEyewearDetectionNone():
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
        application_manager.get_helper_base().enable_person_result_csv()
        application_manager.get_helper_base().set_new_flag("processing_fps_limit: true")
        application_manager.get_helper_base().set_new_flag("processing_fps: 9")
        application_manager.get_helper_base().replace_flag_value("dms:", "    alg_face_detect_min_face_size: 120", "    alg_face_detect_min_face_size: 50")
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "#    app_video_file: 'Full path to video file'",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() + "/data/video_files/dms_male_ir.mp4'")
        application_manager.get_helper_base().remove_window_position_files()
        yield
        application_manager.get_helper_base().clear_saved_data()

    @pytest.mark.basic
    def test_eyewear_detection_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))
        assert future.result() == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_eyewear_detection_esc_core_error(self, set_up):
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
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))

        assert future.result() == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_eyewear_detection_end_ride_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)

            time.sleep(10)
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
    def test_eyewear_detection_none_csv(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        application_manager.run_codriver_sample(False)

        # Returns [total_frames, counter_unknown, counter_none, counter_glasses, counter_sunglasses]
        array_eyewear = application_manager.get_helper_eyewear_detection().read_csv_return_eyewear(
            HelperBase.get_saved_data_csv("person_results.csv"), "Eyewear")

        #if counter_none
        not_none_count = int(array_eyewear[1])+int(array_eyewear[3])+int(array_eyewear[4])
        if not_none_count > 30:
            LOGGER.critical(HelperBase.get_message("failed_condition: Not none Eyewear counted " + str(not_none_count) + " times from "+str(array_eyewear[0])+" frames"))

        assert not_none_count <= 30
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.gui
    def test_eyewear_detection_none_gui(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        p = application_manager.run_codriver_sample_return_process()

        application_manager.maximize_incabin_window()

        counter = 0
        while p.poll() is None:
            counter = HelperBase.get_match_template_return_counter(counter, [0, 300, 960, 900], HelperBase.get_project_dir() +"/data/images/processing_eyes/linux/eyewear_none.png", 0.99)

        if counter < 80:
            LOGGER.critical(
                HelperBase.get_message("failed_condition: Eyewear none image counted " + str(counter) + " times from min 80"))

        assert counter >= 80
        LOGGER.info(HelperBase.get_message("info_finish_message"))