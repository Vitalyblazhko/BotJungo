import concurrent.futures
import logging
import sys
import time
import pytest
from pynput.keyboard import Controller, Key
from Manager.application_manager import ApplicationManager
from Manager.helper_base import HelperBase

class TestHandGesture:
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
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "#    app_video_file: 'Full path to video file'",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() + "/data/video_files/dms_hand_gesture_down.mp4'")
        application_manager.get_helper_base().replace_flag_value("application:", "save_events_csv: false", "save_events_csv: true")
        application_manager.get_helper_base().set_new_flag("processing_hand: true")
        application_manager.get_helper_base().set_new_flag("processing_event_hand_gesture: true")
        application_manager.get_helper_base().set_new_flag("events_hand_gesture_swipe_threshold_vert: 0.1")
        application_manager.get_helper_base().set_new_flag("events_hand_gesture_swipe_threshold_hor: 0.1")
        application_manager.get_helper_base().set_new_flag("processing_fps_limit: true")
        application_manager.get_helper_base().set_new_flag("processing_fps: 30")
        application_manager.get_helper_base().set_new_flag("    onEventStoreFile: 1")
        application_manager.get_helper_base().set_new_flag("EVENT_HAND_GESTURE:")
        application_manager.get_helper_base().remove_window_position_files()
        yield
        application_manager.get_helper_base().clear_saved_data()

    @pytest.mark.basic
    def test_hand_gesture_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))
        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert future.result() == 0

    @pytest.mark.basic
    def test_hand_gesture_esc_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)

            time.sleep(3)
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

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert future.result() == 0

    @pytest.mark.basic
    def test_hand_gesture_end_ride_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)

            time.sleep(3)
            if future.running():
                keyboard = Controller()
                keyboard.press("t")
                keyboard.release("t")
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert future.result() == 0

    @pytest.mark.basic
    def test_hand_gesture_swipe_down_csv(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        application_manager.run_codriver_sample(False)

        counter = HelperBase.read_csv_return_found_expectations_after_frame(HelperBase.get_saved_data_csv("_events.csv"), 0, "Event Name", "HAND GESTURE")
        # Uncomment to show fail in 2.1.0_v4
        #counter = HelperBase.read_csv_return_found_expectations_after_frame(HelperBase.get_saved_data_csv("_events.csv"), 0, "Event Name", "HAND-GESTURE")

        if counter < 3:
            LOGGER.critical(HelperBase.get_message("failed_condition: Event HAND GESTURE raises " + str(counter) + " times from min 3"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert counter >= 3

    @pytest.mark.gui
    def test_hand_gesture_swipe_down_gui(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        p = application_manager.run_codriver_sample_return_process()

        application_manager.maximize_incabin_window()

        counter = 0
        while p.poll() is None:
            counter = HelperBase.get_match_template_return_counter(counter, [0, 0, 1200, 500], HelperBase.get_project_dir()+"/data/images/hand_gesture_down/linux/gesture_down_2.2_2.png", 0.9)
            #Uncomment to show fail in 2.1.0_v4
            #counter = HelperBase.get_match_template_return_counter(counter, [0, 0, 1200, 500], HelperBase.get_project_dir()+"/data/images/hand_gesture_down/linux/gesture_down_2.1_1.png", 0.9)
        if counter < 5:
            LOGGER.critical(HelperBase.get_message("failed_condition: HAND GESTURE image found " + str(counter) + " times from min 10"))

        LOGGER.info(HelperBase.get_message("info_finish_message"))
        assert counter >= 10