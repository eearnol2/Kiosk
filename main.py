from Input import input_handler
from Pages import map, info
from Pages import Calibration_Screen
from Utils import config
from Utils.logger import log_sys_info
from Elements import window_elements

config.initialize()  # Loads config settings
log_sys_info()  # Logs information about system for debug purposes
input_handler.initialize()  # Starts up input handler

master = window_elements.WindowManager()

if config.use_tracker:
    Calibration_Screen.run(master)
else:
    info.run(master, "WannerHall")  # Use this to enter directly to info screen
    #map.run(master)  # Runs entry point for GUI

window_elements.run_master(master)
input_handler.close()  # If master stops, close input handler
