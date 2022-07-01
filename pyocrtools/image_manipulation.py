# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 09:51:46 2022

@author: brendans1020
"""

from pathlib import Path

import cv2

import matplotlib.pyplot as plt
import numpy as np

#My py
from image_acquisition import AcquireImage
from json5_reader import Json5Reader


class ImageManipulation:
    """
    Class containing image manipulation functions

    Use of **kwargs as inputs to all aligns with calling approach from
    field_manager, even if they are superfluous here
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
    def dilate(self, **kwargs):
        """
        Dilate the image

        Params
        ------
        kwargs : <dict>

        Returns
        -------
        <image>

        """
        if "img" in kwargs:
            img = kwargs["img"]
        else:
            img = self.image

        if "iterations" in kwargs:
            iterations = int(kwargs["iterations"])
        else:
            iterations = 1
        kernel = np.ones((1, 1), np.uint8)
        return cv2.dilate(img, kernel, iterations=iterations)

    # -------------------------------------------------------------------------
    def erode(self, **kwargs):
        """
        Erode the image

        Params
        ------
        kwargs : <dict>

        Returns
        -------
        <image>

        """
        if "img" in kwargs:
            img = kwargs["img"]
        else:
            img = self.image

        if "iterations" in kwargs:
            iterations = int(kwargs["iterations"])
        else:
            iterations = 1
        kernel = np.ones((1, 1), np.uint8)
        return cv2.erode(img, kernel, iterations=iterations)

    # -------------------------------------------------------------------------
    def greyscale(self, **kwargs):
        """
        Convert the image to a greyscale

        Params
        ------
        kwargs : <dict>   [not used, just retained for consistency elsewhere]

        Returns
        -------
        <image>

        """
        if "img" in kwargs:
            img = kwargs["img"]
        else:
            img = self.image

        try:
            grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        except Exception:
            print("Unable to perform greyscale on image")
            grey = img
        return grey

    # -------------------------------------------------------------------------
    def invert(self, **kwargs):
        """
        Invert the image colour map

        Params
        ------
        kwargs : <dict>   [not used, just retained for consistency elsewhere]

        Returns
        -------
        <image>

        """
        if "img" in kwargs:
            img = kwargs["img"]
        else:
            img = self.image

        return cv2.bitwise_not(img)

    # -------------------------------------------------------------------------
    def resize(self, **kwargs):
        """
        Resize the image

        Params
        ------
        kwargs : <dict>

        Returns
        -------
        <image>

        """
        if "img" in kwargs:
            img = kwargs["img"]
        else:
            img = self.image

        if "fx" in kwargs:
            fx = kwargs["fx"]
        else:
            fx = 2

        if "fy" in kwargs:
            fy = kwargs["fy"]
        else:
            fy = 2

        if "interpolation" in kwargs:
            interpolation = kwargs["interpolation"]

            rtn = cv2.resize(img, None, fx=fx, fy=fy,
                             interpolation=interpolation)
        else:
            rtn = cv2.resize(img, None, fx=fx, fy=fy,
                             interpolation=cv2.INTER_CUBIC)

        return rtn

    # -------------------------------------------------------------------------
    def threshold(self, **kwargs):
        """
        Apply thresholding to an image

        Params
        ------
        kwargs : <dict>
            If applying MedianBlur, it must be an odd number and greater than 1
            i.e. 3, 5, 7 etc

        Returns
        -------
        <image>

        """
        if "img" in kwargs:
            img = kwargs["img"]
        else:
            img = self.image

        img0 = self.greyscale(**{"img": img})
        if "MedianBlur" in kwargs and kwargs["MedianBlur"] != "False":
            img0 = cv2.medianBlur(img0, int(kwargs["MedianBlur"]))

        if "Binary_OTSU" in kwargs and kwargs["Binary_OTSU"] == "True":
            rtn = cv2.threshold(img0, 0, 255,
                                cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        else:
            print("Unable to perform thresholding, invalid params, " +
                  "returning original image")
            rtn = img  # Just return raw image
        return rtn


# -----------------------------------------------------------------------------
# ---- main
if __name__ == "__main__":

    cwd = Path.cwd()
    params = {"ImageFile":
              str(cwd.parent /
                  r"tests\supportingdata\machineStatus_Header.png")
              }
    img_handle = AcquireImage(**params)
    img_handle.open_image()
    img = img_handle.return_data("cv_image")

    manip_handle = ImageManipulation(**{"image": img})

    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

    grey = manip_handle.greyscale()
    plt.imshow(grey, cmap=plt.get_cmap('gray'))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

    bigger1 = manip_handle.resize(**{"fx": 2, "fy": 2})
    plt.imshow(cv2.cvtColor(bigger1, cv2.COLOR_BGR2RGB))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

    bigger2 = manip_handle.resize(**{"fx": 4, "fy": 4})
    plt.imshow(cv2.cvtColor(bigger2, cv2.COLOR_BGR2RGB))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

    thres1 = manip_handle.threshold(**{"Binary_OTSU": "True",
                                       })
    plt.imshow(cv2.cvtColor(thres1, cv2.COLOR_BGR2RGB))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

    thres2 = manip_handle.threshold(**{"Binary_OTSU": "True",
                                       "MedianBlur": "3",
                                       })
    plt.imshow(cv2.cvtColor(thres2, cv2.COLOR_BGR2RGB))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

    invert1 = manip_handle.invert()
    plt.imshow(cv2.cvtColor(invert1, cv2.COLOR_BGR2RGB))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

    invert2 = manip_handle.invert(**{"img": thres2})
    plt.imshow(cv2.cvtColor(invert2, cv2.COLOR_BGR2RGB))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

    erode1 = manip_handle.erode()
    plt.imshow(cv2.cvtColor(erode1, cv2.COLOR_BGR2RGB))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

    dilate1 = manip_handle.dilate()
    plt.imshow(cv2.cvtColor(dilate1, cv2.COLOR_BGR2RGB))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()
