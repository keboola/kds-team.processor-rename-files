import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from keboola.component import ComponentBase, UserException
from keboola.component.dao import FileDefinition, TableDefinition

KEY_REPLACEMENT = "replacement"

KEY_PATTERN = "pattern"
KEY_MODE = "mode"
KEY_TIMEZONE = "timezone"
KEY_FUNC_TO_UPPERCASE = "to_uppercase"

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [KEY_PATTERN]
REQUIRED_IMAGE_PARS = []


class Component(ComponentBase):
    def __init__(self):
        super().__init__(required_parameters=REQUIRED_PARAMETERS, required_image_parameters=REQUIRED_IMAGE_PARS)

    def run(self):
        """
        Main execution code
        """

        mode = self.configuration.parameters.get(KEY_MODE, "both")
        in_files: list[TableDefinition | FileDefinition] = []
        if mode == "files":
            in_files = self.get_input_files_definitions(only_latest_files=False)
        elif mode == "tables":
            in_files = self.get_input_tables_definitions()
        elif mode == "both":
            in_files.extend(self.get_input_tables_definitions())
            in_files.extend(self.get_input_files_definitions(only_latest_files=False))

        else:
            raise UserException(f'Invalid mode {mode}. Only "files" or "tables" or "all" modes are supported!')

        logging.info(f"Processing files in mode: {mode}")

        logging.info(f"{len(in_files)} input files found. Looking for matches and renaming.")
        renamed_files_count = 0
        for file in in_files:
            if self.rename_and_move(file):
                renamed_files_count += 1

        if len(in_files) > 0 and renamed_files_count == 0:
            logging.warning("No files were renamed. No files matched the pattern.")

        logging.info("Finished. ")

    def rename_and_move(self, in_file: FileDefinition | TableDefinition):
        file_name, has_changed = self.get_new_name(Path(in_file.full_path).name)
        if has_changed:
            logging.info(f'File "{in_file.full_path}" renamed to "{file_name}"')

        if isinstance(in_file, FileDefinition):
            new_out_file = self.create_out_file_definition(file_name)
        elif isinstance(in_file, TableDefinition):
            new_out_file = self.create_out_table_definition(file_name)
        else:
            raise ValueError("Invalid file definition object!")

        self.move_file_to_out(in_file, new_out_file)
        return has_changed

    def move_file_to_out(self, in_file: FileDefinition | TableDefinition, out_file: FileDefinition | TableDefinition):
        logging.debug(f'Moving file "{in_file.full_path}" to "{out_file.full_path}"')

        Path(out_file.full_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(in_file.full_path, out_file.full_path)

        manifest_path = Path(f"{in_file.full_path}.manifest")
        skip_manifest = self.configuration.parameters.get("skip_manifest")

        if manifest_path.exists() and not skip_manifest:
            if isinstance(in_file, TableDefinition):
                # This is less destructive than recreating whole TableDefinition
                in_file._name = out_file.name
                in_file.full_path = out_file.full_path
                self.write_manifest(in_file)
            else:
                shutil.copy(manifest_path, f"{out_file.full_path}.manifest")

    def get_new_name(self, file_name: str) -> tuple[str, bool]:
        params = self.configuration.parameters
        has_changed = True

        matches = re.findall(params[KEY_PATTERN], file_name)

        if not matches:
            return file_name, False

        replacement_string = params[KEY_REPLACEMENT]

        # replace context variables
        replacement_string = self._replace_context_functions(replacement_string)

        group_positions = re.findall(r"(\$\d+)", replacement_string)
        if group_positions:
            new_file_name = self._replace_match_groups(replacement_string, group_positions, matches)
        else:
            # replace patterns
            new_file_name = re.sub(params[KEY_PATTERN], replacement_string, file_name)

        if not new_file_name:
            has_changed = False
            new_file_name = file_name

        to_uppercase = params.get("to_uppercase", False)
        if to_uppercase:
            name, ext = os.path.splitext(new_file_name)
            new_file_name = name.upper() + ext

        add_timestamp = params.get("add_timestamp", False)
        if add_timestamp:
            timestamp = datetime.now(self._get_timezone()).strftime("%Y%m%d%H%M%S")
            name, ext = os.path.splitext(new_file_name)
            new_file_name = f"{name}_{timestamp}{ext}"

        return new_file_name, has_changed

    def _replace_context_functions(self, replacement_string: str) -> str:
        if "{" not in replacement_string:
            return replacement_string

        return replacement_string.format(**self._available_contexts_functions())

    def _get_timezone(self) -> ZoneInfo | None:
        tz_name = self.configuration.parameters.get(KEY_TIMEZONE)
        if not tz_name:
            return None
        try:
            return ZoneInfo(tz_name)
        except ZoneInfoNotFoundError as exc:
            raise UserException(
                f'Invalid timezone "{tz_name}". Use an IANA name such as "Europe/Prague" or "UTC".'
            ) from exc

    def _available_contexts_functions(self):
        now = datetime.now(self._get_timezone())
        return {
            "timestamp": now.strftime("%Y%m%d%H%M%S"),
            "date": now.strftime("%Y%m%d"),
            "time": now.strftime("%H%M%S"),
        }

    def _replace_match_groups(
        self, mask_string: str, mask_match_groups: list[str], filename_match_groups: list[str]
    ) -> str:
        # validate if all groups exists
        # look only at first match
        first_match = filename_match_groups[0]
        if isinstance(first_match, tuple):
            if any([int(group.replace("$", "")) > len(first_match) for group in mask_match_groups]):
                # not all groups are present
                return ""
            for group in mask_match_groups:
                mask_string = mask_string.replace(group, first_match[int(group.replace("$", ""))])
        else:
            mask_string = mask_string.replace("$0", first_match)

        return mask_string


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        comp.run()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
