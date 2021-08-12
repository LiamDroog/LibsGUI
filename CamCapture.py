"""
##################################################
Controls the BFS U3 13Y3 camera. Adapted from
FLIR provided example code for our use
##################################################
# Author:   Liam Droog
# Email:    droog@ualberta.ca
# Year:     2021
# Version:  V.1.0.0
##################################################
"""

import PySpin
import sys
import time
import keyboard
import os
import tkinter as tk
from tkinter import font
from PIL import ImageTk, Image
import multiprocessing as mp

class TriggerType:
    SOFTWARE = 1
    HARDWARE = 2


CHOSEN_TRIGGER = TriggerType.HARDWARE
global shot_num

# file_extension = 'png' # needs to be an input for main

def configure_trigger(cam):
    """1
    This function configures the camera to use a trigger. First, trigger mode is
    ensured to be off in order to select the trigger source. Trigger mode is
    then enabled, which has the camera capture only a single image upon the
    execution of the chosen trigger.

     :param cam: Camera to configure trigger for.
     :type cam: CameraPtr
     :return: True if successful, False otherwise.
     :rtype: bool
    """

    print('*** CONFIGURING CAMERA ***\n')

    if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
        print('Software trigger chosen...')
    elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
        print('Hardware trigger chose...')

    try:
        result = True

        # Ensure trigger mode off
        # The trigger must be disabled in order to configure whether the source
        # is software or hardware.
        if cam.TriggerMode.GetAccessMode() != PySpin.RW:
            print('Unable to disable trigger mode (node retrieval). Aborting...')
            return False

        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

        print('Trigger mode disabled...')

        # Set TriggerSelector to FrameStart
        # For this example, the trigger selector should be set to frame start.
        # This is the default for most cameras.
        if cam.TriggerSelector.GetAccessMode() != PySpin.RW:
            print('Unable to get trigger selector (node retrieval). Aborting...')
            return False

        cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)

        print('Trigger selector set to frame start...')

        # Select trigger source
        # The trigger source must be set to hardware or software while trigger
        # mode is off.
        if cam.TriggerSource.GetAccessMode() != PySpin.RW:
            print('Unable to get trigger source (node retrieval). Aborting...')
            return False

        if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
            cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
            print('Trigger source set to software...')
        elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
            cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
            print('Trigger source set to hardware...')

        # Turn trigger mode on
        # Once the appropriate trigger source has been set, turn trigger mode
        # on in order to retrieve images using the trigger.
        cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        print('Trigger mode turned back on...')

    except PySpin.SpinnakerException as ex:
        print('Error in config_trigger: %s' % ex)
        return False

    return result


def grab_next_image_by_trigger(cam):
    """
    This function acquires an image by executing the trigger node.

    :param cam: Camera to acquire images from.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True
        # Use trigger to capture image
        # The software trigger only feigns being executed by the Enter key;
        # what might not be immediately apparent is that there is not a
        # continuous stream of images being captured; in other examples that
        # acquire images, the camera captures a continuous stream of images.
        # When an image is retrieved, it is plucked from the stream.

        if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
            # Get user input
            input('Press the Enter key to initiate software trigger.')

            # Execute software trigger
            if cam.TriggerSoftware.GetAccessMode() != PySpin.WO:
                print('Unable to execute trigger. Aborting...')
                return False

            cam.TriggerSoftware.Execute()

            # TODO: Blackfly and Flea3 GEV cameras need 2 second delay after software trigger

        elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
            print('Use the hardware to trigger image acquisition.')

    except PySpin.SpinnakerException as ex:
        print('Error in grab_next_by_trigger: %s' % ex)
        return False

    return result


def acquire_images(cam, twd, file_extension):
    global shot_num
    """
    This function acquires and saves 10 images from a device.
    Please see Acquisition example for more in-depth comments on acquiring images.

    :param cam: Camera to acquire images from.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** IMAGE ACQUISITION ***\n')
    try:
        result = True

        # Set acquisition mode to continuous
        if cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
            print('Unable to set acquisition mode to continuous. Aborting...')
            return False

        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        print('Acquisition mode set to continuous...')

        #  Begin acquiring images
        cam.BeginAcquisition()

        print('Acquiring images...')

        # Get device serial number for filename
        device_serial_number = ''
        if cam.TLDevice.DeviceSerialNumber.GetAccessMode() == PySpin.RO:
            device_serial_number = cam.TLDevice.DeviceSerialNumber.GetValue()

            print('Device serial number retrieved as %s...' % device_serial_number)

        # get ith number and save
        # Retrieve, convert, and save images
        while True:
            try:
                if keyboard.is_pressed('esc'):
                    break
                #  Retrieve the next image from the trigger
                # result &= grab_next_image_by_trigger(cam)

                #  Retrieve next received image
                image_result = cam.GetNextImage(100)

                #  Ensure image completion
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:

                    #  Print image information
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()
                    print('Grabbed Image %d, width = %d, height = %d' % (shot_num, width, height))

                    #  Convert image to mono 8
                    image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)

                    # Create a unique filename
                    if device_serial_number:
                        filename = os.path.join(twd, 'Shot-%s-%d.%s' % (device_serial_number, shot_num, file_extension))
                    else:  # if serial number is empty
                        filename = os.path.join(twd, 'Shot-%d.%s' % (shot_num, file_extension))

                    # Save image
                    image_converted.Save(filename)
                    # don't need this bit below as it'll be handled by a separate process!
                    # img = imgViewer(filename)
                    # img = mp.Process(target=imgViewer, args=(filename,))
                    # img.start()

                    print('Image saved at %s\n' % filename)

                    #  Release image
                    image_result.Release()
                    shot_num += 1

            except PySpin.SpinnakerException as ex:
                pass

        # End acquisition
        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error in acquire_images: %s' % ex)

    return result


