# Copyright 2023, Your Name/Org, All rights reserved.

import subprocess
import os
import sys

from common import AppError, AppOneShotProcess


class ExecuteScriptError(AppError):
    """Exception for script execution errors."""
    pass


class ExecuteScriptProcess(AppOneShotProcess):
    """
    Process to execute a shell script with the downloaded path as an argument.
    """
    def __init__(self, script_path: str, file_path: str):
        super().__init__(name="ExecuteScript-" + os.path.basename(file_path))
        self.__script_path = script_path
        self.__file_path = file_path

    @property
    def script_path(self) -> str:
        return self.__script_path

    @property
    def file_path(self) -> str:
        return self.__file_path

    def _run(self):
        self.logger.info(f"Executing script '{self.__script_path}' for file '{self.__file_path}'")
        try:
            # Ensure the script is executable (especially on Linux/macOS)
            if sys.platform != 'win32':
                try:
                    os.chmod(self.__script_path, os.stat(self.__script_path).st_mode | 0o111) # Add execute permission
                except OSError as e:
                    self.logger.warning(f"Could not set execute permission on script '{self.__script_path}': {e}")
                    # Continue anyway, maybe it's already executable

            # Execute the script
            result = subprocess.run(
                [self.__script_path, self.__file_path],
                capture_output=True,
                text=True,
                check=False # Don't raise CalledProcessError automatically
            )

            # Log stdout/stderr
            if result.stdout:
                self.logger.info(f"Script stdout:\n{result.stdout.strip()}")
            if result.stderr:
                self.logger.warning(f"Script stderr:\n{result.stderr.strip()}")

            # Check return code
            if result.returncode != 0:
                raise ExecuteScriptError(f"Script '{self.__script_path}' exited with error code {result.returncode}")
            else:
                 self.logger.info(f"Script '{self.__script_path}' executed successfully for '{self.__file_path}'")

        except FileNotFoundError:
            raise ExecuteScriptError(f"Script file not found: {self.__script_path}")
        except Exception as e:
            # Catch other potential errors during execution
            raise ExecuteScriptError(f"Error executing script '{self.__script_path}': {e}") 