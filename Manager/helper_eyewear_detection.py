import csv
import getpass
import logging
from Manager.helper_base import HelperBase

class HelperEyewearDetection:

    def __init__(self):
        global user_name
        user_name = getpass.getuser()
        global LOGGER
        LOGGER = logging.getLogger(__name__)

    def read_csv_return_eyewear(self, csv_file_name, column_name):
        counter_unknown = 0
        counter_none = 0
        counter_glasses = 0
        counter_sunglasses = 0
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
                    if row[column] == "unknown":
                        counter_unknown += 1
                    elif row[column] == "none":
                        counter_none += 1
                    elif row[column] == "glasses":
                        counter_glasses += 1
                    elif row[column] == "sunglasses":
                        counter_sunglasses += 1
                line_count += 1
        LOGGER.info("Test name: " + HelperBase.get_test_name() + " - Eyewear is detected as:"
                    "\nUnknown: " + str(counter_unknown) +
                    "\nNone: " + str(counter_none) +
                    "\nGlasses: " + str(counter_glasses) +
                    "\nSunglasses: " + str(counter_sunglasses) +
                    "\nTotal frames: "+ str(int(line_count)-1))
        return [int(line_count)-1, counter_unknown, counter_none, counter_glasses, counter_sunglasses]
