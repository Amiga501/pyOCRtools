# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 09:54:52 2022

@author: brendan.sloan@mourneaerospace.com

"""

from pathlib import Path

import inspect

import multiprocessing as mp

# My py
from image_acquisition import AcquireImage
from image_manipulation import ImageManipulation
from capture_ocr import CaptureOCR
from json5_reader import Json5Reader


# -----------------------------------------------------------------------------
class FieldManager:
    """
    Manage the workflow from entry gate to exit gate

    The field manager oversees the entry through the starting gate, the various
    paths walked through the field, execution and scoring of ocr performance
    (via external call), then ranking of the paths at the exit gate of the
    field

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

        self.image = self.raw_image  # Just retain the raw_image incase

        self.field_reader()
        self.list_manipulation_functions()
        self.field_marshall()

    # -------------------------------------------------------------------------
    def field_marshall(self):
        """
        Master controller for fields

        Params
        ------
        None

        Returns
        -------
        None

        """
        for field_name, field_data in self.fields.items():
            print("Currently working on: " + field_name)
            self.paths = field_data
            field_results = self.path_controller_ST()

            # Update the control image to the best ranked
            self.image = field_results[0]["img"]

        # At the end, we should have a decent image and string
        self.final_string = field_results[0]["string"]
        self.final_score = field_results[0]["score"]

    # -------------------------------------------------------------------------
    def field_reader(self):
        """
        Handle the interfacing to the JSON reader

        Not done internal to this class to better allow future expansion of
        reader functionality

        Params
        ------
        None

        Returns
        -------
        None

        """
        params = {"filePath": self.field_file}
        self.fields = Json5Reader(**params).read_json()

    # -------------------------------------------------------------------------
    def list_manipulation_functions(self):
        """
        Gathers a dict of handles of functions within ImageManipulation class

        Params
        ------
        None

        Returns
        -------
        None

        """
        foos0 = dict(inspect.getmembers(
            ImageManipulation(), predicate=inspect.ismethod))

        foos1 = {}
        for foo in foos0.keys():
            if foo[:2] != "__":
                # Isn't a dunder, add to foos1
                foos1[foo] = foos0[foo]

        self.manip_methods = foos1

    # -------------------------------------------------------------------------
    def path_controller_SMP(self):
        """
        SMP controller for paths

        Params
        ------
        None

        Returns
        -------
        <list> of results

        """
        pool = mp.Pool(ncpus=mp.cpu_count())
        smp_work = []

        smp_results = []

        for path_name, path_data in self.paths.items():
            kwargsIn = {"path": path_data}
            smp_work.append(pool.apply_async(self.path_runner, kwds=kwargsIn))

        for iProcess in range(0, len(smp_work)):
            smp_results.append(smp_work[iProcess].get())

        return smp_results

    # -------------------------------------------------------------------------
    def path_controller_ST(self):
        """
        ST controller for paths

        Params
        ------
        None

        Returns
        -------
        <list> of results

        """
        st_results = []

        img = self.image

        for path_name, path_data in self.paths.items():
            kwargsIn = {"path": path_data,
                        "img": img}
            rtn = self.path_runner(**kwargsIn)
            st_results.append(rtn)

        # Filter results for paths that didn't complete
        st_results2 = [res for res in st_results if res["status"] is True]
        # Rank the results
        ranked_results = sorted(st_results2, key=lambda d: d["score"],
                                reverse=True)

        return ranked_results

    # -------------------------------------------------------------------------
    def path_runner(self, **kwargs):
        """
        Run an individual path

        Params
        ------
        kwargs : <dict>

        Returns
        -------
        <dict>

        """
        list_steps = kwargs["path"]
        flag_abandoned = False

        img = kwargs["img"]

        for step in list_steps:
            if not flag_abandoned:
                foo = step["foo"]
                params = step["params"]

                if foo not in self.manip_methods:
                    # The function requested doesn't exist in the manipulation
                    # methods, cannot continue down this path
                    flag_abandoned = True
                    img = kwargs["img"]
                    break
                else:
                    kwargs1 = {"foo": foo,
                               "params": params,
                               "img": img}

                    img = self.manip_methods[foo](**kwargs1)

        # Can then send to ocr
        # In event of abandonment, just send the default image
        params2 = {"cv2Image": img,
                   }
        handle = CaptureOCR(**params2)
        handle.image_to_data(**{"lang": "eng+fra"})
        score = handle.return_data("score")
        string = handle.return_data("ocr_string")

        rtn = {"img": img,
               "score": score,
               "status": not(flag_abandoned),
               "string": string,
               }

        return rtn

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

    imgHandle = AcquireImage(
        **{"ImageFile": str(cwd.parent / r"tests\supportingdata" /
                            "DiscImage_81.png")})
                            # machineStatus_Header.png")})
    imgHandle.open_image()
    img_file = imgHandle.return_data("cv_image")

    params = {"field_file": str(cwd / "field_file.json5"),
              "raw_image": img_file,
              }
    handle = FieldManager(**params)
    final_string = handle.return_data("final_string")
    final_score = handle.return_data("final_score")
