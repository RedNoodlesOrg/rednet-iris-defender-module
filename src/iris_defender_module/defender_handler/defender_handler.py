#   -------------------------------------------------------------
#   Copyright (c) RedNoodles. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------

import hashlib
import shutil
import tempfile
import time
from pathlib import Path
from datetime import datetime

import iris_interface.IrisInterfaceStatus as InterfaceStatus


class SentinelHandler:
    def __init__(self, mod_config, server_config, evidence_storage, input_data, logger):
        self.mod_config = mod_config
        self.server_config = server_config
        self.sentinel = self.get_sentinel_instance()
        self.log = logger
        self.evidence_storage = evidence_storage

        self.user = input_data["user"]
        self.user_id = input_data["user_id"]
        self.case_name = input_data["case_name"]
        self.path = Path(input_data["path"])
        self.case_id = input_data["case_id"]
        self.is_update = input_data["is_update"]

    def get_sentinel_instance(self):
        """
        Returns an sentinel API instance depending if the key is premium or not

        :return: sentinel Instance
        """

        # TODO!
        # Here get your sentinel instance and return it
        # ex: return sentinelApi(url, key)
        return "<TODO>"

    def _ret_task_success(self, msg=""):
        """
        Return a task compatible success object to be passed to the next task
        :return:
        """
        return InterfaceStatus.I2Success(msg)

    def _ret_task_failure(self, msg=""):
        """
        Return a task compatible failure object to be passed to the next task
        :return:
        """
        return InterfaceStatus.I2Error(msg)

    def _is_file_registered(self, fhash):
        file_registered = self.evidence_storage.is_evidence_registered(sha256=fhash, case_id=self.case_id)
        return file_registered

    def _create_import_list(self, path=None):
        import_list = {}

        self.log.info("Checking input files")
        self.log.info(f"Path is {path}")

        if path.is_dir():
            for entry in path.iterdir():

                if not entry.is_dir():
                    # Compute file hash
                    # Compute SHA256 of file
                    sha256_hash = hashlib.sha256()

                    with open(entry, "rb") as f:
                        # Read and update hash string value in blocks of 4K
                        for byte_block in iter(lambda: f.read(4096), b""):
                            sha256_hash.update(byte_block)
                        fhash = sha256_hash.hexdigest()

                        file_registered = self._is_file_registered(fhash)

                        if not file_registered:

                            is_valid = True
                            # TODO!
                            # Here detect if the files are suited for this module (e.g EVTX files for EVTX module)
                            if entry.suffix == ".csv":

                                if "<TODO>" not in import_list:
                                    import_list["<TODO>"] = [entry]
                                else:
                                    import_list["<TODO>"].append(entry)

                            # elif... other file type

                            else:
                                is_valid = False

                            if not is_valid:
                                try:
                                    entry.unlink()
                                    self.log.debug(entry)
                                except Exception:
                                    pass
                                self.log.info("File has been deleted from the server")

                        else:
                            entry.unlink()
                            self.log.warning(f"{entry} was already imported")

            return import_list

        else:
            self.log.error("Internal error. Provided path is not a path")
            return None

    def _save_evidence(self, filepath: Path):
        # Compute SHA256 of file
        sha256_hash = hashlib.sha256()

        # Get file size
        fsize = filepath.stat().st_size

        with open(filepath, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            fhash = sha256_hash.hexdigest()

            file_registered = self._is_file_registered(fhash)

            if not file_registered:
                self.evidence_storage.add_evidence(
                    filename=filepath.name,
                    sha256=fhash,
                    date_added=datetime.now(),
                    case_id=self.case_id,
                    user_id=self.user_id,
                    size=fsize,
                    description=f"[Auto] file named {filepath.name}",
                )

    def _inner_import_files(self, import_list: list, data_type):
        """
        Method to be called as an entry point  import evidence
        :param data_type:
        :param import_list:
        :return: True if imported, false if not + list of errors
        """

        self.log.info(f"New imports for {self.case_name} on behalf of {self.user}")
        self.log.info(f"{len(import_list)} files of type {data_type} to import")

        self.log.info("Starting processing of files")

        in_path = import_list[0].parent

        out_path = in_path.parent / "out"

        if data_type == "<TODO>":

            start_time = time.time()

            # TODO!
            # Do your stuff here
            # Example :
            # self.sentinel.process_evidence(in_path, out_path)
            self.log.info("<TODO> sentinel import")
            ret_t = True

            end_time = time.time()

            self.log.info(f"Finished in {end_time - start_time}")

            if ret_t is False:
                return self._ret_task_failure("Error importing files.")

            for file in import_list:
                self._save_evidence(file)

            return self._ret_task_success("Files imported and saved")
        else:
            self.log.error("Unexpected file type, aborting...")
            return self._ret_task_failure()

    def import_evidence(self):
        """
        Check every uploaded files and dispatch to handlers
        :return:
        """
        # This is just an example on how to retrieve the files from IRIS and import/process them
        self.log.info(f"Received new sentinel import signal for {self.case_name}")

        temp_path = tempfile.TemporaryDirectory()
        shutil.move(str(self.path), temp_path.name)
        module_name = self.path.name
        self.path = Path(temp_path.name, module_name)

        import_list = self._create_import_list(path=self.path)

        ret = None
        if import_list:

            for data_type in import_list:

                ret_t = self._inner_import_files(import_list[data_type], data_type)

                # Merge the result with the current caller
                ret = InterfaceStatus.merge_status(ret, ret_t)

        else:

            self.log.error("Import list was empty. Please check previous errors.")
            self.log.error("Either internal error, either the files could not be uploaded successfully.")
            self.log.error("Nothing to import")
            ret = self._ret_task_failure("Import list empty")

        return ret
