#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Copyright (c) 2021 anoduck

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------------

'''
The purpose of this file is to convert a list of profiles generated during the 
friend exploration process by photo-scraper.py and to convert it into a file 
that can be used as input.txt for photo-scraper.py to use for scraping even 
more profiles.
'''

#===========================================================================
# *                            Imports
#===========================================================================

from furl import furl
from pathlib import Path
import fileinput
import os

#================================================
#                extract names
#================================================

def extract_usernames():
    _input = fileinput.input()
    print("Extracting Usernames")
    for line in _input:
        f = furl(line)
        print("Profile Link is " + line)
        fapath = f.pathstr.strip("/")
        if fapath == "profile.php":
            uid = f.args.popvalue('id')
            print("Found uid as: " + uid)
        else:
            uid = fapath
            print("Found uid as: " + uid)
        if fapath != "%0A" and len(fapath) > 1:
            i = open("input.txt", "a", encoding="utf-8", newline="\n")
            i.writelines(uid)
            i.write("\n")
            i.close()
        else:
            continue
    print("Completed extracting usernames")
#================================================
#                convert files
#================================================

class convert_file():
    CWD = os.getcwd()
    indt = CWD + "/" + "input.txt"
    if os.path.exists(indt) is True:
        print("Input.txt found")
        bkin = CWD + "/" + "input-backup.txt"
        if os.path.exists(bkin) is True:
            print("input-backup.txt is found")
            filename, extension = os.path.splitext(bkin)
            counter = 1
            while os.path.exists(indt):
                ninf = filename + str(counter) + extension
                counter += 1
                os.rename(indt, ninf)
            print("New Backup File is: " + ninf)
            extract_usernames()
        elif os.path.exists(bkin) is False:
            os.rename(indt, bkin)
            extract_usernames()
        else:
            print("Failed to create new backup of input.txt")
    elif os.path.exists(indt) is False:
        Path(indt).touch()
        if os.path.exists(indt):
            extract_usernames()
        else:
            print("Failed to create new input.txt")   
    else:
        print("input.txt is not in path.")

#------------------------------------------------
#                Main
#------------------------------------------------

if __name__ == "__main__":
    convert_file()
