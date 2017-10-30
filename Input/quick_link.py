from ctypes import *
from Utils.logger import log

dll = CDLL('Input\DLL\QuickLink2.dll')

error_list = ['OK', 'Invalid Device ID', 'Invalid Settings ID', 'Invalid Calibration ID', 'Invalid Target ID',
              'Invalid Password', 'Invalid Path', 'Invalid Duration', 'Invalid Pointer', 'Timeout Elapsed',
              'Internal Error', 'Buffer Too Small', 'Calibration Not Initialized', 'Device Not Started',
              'Device Not Supported', 'Settings Not Found', 'UNAUTHORIZED', 'Invalid Group']

connected_device = 0  # This is set on initialization


def __display_error(code):
    if code is not 0:
        log(error_list[code], 0)


def get_version():
    func = dll.QLAPI_GetVersion
    buffer_size = 32
    output = create_string_buffer(buffer_size)
    __display_error(func(c_int(buffer_size), output))
    return output.value.decode('UTF-8')


def device_enumerate():
    func = dll.QLDevice_Enumerate
    buffer_size = 5
    num_devices = c_int(buffer_size)
    num_devices_pointer = pointer(num_devices)
    device_buffer = (c_int * buffer_size)()
    device_buffer_pointer = pointer(device_buffer)
    func(num_devices_pointer, device_buffer_pointer)
    number = num_devices.value
    device_list = []
    for i in range(0, number):
        device_list.append(device_buffer[i])
    return device_list


def get_status(identifier):
    func = dll.QLDevice_GetStatus
    device_id = c_int(identifier)
    device_status = c_int()
    device_status_pointer = pointer(device_status)
    __display_error(func(device_id, device_status_pointer))
    return device_status.value


def start(identifier):
    func = dll.QLDevice_Start
    device_id = c_int(identifier)
    __display_error(func(device_id))


def initialize():
    device_list = device_enumerate()

    if len(device_list) is 0:
        log("No devices found", 0)
        return 0
    elif len(device_list) > 1:
        log("More than 1 device found", 1)

    global connected_device
    connected_device = device_list[0]

    for device in device_list:
        if get_status(device) is 1:
            log("Starting device " + str(device), 2)
            start(device)
            log(("Waiting for device " + str(device) + " to start"), 3)
            while get_status(device) is not 3:
                pass
        log(("Device " + str(device) + " started"), 3)


def stop_all():
    log("Stopping all devices", 3)
    func = dll.QLDevice_Stop_All
    __display_error(func())
    log("All devices stopped", 2)


class QLXYPairFloat(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float)
    ]


class QLEyeData(Structure):
    _fields_ = [
        ("Found", c_bool),
        ("Calibrated", c_bool),
        ("PupilDiameter", c_float),
        ("Pupil", QLXYPairFloat),
        ("Glint0", QLXYPairFloat),
        ("Glint1", QLXYPairFloat),
        ("GazePoint", QLXYPairFloat),
        ("Reserved", (c_voidp * 16))
    ]


class QLWeightedGazePoint(Structure):
    _fields_ = [
        ("Valid", c_bool),
        ("x", c_float),
        ("y", c_float),
        ("LeftWeight", c_float),
        ("RightWeight", c_float),
        ("Reserved", (c_voidp * 16))
    ]


class QLRectInt(Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int),
        ("width", c_int),
        ("height", c_int)
    ]


class QLImageData(Structure):
    _fields_ = [
        ("PixelData", c_char_p),
        ("Width", c_int),
        ("Height", c_int),
        ("Timestamp", c_double),
        ("Gain", c_int),
        ("FrameNumber", c_long),
        ("ROI", QLRectInt),
        ("ScaleFactor", c_float),
        ("Reserved", (c_voidp * 13))
    ]


class FrameData(Structure):
    _fields_ = [
        ("ImageData", QLImageData),
        ("LeftEye", QLEyeData),
        ("RightEye", QLEyeData),
        ("WeightedGazePoint", QLWeightedGazePoint),
        ("Focus", c_float),
        ("Distance", c_float),
        ("Bandwidth", c_int),
        ("DeviceID", c_int),
        ("Reserved", (c_voidp * 15))
    ]


class FrameObject:
    def __init__(self, frame_struct):
        self.x_pos = frame_struct.WeightedGazePoint.x
        self.y_pos = frame_struct.WeightedGazePoint.y
        self.is_valid = frame_struct.WeightedGazePoint.Valid


def get_frame():
    if connected_device is 0:
        log("Attempted to get data from unconnected device", 0)
        return None

    func = dll.QLDevice_GetFrame
    device_or_group = c_int(connected_device)
    frame_struct = FrameData()
    __display_error(func(device_or_group, c_int(1000), byref(frame_struct)))
    return FrameObject(frame_struct)


