import getpass
import platform
import time
from datetime import datetime
import cv2
import numpy as np
import pyautogui

from Manager.helper_base import HelperBase


class HelperFaceRecognitionAddPerson:

    def __init__(self):
        global user_name
        user_name = getpass.getuser()
        global platform_name
        platform_name = platform.system()

        global add_person_button
        global detect_completed
        global detect_person_unrecognized
        global detect_completed_incabin

        if platform_name == "Linux":
            add_person_button = HelperBase.get_project_dir() + "/data/images/face_recognition/linux/face_recognition_add_person_button.png"
            detect_completed = HelperBase.get_project_dir() + "/data/images/face_recognition/linux/face_recognition_detect_completed.png"
            detect_person_unrecognized = HelperBase.get_project_dir() + "/data/images/face_recognition/linux/face_recognition_person_unrecognized.png"
            detect_completed_incabin = HelperBase.get_project_dir() + "/data/images/face_recognition/linux/face_recognition_detect_completed_incabin.png"
        elif platform_name == "Windows":
            pass

    def click_add_person_button(self):
        if pyautogui.locateOnScreen(add_person_button, region=(934, 425, 1268, 2668), confidence=0.8) is not None:
            pyautogui.click(pyautogui.locateCenterOnScreen(add_person_button))
            return True
        return False

    def confirm_detection(self, template, region):
        if pyautogui.locateOnScreen(template, region=(region[0], region[1], region[2], region[3]), confidence=0.9) is not None:
            return True
        return False

    def compare_templates(self, p, counter, template):
        while p.poll() is None:
            screenshot = pyautogui.screenshot(region=(920, 380, 1570, 920))
            screenshot.save(HelperBase.get_project_dir() + "/outputs/tmp.png")
            counter = self.get_match_template(counter, HelperBase.get_project_dir() + "/outputs/tmp.png", template)
        return counter

    def add_person_confirm_adding_with_process(self, p, flag_templates_found):
        while p.poll() is None:
            if self.confirm_detection(detect_person_unrecognized, [934, 425, 1268, 2668]):
                while p.poll() is None:
                    if self.click_add_person_button():
                        while p.poll() is None:
                            if self.confirm_detection(detect_completed, [934, 425, 1268, 2668]):
                                while p.poll() is None:
                                    if self.confirm_detection(detect_completed_incabin, [370, 510, 980, 897]):
                                        flag_templates_found = True
                                        break
                                    else:
                                        time.sleep(2)
                                break
                            else:
                                time.sleep(2)
                        break
                    else:
                        time.sleep(2)
                break
            else:
                time.sleep(2)
        return flag_templates_found

    def add_person_confirm_adding_with_future(self, future, flag_templates_found):
        while future.running():
            if self.confirm_detection(detect_person_unrecognized, [934, 425, 1268, 2668]):
                while future.running():
                    if self.click_add_person_button():
                        while future.running():
                            if self.confirm_detection(detect_completed, [934, 425, 1268, 2668]):
                                flag_templates_found = True
                                break
                            else:
                                time.sleep(2)
                        break
                    else:
                        time.sleep(2)
                break
            else:
                time.sleep(2)
        return flag_templates_found

    def add_person_confirm_adding_kill_process(self, p, flag_templates_found):
        while p.poll() is None:
            if self.confirm_detection(detect_person_unrecognized, [934, 425, 1268, 2668]):
                while p.poll() is None:
                    if self.click_add_person_button():
                        while p.poll() is None:
                            if self.confirm_detection(detect_completed, [934, 425, 1268, 2668]):
                                while p.poll() is None:
                                    if self.confirm_detection(detect_completed_incabin, [370, 510, 980, 897]):
                                        flag_templates_found = True
                                        p.kill()
                                        break
                                    else:
                                        time.sleep(2)
                                break
                            else:
                                time.sleep(2)
                        break
                    else:
                        time.sleep(2)
                break
            else:
                time.sleep(2)
        return flag_templates_found

    def get_match_template(self, counter, screen, template):
        img_rgb = cv2.imread(screen)
        #cv2.imwrite(screen+"_" + datetime.now().strftime("%Y%m%d%H%M%S.%f") + ".png", img_rgb)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

        template = cv2.imread(template, 0)

        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

        threshold = 0.99

        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            cv2.imwrite(HelperBase.create_test_dir("passed") + "/screenshot_" + datetime.now().strftime("%Y%m%d%H%M%S.%f") + ".png", img_rgb)
            counter += 1
        cv2.waitKey(0)
        return counter