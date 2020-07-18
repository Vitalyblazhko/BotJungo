import concurrent.futures
import logging
import platform
import sys
import time
import pytest
from pynput.keyboard import Controller, Key
from Manager.application_manager import ApplicationManager
from Manager.helper_base import HelperBase

class TestDistractionHeadPose:
    @pytest.fixture(scope="class", autouse=True)
    def session_initializing(self):
        global application_manager
        application_manager = ApplicationManager()
        global platform_name
        platform_name = platform.system()
        global LOGGER
        LOGGER = logging.getLogger(__name__)
        LOGGER.info(HelperBase.get_message("info_start_suit"))
        global distraction_head_pose_bar
        global distraction_head_pose_event
        if platform_name == "Linux":
            distraction_head_pose_bar = HelperBase.get_project_dir() + "/data/images/distraction_head_pose/linux/distraction_head_pose_bar.png"
            distraction_head_pose_event = HelperBase.get_project_dir() + "/data/images/distraction_head_pose/linux/distraction_head_pose_event.png"
        elif platform_name == "Windows":
            pass
        yield
        LOGGER.info(HelperBase.get_message("info_finish_suit"))

    @pytest.fixture()
    def set_up(self):
        application_manager.get_helper_base().set_default_yml()
        application_manager.get_helper_base().remove_window_position_files()
        application_manager.get_helper_base().enable_events_csv()
        application_manager.get_helper_base().set_new_flag("processing_fps_limit: true")
        application_manager.get_helper_base().set_new_flag("processing_fps: 25")
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "#    app_video_file: 'Full path to video file'",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() + "/data/video_files/dms_male.mp4'")
        # To show failed cases for gui
        # application_manager.get_helper_base().replace_flag_value("dms:",
        #                                                          "    show_alarm: true",
        #                                                          "    show_alarm: false")
        #application_manager.get_helper_base().set_new_flag("show_events_info: false")
        yield
        application_manager.get_helper_base().clear_saved_data()

    @pytest.mark.basic
    def test_distraction_head_pose_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))

        assert future.result() == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_distraction_head_pose_esc_core_error(self, set_up):
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

        assert future.result() == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_distraction_head_pose_end_ride_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            keyboard = Controller()
            future = executor.submit(application_manager.run_codriver_sample, True)
            time.sleep(20)
            if future.running():
                keyboard.press("t")
                keyboard.release("t")
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))
            time.sleep(5)
            if future.running():
                keyboard.press("t")
                keyboard.release("t")
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))

        assert future.result() == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_distraction_head_pose_csv(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        application_manager.run_codriver_sample(False)
        counter = HelperBase.read_csv_return_found_expectations_after_frame(HelperBase.get_saved_data_csv("_events.csv"), 0, "Event Name", "DISTRACTION")

        if counter < 5:
            LOGGER.critical(HelperBase.get_message("failed_condition: Event DISTRACTION raised " + str(counter) + " times from min 5"))

        assert counter >= 5
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_distraction_head_pose_end_ride_csv(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        p = application_manager.run_codriver_sample_return_process()
        time.sleep(20)

        if p.poll() is None:
            keyboard = Controller()
            keyboard.press("t")
            keyboard.release("t")
            time.sleep(5)
            p.wait()
        else:
            LOGGER.info(HelperBase.get_message("failed_run"))

        counter = HelperBase.read_csv_return_found_expectations_after_frame(HelperBase.get_saved_data_csv("_events.csv"), 360, "Event Name", "DISTRACTION")

        if counter > 0:
            LOGGER.critical(HelperBase.get_message(
                "failed_condition: Event DISTRACTION raised " + str(counter) + " times after END RIDE"))

        assert counter == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.gui
    def test_distraction_head_pose_gui(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        fails = []
        counter = [0, 0]
        p = application_manager.run_codriver_sample_return_process()

        while p.poll() is None:
            counter = HelperBase.get_template_from_array_return_counter(counter, [250, 89, 895, 935], [distraction_head_pose_bar, distraction_head_pose_event], 0.99)

        if not counter[0] >= 7:
            fails.append("condition_1 failed")
        if not counter[1] >= 20:
            fails.append("condition_2 failed")

        if not counter[0] >= 7:
            fails.append("Distraction Bar image counted " + str(counter[0]) + " times from 7")
            LOGGER.critical(HelperBase.get_message("failed_condition: Distraction Bar image counted " + str(counter[0]) + " times from min 7"))
        if not counter[1] >= 20:
            fails.append("Distraction Event image counted " + str(counter[1]) + " times from 20")
            LOGGER.critical(HelperBase.get_message("failed_condition: Distraction Event image counted " + str(counter[1]) + " times from min 20"))

        assert not fails, "errors occured:\n{}".format("\n".join(fails))
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.gui
    def test_distraction_head_pose_end_ride_gui(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        fails = []
        counter = [0, 0]
        p = application_manager.run_codriver_sample_return_process()

        time.sleep(10)
        if p.poll() is None:
            keyboard = Controller()
            keyboard.press("t")
            keyboard.release("t")
            time.sleep(5)
        else:
            LOGGER.info(HelperBase.get_message("failed_run"))

        while p.poll() is None:
            counter = HelperBase.get_template_from_array_return_counter(counter, [250, 89, 895, 935],
                                                                        [distraction_head_pose_bar, distraction_head_pose_event], 0.99)

        if not counter[0] == 0:
            fails.append("Distraction Bar image counted " + str(counter[0]) + " times. It is not expected.")
            LOGGER.critical(HelperBase.get_message("failed_condition: Distraction Bar image counted " + str(counter[0]) + " times. It is not expected."))
        if not counter[1] == 0:
            fails.append("Distraction Event image counted " + str(counter[1]) + " times. It is not expected.")
            LOGGER.critical(HelperBase.get_message("failed_condition: Distraction Event image counted " + str(counter[1]) + " times. It is not expected."))

        assert not fails, "errors occured:\n{}".format("\n".join(fails))
        LOGGER.info(HelperBase.get_message("info_finish_message"))