def apply_calibration(identifier, calibration):
    func = dll.QLDevice_ApplyCalibration
    device_id = c_int(identifier)
    calibration_id = c_int(calibration) #call the create or load fuction
    __display_error(func(device_id, calibration_id))
    return


class EyeRadius:
    def __init__(self, eye_struct):
        self.left_eye = eye_struct.LeftEye
        self.right_eye = eye_struct.RightEye


def calibrate_eye_radius(identifier):
    func = dll.QLDevice_CalibrateEyeRadius
    device_id = c_int(identifier)
    distance = c_int(60)
    eye_struct = FrameData()
    eye_radius = EyeRadius()
    left_radius_pointer = pointer(eye_radius.left_eye)
    right_radius_pointer = pointer(eye_radius.right_eye)
    __display_error(func(device_id, distance, left_radius_pointer, right_radius_pointer))
    return EyeRadius(eye_struct)


def calibration_load(calibration):
    func = dll.QLDevice_CalibrationLoad
    path = "path one", c_char   # Alec look at this it might need to be changed it is the path name created when the calibration is created
    path_pointer = pointer(path)
    calibration_id = c_int(calibration)
    calibration_id_pointer = pointer(calibration_id)
    __display_error(func(path_pointer, calibration_id_pointer))
    return


def calibration_save(calibration):
    func = dll.QLDevice_CalibrationSave
    path = "path one", c_char
    path_pointer = pointer(path)
    calibration_id = c_int(calibration)
    __display_error(func(path_pointer, calibration_id))
    return


def calibration_create():
    func = dll.QLDevice_CalibrationCreate
    calibration_source = c_int(0)
    calibration_id = c_int(0)
    calibration_id_pointer = pointer(calibration_id)
    __display_error(func(calibration_source, calibration_id_pointer))
    return calibration_id.value


def calibration_initialize(identifier, calibration):
    func = dll.QLDevice_CalibrationInitialize
    QL_CALIBRATION_TYPE_5 = c_int(0)
    device_id = c_int(identifier)
    calibration_id = c_int(calibration)
    calibration_type = QL_CALIBRATION_TYPE_5   # Alec we are planning on using the 5 point calibration type which in the program is written QL_CALIBRATION_TYPE_5 but it did not like that so we tried 5 you may need to change this
    __display_error(func(device_id, calibration_id, calibration_type))
    return


def calibration_get_targets():
    func = dll.QLDevice_CalibrationGetTargets
    calibration_id = calibration_create()
    target_size = c_int(5)   # Alec this was a random number I put in if the size of the buffer needs to be different change it
    num_targets = c_int(target_size)
    num_targets_pointer = pointer(num_targets)
    target_x = c_float(0) # Alec this I believe will only find the center point it will ned to be adjusted to find multiple point
    target_y = c_float(0)
    calibration_target_pointer = pointer(target_x, target_y)
    __display_error(func( calibration_id, num_targets_pointer, calibration_target_pointer))
    return


def calibration_calibrate(calibration, target):
    func = dll.QLDevice_CalibrationCalibrate
    calibration_id = c_int(calibration)
    target_id = c_int(target)       #Emily's program is needed 5 is just a place holder
    __display_error(func(calibration_id, target_id))
    return


def calibration_get_scoring(calibration,  target, eye_type):
    func = dll.QLDevice_CalibrationGetScoring
    calibration_id = c_int(calibration)
    target_id = c_int(target)     #Emily's program is needed 5 is just a place holder
    eye_type = c_int(eye_type)      # Alec I believe this is pulling the eye type from the above but it may need to be modify
    score_x = 0.01
    score_y = 0.01
    calibration_score_pointer = pointer(score_x, score_y)
    __display_error(func(calibration_id, target_id, eye_type, calibration_score_pointer))
    return


def calibration_get_status(calibration,  target, eye_type):
    func = dll.QLDevice_CalibrationGetStatus
    calibration_id = c_int(calibration)
    target_id = c_int(target)  # Emily's program is needed 5 is just a place holder
    eye_type = c_int(eye_type)
    calibration_status = c_int(0)  # This will be changed to an if statement at a later time
    calibration_status_pointer = pointer(calibration_status)
    __display_error(func(calibration_id, target_id, eye_type, calibration_status_pointer))
    cal_status = calibration_status.value
    return cal_status


def calibration_finalize(calibration):
    func = dll.QLDevice_CalibrationFinalize
    calibration_id = c_int(calibration)
    __display_error(func(calibration_id,))
    return


def calibration_cancel(calibration):
    func = dll.QLDevice_CalibrationCancel
    calibration_id = c_int(calibration)
    __display_error(func(calibration_id))
    return


def calibration_add_bias(calibration,  eye_type):
    func = dll.QLDevice_CalibrationAddBias
    calibration_id = c_int(calibration)
    eye_type = c_int(eye_type)
    xoffset = c_float(0)
    yoffset = c_float(0)
    __display_error(func(calibration_id, eye_type, xoffset, yoffset))
    return