def reset_trigger(cam):
    """
    This function returns the camera to a normal state by turning off trigger mode.

    :param cam: Camera to acquire images from.
    :type cam: CameraPtr
    :returns: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True
        # Ensure trigger mode off
        # The trigger must be disabled in order to configure whether the source
        # is software or hardware.
        if cam.TriggerMode.GetAccessMode() != PySpin.RW:
            print('Unable to disable trigger mode (node retrieval). Aborting...')
            return False

        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

        print('Trigger mode disabled...')

    except PySpin.SpinnakerException as ex:
        print('Error in reset_trigger: %s' % ex)
        result = False

    return result


def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** DEVICE INFORMATION ***\n')

    try:
        result = True
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

        else:
            print('Device control information not available.')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def run_single_camera(cam, twd, file_extension):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True
        err = False

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Configure trigger
        if configure_trigger(cam) is False:
            return False

        # Acquire images
        result &= acquire_images(cam, twd, file_extension)

        # Reset trigger
        result &= reset_trigger(cam)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error in run_single_cam: %s' % ex)
        result = False

    return result


def set_directory(twd, file_extension):
    global shot_num
    if not os.path.exists(twd):
        os.mkdir(twd)
        shot_num = 1
    else:
        print('Images Directory found - Parsing for images')
        if [i for i in os.listdir(twd) if i[-3:] == file_extension]:
            present_shots = [int(i[:-4].split('-')[-1]) for i in os.listdir(twd) if i[-3:] == file_extension]
            shot_num = max(present_shots) + 1
        else:
            shot_num = 1

    print('Shot num: ', shot_num)


def main(directory, file_extension):
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
    st = time.time()

    twd = directory
    # twd = os.path.join(owd, 'Images')
    set_directory(twd, file_extension)
    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    # Finish if there are no cameras
    if num_cameras == 0:
        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras connected!')
        input('Done! Press Enter to exit...')
        return False

    # Run example on each camera
    for cam in cam_list:
        result &= run_single_camera(cam, twd, file_extension)

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()
    print('Done!')
    return result


# class imgViewer:
#     def __init__(self, targetImage):
#         self.window = tk.Tk(className='\Image Viewer Doohickey')
#         # font = tk.font.Font(family='Helvetica', size=36, weight='bold')
#         imgFrame(self.window, targetImage, posX=0, posY=0, columnspan=2)
#         # self.acceptBtn = tk.Button(master=self.window, text='Accept', command=self.accept, bg='green', font=font)
#         # self.acceptBtn.grid(row=2, column=1, sticky='nsew', ipady=25)
#         #
#         # self.rejectBtn = tk.Button(master=self.window, text='Reject', command=self.reject, bg='red', font=font)
#         # self.rejectBtn.grid(row=2, column=0, sticky='nsew', ipady=25)
#         # self.window.protocol("WM_DELETE_WINDOW", self.dontQuit)
#         self.window.after(3000, lambda: self.window.destroy())
#         self.window.mainloop()
#
#     def dontQuit(self):
#         pass
#
#     def accept(self):
#         self.accepted = True
#         self.window.destroy()
#
#     def reject(self):
#         self.accepted = False
#         self.window.destroy()
#
# class imgFrame:
#     def __init__(self, master, targetImage, posX, posY, columnspan=1, rowspan=1):
#         self.window = tk.Frame(master=master)
#         font = tk.font.Font(family='Helvetica', size=36, weight='bold')
#         self.header = tk.Label(master=self.window, text=targetImage.split('\\')[-1], font=font)
#         self.header.grid(row=0, column=0, columnspan=2)
#         # self.imageFrame = tk.Frame(master=self.window)
#         self.image = Image.open(targetImage)
#         factor = 0.5
#         self.image = self.image.resize((int(self.image.size[0]*factor) , int(self.image.size[1]*factor)), Image.ANTIALIAS)
#         self.tkimage = ImageTk.PhotoImage(self.image)
#         self.label = tk.Label(master=self.window, image=self.tkimage)
#         self.label.image = self.tkimage
#         self.label.grid(row=1, column=0, columnspan=2)
#
#         self.window.grid(row=posY, column=posX, columnspan=columnspan, rowspan=rowspan)
#

if __name__ == '__main__':
    # imgViewer('C:/Users/Liam/PycharmProjects/BaldrControlHub py3.8/Images/Shot-19129388-2.bmp')
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
