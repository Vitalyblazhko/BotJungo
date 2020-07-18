import csv
import fileinput
import getpass
import os
import platform
import shutil
import sys
from datetime import datetime
import numpy as np

import cv2
import pandas as pd
import logging as log

import pyautogui

from Manager.helper_path import HelperPath


class HelperBase():

    def __init__(self):
        global user_name
        user_name = getpass.getuser()
        global platform_name
        platform_name = platform.system()

        # global helper_path
        # helper_path = HelperPath()

    def set_video_file_in_dms(self):
        path_to_video_file = HelperPath.detect_path()[2]
        self.replace_flag_value("application:",
                                "#    app_video_file: 'Full path to video file'",
                                "    app_video_file: '" + path_to_video_file + "'")

    def set_left_behind_mode(self):
        self.replace_flag_value("application:",
                                "    app_detection_mode: \"dms\" # dms / dms_lite / full_cabin / full_cabin_lite / dms_full_cabin / left_behind",
                                "    app_detection_mode: \"left_behind\" # dms / dms_lite / full_cabin / full_cabin_lite / dms_full_cabin / left_behind")

    def enable_events_csv(self):
        self.replace_flag_value("application:",
                                "save_events_csv: false",
                                "save_events_csv: true")

    def set_default_yml(self):
        if platform_name == "Linux":
            shutil.copyfile(HelperPath.detect_path()[0], HelperPath.detect_path()[1])

        # elif platform_name == "Windows":
        #     #TODO
        #     shutil.copyfile(HelperPath.detect_path()[0], HelperPath.detect_path()[1])

    def enable_person_result_csv(self):
        self.replace_flag_value("application:",
                                "save_person_result_csv: false",
                                "save_person_result_csv: true")

    def replace_flag_value(self, mode, from_string, to_string):
        with fileinput.FileInput(HelperPath.detect_path()[1], inplace=True) as file:
            for line in file:
                if line.startswith(mode):
                    print(line, end='')
                    for line in file:
                        if line.startswith(from_string):
                            print(line.replace(from_string, to_string), end='')
                            break
                        else:
                            print(line, end='')
                else:
                    print(line, end='')

    def set_new_flag(self, flag):
        with fileinput.FileInput(HelperPath.detect_path()[1], inplace=True) as file:
            for line in file:
                if line.strip() == "# == For full flags descriptions refer to docs/flags_help.txt ==":
                    print(line, end='')
                    print(flag, end='\n')
                else:
                    print(line, end='')

    def clear_saved_data(self):
        directory = HelperPath.detect_path()[3]
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def clear_saved_face_recognition_data(self):
        directory = HelperPath.detect_path()[6]
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def remove_window_position_files(self):
        try:
            os.remove(HelperPath.detect_path()[4])
        except:
            pass

    def remove_cfg_file(self):
        path_to_data_dir = HelperPath.detect_path()[5]
        for dirpath, dirnames, filenames in os.walk(path_to_data_dir, topdown=False):
            for filename in filenames:
                if filename.endswith(".cfg"):
                    path_to_csv = os.path.join(dirpath, filename)
        try:
            os.remove(path_to_csv)
        except:
            pass

    def touch(self, path):
        with open(path, "w+"):
            os.utime(path, None)
        return path

    @staticmethod
    def put_cfg_file(cfg):
        try:
            shutil.copy(HelperBase.get_project_dir() + "/data/licenses/" + cfg, HelperPath.detect_path()[5])
        except:
            pass

    @staticmethod
    def read_text_file_return_result(file, expected_result):
        with open(file) as f:
            if expected_result in f.read():
                f.close()
                return True
        f.close()
        return False

    @staticmethod
    def create_test_dir(state):
        path = HelperBase.get_project_dir() + "/outputs/" + HelperBase.get_test_name() + "/" + state
        isdir = os.path.isdir(path)
        if isdir:
            pass
        else:
            try:
                os.makedirs(HelperBase.get_project_dir() + "/outputs/" + HelperBase.get_test_name() + "/" + state)
            except OSError:
                pass
        return path

    @staticmethod
    def create_logs_dir():
        path = HelperBase.get_project_dir() + "/outputs/logs"
        isdir = os.path.isdir(path)
        if isdir:
            pass
        else:
            try:
                os.makedirs(HelperBase.get_project_dir() + "/outputs/logs")
            except OSError:
                pass
        f = open(path + "log.txt", "a")
        f.close()

    @staticmethod
    def get_project_dir():
        TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
        sys.path.insert(0, PROJECT_DIR)
        return PROJECT_DIR

    @staticmethod
    def get_test_name():
        return os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]

    @staticmethod
    def get_class_name():
        return os.environ.get('PYTEST_CURRENT_TEST').split('::')[1]

    @staticmethod
    def read_csv_get_column_values(csv_file, column_name):
        column_values = []
        with open(csv_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    for item in row:
                        if item == column_name:
                            column = row.index(item)
                    line_count += 1
                else:
                    column_values.append(row[column])
                    line_count += 1
        return column_values

    @staticmethod
    #TODO: add to log if file does not exist
    def get_saved_data_csv(csv_file_name_postfix):
        path_to_saved_data_directory = HelperPath.detect_path()[3]
        for dirpath, dirnames, filenames in os.walk(path_to_saved_data_directory, topdown=False):
            for filename in filenames:
                if filename.endswith(csv_file_name_postfix):
                    path_to_saved_data_directory = os.path.join(dirpath, filename)
        return path_to_saved_data_directory

    @staticmethod
    def get_saved_face_recognition_data_csv(csv_file_name):
        path_to_saved_data_directory = HelperPath.detect_path()[6]
        for dirpath, dirnames, filenames in os.walk(path_to_saved_data_directory, topdown=False):
            for filename in filenames:
                if filename.endswith(csv_file_name):
                    path_to_saved_data_directory = os.path.join(dirpath, filename)
        return path_to_saved_data_directory

    @staticmethod
    def read_csv_compare_columns(csv_file_name, threshold):
        with open(csv_file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count != 0:
                    if (float(float(row[2]) + threshold) >= float(row[1]) >= float(float(row[2]) - threshold)) or (
                            row[1] == row[2]):
                        continue
                    else:
                        return False
                line_count += 1
        return True

    @staticmethod
    def read_csv_return_error_count(csv_file_name, column_name, expected_result):
        counter_error = 0
        column = -1
        with open(csv_file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    for item in row:
                        if item == column_name:
                            column = row.index(item)
                else:
                    if row[column] != expected_result:
                        counter_error +=1
                line_count += 1
        return counter_error

    @staticmethod
    # TODO: add to log file not found
    def get_failed_results(csv_file_name, threshold):
        file_failed = csv_file_name + "_failed.csv"
        with open(file_failed, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Frame", "Source", "Failed", "Diff"])

            with open(csv_file_name) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count != 0:
                        if (float(float(row[2]) + threshold) >= float(row[1]) >= float(float(row[2]) - threshold)) or (
                                row[1] == row[2]):
                            pass
                        else:
                            writer.writerow([row[0], row[1], row[2], str(HelperBase.count_failure(row[1], row[2]))])
                    line_count += 1

        file_read = open(file_failed, "r")
        reader = csv.reader(file_read)

        failures_number = int(len(list(reader))) - 1

        df = pd.read_csv(file_failed)

        p = df['Diff'].max()
        # q = df['ColumnName'].min()

        # returns all frames quantity, failed_frames, percentage of failed frames, max value from failed
        return [int(line_count)-1, failures_number, HelperBase.count_failures_percentage(failures_number, int(line_count) - 1), p]

    @staticmethod
    def count_failure(number_1, number_2):
        if float(number_1) > float(number_2):
            return float(number_1) - float(number_2)
        else:
            return float(number_2) - float(number_1)

    @staticmethod
    def count_failures_percentage(failures, frames):
        return int(failures) / int(frames) * 100

    @staticmethod
    def read_csv_return_found_expectations(csv_file_name, column_name, expected_result):
        counter = 0
        column = -1
        with open(csv_file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    for item in row:
                        if item == column_name:
                            column = row.index(item)
                else:
                    if row[column] == expected_result:
                        counter += 1
                line_count += 1
        return counter

    @staticmethod
    def read_csv_return_found_expectations_after_frame(csv_file_name, frame_number, column_name, expected_result):
        counter = 0
        column = -1
        with open(csv_file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    for item in row:
                        if item == column_name:
                            column = row.index(item)
                else:
                    if int(row[0]) >= frame_number and row[column] == expected_result:
                        counter += 1
                line_count += 1
        return counter

    @staticmethod
    def read_csv_return_lines_count(csv_file_name):
        file_read = open(csv_file_name, "r")
        reader = csv.reader(file_read)

        return len(list(reader))

    @staticmethod
    def read_csv_get_event_details(csv_file_name, event_name):
        column = -1
        with open(csv_file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    for item in row:
                        if item == "Event Name":
                            column = row.index(item)
                else:
                    if row[column] == event_name:
                        return row[int(column) + 1]
                line_count += 1
        return -1

    @staticmethod
    def read_csv_get_person_name_from_faced_db(csv_file_name):
        with open(csv_file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            counter = 0
            id_name = ""
            person_name = ""
            for row in csv_reader:
                id_name = row[0][:3]
                person_name = row[1]
                if id_name == person_name.split("-")[1]:
                    counter += 1
        if counter == 5:
            return person_name
        else:
            return -1

    @staticmethod
    #TODO: add logs file not found
    def get_saved_face_recognition_data_person_image(person_id_prefix):
        path_to_person_image = HelperPath.detect_path()[6]
        for dirpath, dirnames, filenames in os.walk(path_to_person_image, topdown=False):
            for filename in filenames:
                if filename.startswith(person_id_prefix):
                    path_to_person_image = os.path.join(dirpath, filename)
        return path_to_person_image

    @staticmethod
    def get_image_size(image):
        try:
            im = cv2.imread(image)
            return im.shape
        except:
            pass
        return -1

    @staticmethod
    def return_templates_counter(counter, template, region, threshold):
        if pyautogui.locateOnScreen(template, region=(region[0], region[1], region[2], region[3]), confidence=threshold) is not None:
            counter += 1
        return counter

    @staticmethod
    def get_match_template_return_counter(counter, region, template, threshold):
        screenshot = pyautogui.screenshot(region=(region[0], region[1], region[2], region[3]))
        screenshot.save(HelperBase.get_project_dir() + "/outputs/tmp.png")
        img_rgb = cv2.imread(HelperBase.get_project_dir() + "/outputs/tmp.png")
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(template, 0)

        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        flag_found_image = False

        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            flag_found_image = True
        cv2.imwrite(HelperBase.create_test_dir("screenshots") + "/screenshot_" + datetime.now().strftime("%Y%m%d%H%M%S.%f") + ".png", img_rgb)

        if flag_found_image:
            counter += 1
        cv2.waitKey(0)
        return counter

    @staticmethod
    def get_template_from_array_return_counter_with_array(counter, region, array_templates, threshold):
        screenshot = pyautogui.screenshot(region=(region[0], region[1], region[2], region[3]))
        screenshot.save(HelperBase.get_project_dir() + "/outputs/tmp.png")
        img_rgb = cv2.imread(HelperBase.get_project_dir() + "/outputs/tmp.png")

        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

        templates_length = len(array_templates)
        for x in range(templates_length):
            flag_found_template = False
            template = cv2.imread(array_templates[x], 0)

            w, h = template.shape[::-1]
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

            loc = np.where(res >= threshold)

            for pt in zip(*loc[::-1]):
                cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
                flag_found_template = True

            if flag_found_template:
                del array_templates[x]
                counter += 1
                break

        cv2.imwrite(HelperBase.create_test_dir("screenshots") + "/screenshot_" + datetime.now().strftime(
            "%Y%m%d%H%M%S.%f") + ".png", img_rgb)
        cv2.waitKey(0)

        return counter, array_templates

    @staticmethod
    def get_template_from_array_return_counter(counter, region, array_templates, threshold):
        screenshot = pyautogui.screenshot(region=(region[0], region[1], region[2], region[3]))
        screenshot.save(HelperBase.get_project_dir() + "/outputs/tmp.png")
        img_rgb = cv2.imread(HelperBase.get_project_dir() + "/outputs/tmp.png")

        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

        templates_length = len(array_templates)
        flag_found_template = []

        for x in range(templates_length):
            flag_found_template.append(False)
            template = cv2.imread(array_templates[x], 0)

            w, h = template.shape[::-1]
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

            loc = np.where(res >= threshold)

            for pt in zip(*loc[::-1]):
                cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
                flag_found_template.insert(x, True)

            if flag_found_template[x]:
                counter[x] += 1

        cv2.imwrite(HelperBase.create_test_dir("screenshots") + "/screenshot_" + datetime.now().strftime(
            "%Y%m%d%H%M%S.%f") + ".png", img_rgb)

        cv2.waitKey(0)
        return counter

    @staticmethod
    def get_message(type_message):
        if type_message == "info_start_message":
            #return "Test name: \"" + HelperBase.get_test_name().replace("_", " ").upper() + "\" started"
            return "Test name: " + HelperBase.get_test_name() + " started"
        elif type_message == "info_finish_message":
            return "Test name: " + HelperBase.get_test_name() + " finished\n------------------------------------------------------------"
        elif type_message == "templates_not_found":
            return "Templates not found"
        elif type_message == "info_start_suit":
            return "Test suit name: \"" + HelperBase.to_upper_case(HelperBase.get_class_name()).upper() + "\" started\n------------------------------------------------------------"
        elif type_message == "info_finish_suit":
            return "Test suit name: \"" + HelperBase.to_upper_case(HelperBase.get_class_name()).upper() + "\" finished\n============================================================"
        elif type_message.startswith("failed_condition:"):
            return "Test name: " + HelperBase.get_test_name() + " -" + type_message.split("failed_condition:")[1]
        elif type_message == "failed_run":
            return "Test name: " + HelperBase.get_class_name() + " - CoDriver interrupted"

    @staticmethod
    def to_upper_case(string):
        for ch in string:
            if ch.isupper():
                string = string.split(ch)[0]+ " " + ch+string.split(ch)[1]
        return string.lstrip()


#HelperBase.read_csv_get_person_name_from_faced_db("/var/codriver/saved_face_recognition_data/faces_db.csv")
