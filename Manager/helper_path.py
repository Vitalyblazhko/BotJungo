import getpass
import os
import platform


class HelperPath:

    def __init__(self):
        global user_name
        user_name = getpass.getuser()
        global platform_name
        platform_name = platform.system()

    @staticmethod
    def detect_path():
        path = []

        if platform_name == "Linux":
            # default yml, path[0]
            path.append(HelperPath.get_path_to_codriver_directory_linux() + "/data/codriver_sample_config.yml")
            # yml, path[1]
            path.append("/var/codriver/data/codriver_sample_config.yml")
            # video file dms, path[2]
            path.append("/net/fs/arch/home/vitalyb/shared/video_test/oded_hsae.mp4")
            #path.append("/home/" + user_name + "/Desktop/video/hand.mp4")
            # saved_data directory, path[3]
            path.append("/var/codriver/saved_data")
            # window_positions file, path[4]
            path.append("/var/codriver/data/window_positions.csv")
            # data directory, path[5]
            path.append("/var/codriver/data")
            # saved_face_recognition_data directory, path[6]
            path.append("/var/codriver/saved_face_recognition_data")


        elif platform_name == "Windows":
            # TODO: windows path handling
            # default yml, path[0]
            path.append(HelperPath.get_path_to_codriver_directory_linux() + "/data/codriver_sample_config.yml")
            # yml, path[1]
            path.append("C:\\Users\\" + user_name + "\\CoDriver\\data\\codriver_sample_config.yml")
            # video file dms, path[2]
            path.append("/home/vitalyb/Desktop/video/oded_hsae.mp4")
            # path.append("/home/vitalyb/Desktop/video/hand.mp4")
            # saved_data directory, path[3]
            path.append("C:\\Users\\" + user_name + "\\CoDriver\\saved_data")
            # window_positions file, path[4]
            path.append("C:\\Users\\" + user_name + "\\CoDriver\\data\\window_positions.csv")
            # data directory, path[5]
            path.append("C:\\Users\\" + user_name + "\\CoDriver\\data")
            # saved_face_recognition_data directory, path[6]
            path.append("C:\\Users\\" + user_name + "\\CoDriver\\saved_face_recognition_data")
        return path

    @staticmethod
    def get_path_to_codriver_directory_linux():
        path_to_codriver_directory = ""
        path_before_codriver_derectory = "/home/"+ user_name + "/Desktop/"

        for dirpath, dirnames, filenames in os.walk(path_before_codriver_derectory, topdown=False):
            for dirname in dirnames:
                if dirname.startswith("Jungo-CoDriver"):
                    path_to_codriver_directory = os.path.join(dirpath, dirname)
                    break
        return path_to_codriver_directory