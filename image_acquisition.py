# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:25:57 2022

@author: brendans1020
"""
from copy import deepcopy
from pathlib import Path

import numpy as np

import cv2
import pyscreeze


# -----------------------------------------------------------------------------
def get_variable(kwargs, class_handle, name, optional=False):
    """
    Function for acquiring a variable entry for "name"
    Sources in order of preference:
        kwargs
        class_handle

    Params
    ------
    kwargs : <dict> of keyword arguments
    class_handle : <class> Name of class
    name : <str> Name of variable to acquire
    optional : <bool> Set TRUE if the variable is optional, means no warning

    """
    if name in kwargs:
        var = kwargs[name]
    elif hasattr(class_handle, name):
        var = getattr(class_handle, name)
    else:
        var = None
        if not optional:
            print("Unable to find an entry for variable: " + str(name) + "\n" +
                  "Have you passed this into either class or function " +
                  "correctly?")
    return var


# -----------------------------------------------------------------------------
class AcquireImage:
    """
    Class for acquiring an image

    Image can be from pyscreeze screenshot, or an image file

    Output will be OpenCV BGR form

    """

    # -------------------------------------------------------------------------
    def __init__(self, **kwargs):
        """
        Instantiate the class

        Params
        ------
        kwargs : <dict>


        Returns
        -------
        None

        """
        # This will set all entries within kwargs into the class variable space
        for key_val in kwargs.items():
            setattr(self, key_val[0], key_val[1])

    # -------------------------------------------------------------------------
    def screen_shot(self, **kwargs):
        """
        Acquire a screenshot via pyscreeze

        Params
        ------
        kwargs : <dict>
            ImageFile : <str> full path to image
            BoundBox : <tuple> 4 entry tuple of (left, top, width, height)
                for downselecting a region to screen shot. Very useful for OCR
            [Both above optional if already in class variables via
             instantiation]

        Returns
        -------
        <image> A return that the user will usually ignore, but may be of value
            for debugging purposes

        """
        bound_box = get_variable(kwargs, self, "BoundBox", optional=True)
        try:
            if not bound_box:
                self.raw_image = pyscreeze.screenshot()
            else:
                self.raw_image = pyscreeze.screenshot(region=bound_box)

            self.convert_RGB_to_BGR()

        except Exception:
            print("Failed to acquire/convert a screenshot")

    # -------------------------------------------------------------------------
    def convert_RGB_to_BGR(self, unit_type="uint32"):
        """
        Convert a RGB format image to an BGR numpy array

        Params
        ------
        unit_type : <string> Unsigned integer unit type for the numpy array
            [Optional param, default is uint32, often seen uint8 used too]

        Returns
        -------
        None

        """
        if self.raw_image:
            img0 = np.asarray(self.raw_image, dtype=unit_type)

            # Convert to BGR as per below
            img = deepcopy(img0)
            img[0,:,0] = img0[0,:,2]
            img[0,:,2] = img0[0,:,0]
            img[1,:,0] = img0[1,:,2]
            img[1,:,2] = img0[1,:,0]

            self.cv_image = img
        else:
            print("No RGB image available to convert to BGR")

    # -------------------------------------------------------------------------
    def open_image(self, **kwargs):
        """
        Acquire an image via opening a pre-existing image file

        Params
        ------
        kwargs : <dict>

        """
        image_file = get_variable(kwargs, self, "ImageFile")
        if image_file:
            if Path(image_file).exists():
                self.cv_image = cv2.imread(image_file)
                # Load using default params
            else:
                print("Invalid image file path specified, file not found")

    # -------------------------------------------------------------------------
    def return_data(self, attr):
        """
        Return the data 'attr' within the class

        Params
        ------
        None

        Returns
        -------
        None

        """
        if hasattr(self, attr):
            rtn = getattr(self, attr)
        else:
            print("Cannot find attribute: " + str(attr) + " to return")
            rtn = None
        return rtn


# -----------------------------------------------------------------------------
# ---- main
if __name__ == "__main__":

    cwd = Path.cwd()
    params = {"BoundBox": (1562, 645, 120, 70),
              "ImageFile":
                  str(cwd /
                      r"tests\supportingdata\machineStatus_Header.png")
              }

    # -------------------------------------------------------------------------
    # A few sanity checks, these can be offloaded to proper testing script(s)
    # later

    # Bound screenshots
    handle1 = AcquireImage(**params)
    r1a = handle1.screen_shot()
    r1b = handle1.return_data("cv_image")

    handle2 = AcquireImage()
    r2a = handle2.screen_shot(**params)
    r2b = handle2.return_data("cv_image")

    # Full screen
    handle3 = AcquireImage()
    r3a = handle3.screen_shot()
    r3b = handle3.return_data("cv_image")

    # Load image
    handle4 = AcquireImage(**params)
    r4a = handle4.open_image()
    r4b = handle4.return_data("cv_image")

    handle5 = AcquireImage()
    r5a = handle5.open_image(**params)
    r5b = handle5.return_data("cv_image")

    # Errors
    handle6 = AcquireImage()
    r6a = handle6.open_image()
    r6b = handle6.return_data("cv_image")

    params["ImageFile"] = \
        str(cwd /
            r"tests\supportingdata\machineStatus_Heade.png")
    handle7 = AcquireImage(**params)
    r7a = handle7.open_image()
    r7b = handle7.return_data("cv_image")
