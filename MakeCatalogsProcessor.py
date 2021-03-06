#!/usr/bin/python
#
# Copyright 2013 Greg Neagle
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""autopkg processor to run makecatalogs on a Munki repo"""

import os.path
import plistlib
import subprocess

from autopkglib import Processor, ProcessorError, get_pref

__all__ = ["MakeCatalogsProcessor"]

class MakeCatalogsProcessor(Processor):
    """Runs makecatalogs on a munki repo"""
    input_variables = {
        "munki_repo_path": {
            "required": True,
            "description": "Path to the munki repo.",
        },
        "force_rebuild": {
            "required": False,
            "description":
                "If not false or empty or undefined, force a makecatalogs run.",
        },
    }
    output_variables = {
        "makecatalogs_resultcode": {
            "description": "Result code from the makecatalogs operation.",
        },
        "makecatalogs_stderr": {
            "description": "Error output (if any) from makecatalogs.",
        },
    }

    description = __doc__

    def main(self):
        '''Rebuild Munki catalogs in repo_path'''

        cache_dir = get_pref("CACHE_DIR") or os.path.expanduser(
            "~/Library/AutoPkg/Cache")
        current_run_results_plist = os.path.join(
            cache_dir, "autopkg_results.plist")
        try:
            run_results = plistlib.readPlist(current_run_results_plist)
        except IOError:
            run_results = []

        something_imported = False
        # run_results is an array of autopackager.results,
        # which is itself an array.
        # look through all the results for evidence that
        # something was imported
        # this could probably be done as an array comprehension
        # but might be harder to grasp...
        for result in run_results:
            for item in result:
                if item.get("Processor") == "MunkiImporter":
                    if item["Output"].get("pkginfo_repo_path"):
                        something_imported = True
                        break

        if not something_imported and not self.env.get("force_rebuild"):
            self.output("No need to rebuild catalogs.")
            self.env["makecatalogs_resultcode"] = 0
            self.env["makecatalogs_stderr"] = ""
        else:
            # Generate arguments for makecatalogs.
            args = ["/usr/local/munki/makecatalogs",
                    self.env["munki_repo_path"]]

            # Call makecatalogs.
            try:
                proc = subprocess.Popen(
                    args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (_, err_out) = proc.communicate()
            except OSError as err:
                raise ProcessorError(
                    "makecatalog execution failed with error code %d: %s"
                    % (err.errno, err.strerror))

            self.env["makecatalogs_resultcode"] = proc.returncode
            self.env["makecatalogs_stderr"] = err_out
            if proc.returncode != 0:
                raise ProcessorError("makecatalogs failed: %s" % err_out)
            else:
                self.output("Munki catalogs rebuilt!")


if __name__ == "__main__":
    PROCESSOR = MakeCatalogsProcessor()
    PROCESSOR.execute_shell()
