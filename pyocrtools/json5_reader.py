# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 11:49:09 2022

@author: brendans1020
"""

import pyjson5


class Json5Reader:
    """
    Class for reading JSON5 files

    Done like this to allow future off-boarding to a full module with error
    handling. But for now, simple and happy-path only
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
    def read_json(self):
        """
        Read the JSON5 file

        Params
        ------
        None

        Returns
        -------
        <dict>  [or None in case of unsuccessful read]

        """
        try:
            with open(self.filePath, 'r') as f:
                rtn = pyjson5.decode_io(f)
        except Exception:
            print("Unable to read the JSON5 file")
            rtn = None
        return rtn
