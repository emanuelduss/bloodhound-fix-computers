#!/usr/bin/env python
#
# By Rudolf & Misha :) KTHX!
#

import json
import os
import sys
import zipfile
import tempfile

def update_zip_file(zipname, filename, data):
    # generate a temp file
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipname))
    os.close(tmpfd)

    # create a temp copy of the archive without filename
    with zipfile.ZipFile(zipname, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment # preserve the comment
            for item in zin.infolist():
                if item.filename != filename:
                    zout.writestr(item, zin.read(item.filename))

    # replace with the temp archive
    os.remove(zipname)
    os.rename(tmpname, zipname)

    # now add filename with its new data
    with zipfile.ZipFile(zipname, mode='a', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, data)


def bloodhound_computer_fix(inputfile):
  print(f"Fixing {inputfile}...", end=' ')
  # open BloodHound archive and search for the file to fix
  archive = zipfile.ZipFile(inputfile, 'r')
  selected_file = None
  for filename in archive.namelist():
    if filename.endswith('_computers.json'):
      selected_file = filename
  old_file_data = archive.read(selected_file)

  # relevant parts of a computers.json file that parses correctly in bloodhound
  #ref_file = open(os.path.dirname(__file__) + '/computers_missing_properties.json')
  missing_properties = """
      {
      "data": [
        {
          "LocalAdmins": {
            "Results": [],
            "Collected": false,
            "FailureReason": null
          },
          "RemoteDesktopUsers": {
            "Results": [],
            "Collected": false,
            "FailureReason": null
          },
          "DcomUsers": {
            "Results": [],
            "Collected": false,
            "FailureReason": null
          },
          "PSRemoteUsers": {
            "Results": [],
            "Collected": false,
            "FailureReason": null
          }
        }
      ]
    }
    """

  data = json.loads(missing_properties)
  a1 = data["data"][0]["LocalAdmins"]
  a2 = data["data"][0]["RemoteDesktopUsers"]
  a3 = data["data"][0]["DcomUsers"]
  a4 = data["data"][0]["PSRemoteUsers"]

  # computers.json file that produces the parsing error
  data = json.loads(old_file_data)
  for item in data["data"]:
      # add missing properties
      item["LocalAdmins"] = a1
      item["RemoteDesktopUsers"] = a2
      item["DcomUsers"] = a3
      item["PSRemoteUsers"] = a4
  json_object = json.dumps(data, indent=4)

  # write modified file into archive
  update_zip_file(inputfile, selected_file, json_object)
  print("Done.")

def main():
    if len(sys.argv) < 2:
        print("Usage: bloodhound-fix-computer 20230523133742_BloodHound.zip ...")
        print("Warning: the input file will be overwritten!")
    else:
        for zipfile in sys.argv[1:]:
            bloodhound_computer_fix(zipfile)

if __name__ == "__main__":
    main()
