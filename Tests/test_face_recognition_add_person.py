import concurrent.futures
import logging
import sys
import time
import pytest
from pynput.keyboard import Controller, Key
from Manager.application_manager import ApplicationManager
from Manager.helper_base import HelperBase


class TestFaceRecognitionAddPerson:
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
        application_manager.get_helper_base().enable_events_csv()
        application_manager.get_helper_base().set_new_flag("processing_fps_limit: true")
        application_manager.get_helper_base().set_new_flag("processing_fps: 30")
        application_manager.get_helper_base().replace_flag_value("application:",
                                                                 "#    app_video_file: 'Full path to video file'",
                                                                 "    app_video_file: '" + HelperBase.get_project_dir() + "/data/video_files/dms_face_recognition.mp4'")
        yield
        application_manager.get_helper_base().clear_saved_data()
        application_manager.get_helper_base().clear_saved_face_recognition_data()

    @pytest.mark.basic
    def test_face_recognition_add_person_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(application_manager.run_codriver_sample, True)
            time.sleep(10)

            if future.running():
                keyboard = Controller()
                keyboard.press("a")
                keyboard.release("a")
                time.sleep(10)

            flag_templates_found = False

            flag_templates_found = application_manager.get_helper_face_recognition_add_person().add_person_confirm_adding_with_future(future, flag_templates_found)

            if not flag_templates_found:
                LOGGER.error(HelperBase.get_message("templates_not_found"))

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))

        assert future.result() == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_face_recognition_add_person_esc_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            keyboard = Controller()
            future = executor.submit(application_manager.run_codriver_sample, True)

            time.sleep(10)

            if future.running():
                keyboard.press("a")
                keyboard.release("a")
                time.sleep(10)

            flag_templates_found = False

            flag_templates_found = application_manager.get_helper_face_recognition_add_person().add_person_confirm_adding_with_future(future, flag_templates_found)

            if not flag_templates_found:
                LOGGER.error(HelperBase.get_message("templates_not_found"))
            else:
                time.sleep(20)
                try:
                    keyboard.press(Key.esc)
                    keyboard.release(Key.esc)
                except KeyboardInterrupt:
                    sys.exit()

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))

        assert future.result() == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_face_recognition_add_person_end_ride_core_error(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            keyboard = Controller()
            future = executor.submit(application_manager.run_codriver_sample, True)
            time.sleep(10)

            if future.running():
                keyboard.press("a")
                keyboard.release("a")
                time.sleep(10)
            else:
                LOGGER.error(HelperBase.get_message("failed_run"))

            flag_templates_found = False
            flag_templates_found = application_manager.get_helper_face_recognition_add_person().add_person_confirm_adding_with_future(future, flag_templates_found)

            if not flag_templates_found:
                LOGGER.error(HelperBase.get_message("templates_not_found"))
            else:
                if future.running():
                    time.sleep(20)
                    keyboard.press("t")
                    keyboard.release("t")
                    time.sleep(10)
                    if future.running():
                        keyboard.press("t")
                        keyboard.release("t")
                    else:
                        LOGGER.error(HelperBase.get_message("failed_run"))
                else:
                    LOGGER.error(HelperBase.get_message("failed_run"))

        if future.result() != 0:
            LOGGER.critical(HelperBase.get_message("failed_condition: Returned " + str(future.result()) + " code"))

        assert future.result() == 0
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.basic
    def test_face_recognition_add_person_csv(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        fails = []
        flag_templates_found = False

        p = application_manager.run_codriver_sample_return_process()
        time.sleep(10)

        if p.poll() is None:
            keyboard = Controller()
            keyboard.press("a")
            keyboard.release("a")
            time.sleep(10)
        else:
            LOGGER.info(HelperBase.get_message("failed_run"))

        flag_templates_found = application_manager.get_helper_face_recognition_add_person().add_person_confirm_adding_with_process(p, flag_templates_found)

        if not flag_templates_found:
            LOGGER.error(HelperBase.get_message("templates_not_found"))

        while p.poll() is None:
            time.sleep(3)

        person_name = HelperBase.read_csv_get_person_name_from_faced_db(HelperBase.get_saved_face_recognition_data_csv("faces_db.csv"))

        if not HelperBase.read_csv_return_lines_count(HelperBase.get_saved_face_recognition_data_csv("faces_db.csv")) == 5:
            fails.append("Lines count in faces_db failed")
            LOGGER.critical(HelperBase.get_message("failed_condition: Lines count in faces_db failed"))

        if not str(HelperBase.read_csv_get_event_details(HelperBase.get_saved_data_csv("_events.csv"), "DRIVER RECOGNIZED")) == str(person_name).split("-")[1]:
            fails.append("Person names in faces_db.csv and events.csv are not identical")
            LOGGER.critical(HelperBase.get_message("failed_condition: Person names in faces_db.csv and events.csv are not identical"))

        if not HelperBase.get_image_size(HelperBase.get_saved_face_recognition_data_person_image(person_name.split("-")[1]))[0] ==\
               HelperBase.get_image_size(HelperBase.get_saved_face_recognition_data_person_image(person_name.split("-")[1]))[1]:
            fails.append("Person image width and height are not identical")
            LOGGER.critical(HelperBase.get_message("failed_condition: Person image width and height are not identical"))

        assert not fails, "errors occured:\n{}".format("\n".join(fails))
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.gui
    def test_face_recognition_add_person_gui(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        flag_templates_found = False

        p = application_manager.run_codriver_sample_return_process()
        time.sleep(10)

        if p.poll() is None:
            keyboard = Controller()
            keyboard.press("a")
            keyboard.release("a")
            time.sleep(10)
        else:
            LOGGER.info(HelperBase.get_message("failed_run"))

        flag_templates_found = application_manager.get_helper_face_recognition_add_person().add_person_confirm_adding_kill_process(p, flag_templates_found)

        if not flag_templates_found:
            LOGGER.critical(HelperBase.get_message("templates_not_found"))

        time.sleep(3)

        assert flag_templates_found
        LOGGER.info(HelperBase.get_message("info_finish_message"))

    @pytest.mark.gui
    def test_face_recognition_add_person_end_ride_gui(self, set_up):
        LOGGER.info(HelperBase.get_message("info_start_message"))
        flag_templates_found = False
        counter = 0
        keyboard = Controller()

        p = application_manager.run_codriver_sample_return_process()
        time.sleep(10)

        if p.poll() is None:
            keyboard.press("a")
            keyboard.release("a")
            time.sleep(10)
        else:
            LOGGER.info(HelperBase.get_message("failed_run"))

        flag_templates_found = application_manager.get_helper_face_recognition_add_person().add_person_confirm_adding_with_process(p, flag_templates_found)

        if not flag_templates_found:
            LOGGER.error(HelperBase.get_message("templates_not_found"))
        else:
            time.sleep(10)
            keyboard = Controller()
            keyboard.press("t")
            keyboard.release("t")
            counter = application_manager.get_helper_face_recognition_add_person().compare_templates(p, counter, HelperBase.get_project_dir() +"/data/images/face_recognition/linux/face_recognition_window_end_ride.png")
        if counter < 20:
            LOGGER.critical(HelperBase.get_message("failed_condition: Empty Face Fecognition window returned " + str(counter) + " times"))

        assert counter > 20
        LOGGER.info(HelperBase.get_message("info_finish_message"))