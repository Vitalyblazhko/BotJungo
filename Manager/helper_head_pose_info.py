import csv
import getpass
import logging

from Manager.helper_base import HelperBase

class HelperHeadPoseInfo():

    def __init__(self):
        global user_name
        user_name = getpass.getuser()
        global LOGGER
        LOGGER = logging.getLogger(__name__)

    def compare_results(self, sample_csv, column_name, threshold, allowed_fails):
        frames_counter = []
        frames_len = len(HelperBase.read_csv_get_column_values(HelperBase.get_project_dir()+"/data/samples/"+sample_csv, column_name))
        for x in range(frames_len):
            frames_counter.append(x+1)
        source_values = HelperBase.read_csv_get_column_values(HelperBase.get_project_dir()+"/data/samples/"+sample_csv, column_name)
        processed_values = HelperBase.read_csv_get_column_values(HelperBase.get_saved_data_csv("person_results.csv"), column_name)

        with open(HelperBase.create_test_dir("results") + "/"+column_name+".csv", "w", newline='') as file:
            writer = csv.writer(file)

            writer.writerow(["Frame", "Source", "Processed"])
            for x in range(frames_len):
                writer.writerow([frames_counter[x], source_values[x], processed_values[x]])

        failed = HelperBase.get_failed_results(HelperBase.create_test_dir("results") + "/" + column_name + ".csv", threshold)

        LOGGER.info("Test name: " + HelperBase.get_test_name() + " - Failed results info on thresh +/-"+str(threshold)+":"
                                                                  "\nFailed frames: "+str(failed[1])+" from "+str(failed[0])+
                    "\nFailed percentage: "+str("%.2f" % round(failed[2], 2))+"\nMax difference: "+str("%.2f" % round(failed[3], 2))+" degrees")

        # Returns True if failed quantity of frames does not exceed allowed failed quantity
        return failed[1] < allowed_fails