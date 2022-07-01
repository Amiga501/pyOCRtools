# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 21:20:15 2022

brendan.sloan@mourneaerospace.com
"""

from collections import defaultdict
from pathlib import Path

import cv2
import string

import matplotlib.pyplot as plt  # For debugging only, can remove from final
import numpy as np
import pytesseract as pyt

from image_acquisition import AcquireImage
from json5_reader import Json5Reader

class CaptureOCR:
    """
    Class for running the OCR method


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

        self.config_reader()

    # -------------------------------------------------------------------------
    def config_reader(self):
        """
        Handles the interfacing to the JSON reader

        Not done internal to this class to better allow future expansion of
        reader functionality

        Params
        ------
        None

        Returns
        -------
        None

        """
        params = {"filePath": str(Path.cwd() / "config.json5")}
        config_file = Json5Reader(**params).read_json()
        if "tesseract_path" not in config_file:
            print("You have not configured the tesseract path within the " +
                  "config file, the OCR capture process won't work")
        else:
            pyt.pytesseract.tesseract_cmd = config_file["tesseract_path"]

    # -------------------------------------------------------------------------
    def image_to_data(self, **kwargs):
        """
        Runs OCR on cv2Image, optional kwarg params to pass to pyt

        Params
        ------
        kwargs : <dict>
            Dictionary of optional parameters to pass to pytesseract

        Returns
        -------


        """
        img_rgb = cv2.cvtColor(self.cv2Image, cv2.COLOR_BGR2RGB)

        param_headers = ["lang", "config", "nice",
                         "timeout", "pandas_config"]
        # The above are the available config items for pytesseract as per pypi
        # We need to keep output_type as a dataframe for confidence measure,
        # so it is not adjustable

        are_configs = []
        are_configs = [i for i in param_headers if i in kwargs]
        if are_configs:
            # User may have defined custom parameters for call
            # Currently no checks on validity of user inputs, delegate to pyt
            sub_kwargs = {}
            for k in are_configs:
                sub_kwargs[k] = kwargs[k]
            self.ocr = pyt.image_to_data(
                img_rgb, **sub_kwargs, output_type="data.frame")
            self.ocr_string = pyt.image_to_string(
                img_rgb, **sub_kwargs).strip()  # Can try to clean a bit
        else:
            self.ocr = pyt.image_to_data(img_rgb, output_type="data.frame")
            self.ocr_string = pyt.image_to_string(
                img_rgb).strip()  # Can try to clean a bit

        self.performance_manager()

    # -------------------------------------------------------------------------
    def performance_manager(self):
        """
        Manage the characterisation of OCR performance

        Params
        ------
        None

        Returns
        -------
        None

        """
        self.performance_confidence()
        self.performance_irregular_chars()

        # Aggregate
        self.score = np.mean([self.score_confidence,
                              self.score_irregular_chars])

    # -------------------------------------------------------------------------
    def performance_confidence(self):
        """
        Produce a score for performance based on pytesseract's own confidence

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        ocr = self.ocr
        ocr = ocr[ocr["text"].notnull()]  # Filter out the nan text entries
        # Note, a nan entry is not the same as a blank within ocr
        avg_confidence = ocr.conf.mean()

        # May add some more fancy distribution to bias toward lower scores
        # later

        self.score_confidence = avg_confidence

    # -------------------------------------------------------------------------
    def performance_irregular_chars(self):
        """
        Produce a score for performance based on presence of irregular chars

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        ocr_string = self.ocr_string

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Candidate for removal, unused
        ocr = self.ocr
        ocr = ocr[ocr["text"].notnull()]  # Filter out the nan text entries
        # Note, a nan entry is not the same as a blank within ocr

        # Combine all text entries into one blob
        text_values = ocr["text"].values
        text_values = [str(i) for i in text_values]
        text_blob = "".join(text_values)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Declare our characters and rankings
        chars = \
            {0: string.ascii_letters + string.digits,
             # These are the most likely
             0.1: ' ',
             # Not likely to be problematic, but can mean missed text
             3: string.punctuation,
             # These are less frequent, and could be either misinterpretation
             # or ok
             5: "all others",
             # These are likely problematic. Don't worry if this isn't entered
             # in  the iterator, we'll catch them later on with a not [] check
             }
        # Basis of above is lower score the better, we'll then do an inversion
        # at the end based on total char count

        found_chars = defaultdict(int)
        for char in ocr_string:
            # Tried this with text_blob, better with ocr_string
            found_chars[char] += 1

        ranking = {}
        running_total = 0
        for char in found_chars:
            weight = [k for k, v in chars.items() if char in v]
            if not weight:
                weight = [5]

            score = found_chars[char] * weight[0]
            ranking[char] = score
            running_total = running_total + score

        # Do the inversion and factor by 100. A score of 100 would then mean
        # 100% of our characters are conventional alphanumerics
        final_score = 100*(len(ocr_string) - running_total)/len(ocr_string)
        self.score_irregular_chars = final_score

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
    params1 = {"ImageFile":
                  str(cwd.parent /
                      r"tests\supportingdata\machineStatus_Header.png")
              }

    img1 = AcquireImage(**params1).open_image()

    params2 = {"cv2Image": img1,
               }
    handle = CaptureOCR(**params2)
    handle.image_to_data(**{"lang": "eng+fra"})

    score = handle.return_data("score")
