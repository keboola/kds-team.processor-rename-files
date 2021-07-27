import logging
import re
import shutil
from pathlib import Path
from typing import Tuple, List

from keboola.component.base import ComponentBase, UserException
# configuration variables
from keboola.component.dao import FileDefinition

KEY_REPLACEMENT = "replacement"

KEY_PATTERN = 'pattern'

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [KEY_PATTERN]
REQUIRED_IMAGE_PARS = []


class Component(ComponentBase):

    def __init__(self):
        super().__init__(required_parameters=REQUIRED_PARAMETERS,
                         required_image_parameters=REQUIRED_IMAGE_PARS)

    def run(self):
        '''
        Main execution code
        '''

        in_files = self.get_input_files_definitions(only_latest_files=False)
        logging.info(f"{len(in_files)} input files found. Looking for matches and renaming.")
        renamed_files_count = 0
        for file in in_files:
            if self.rename_and_move(file):
                renamed_files_count += 1

        if len(in_files) > 0 and renamed_files_count == 0:
            logging.warning("No files were renamed. No files matched the pattern.")

        logging.info(f'Finished. ')

    def rename_and_move(self, in_file: FileDefinition):
        params = self.configuration.parameters

        file_name, has_changed = self.get_new_name(in_file.full_name)
        if has_changed:
            logging.info(f'File "{in_file.full_path}" renamed to "{file_name}"')

        new_out_file = self.create_out_file_definition(file_name)

        self.move_file_to_out(in_file.full_path, new_out_file)
        return has_changed

    def move_file_to_out(self, source_path, file: FileDefinition):
        # move in_file to out
        shutil.copy(source_path, file.full_path)
        if Path(f'{source_path}.manifest').exists() and not self.configuration.parameters.get('skip_manifest', False):
            self.write_filedef_manifest(file)

    def get_new_name(self, file_name: str) -> Tuple[str, bool]:
        params = self.configuration.parameters
        has_changed = True

        matches = re.findall(params[KEY_PATTERN], file_name)

        if not matches:
            return file_name, False

        replacement_string = params[KEY_REPLACEMENT]
        group_positions = re.findall(r'(\$\d+)', replacement_string)
        if group_positions:
            new_file_name = self._replace_match_groups(replacement_string, group_positions, matches)
        else:
            # replace patterns
            new_file_name = re.sub(params[KEY_PATTERN], replacement_string, file_name)

        if not new_file_name:
            has_changed = False
            new_file_name = file_name

        return new_file_name, has_changed

    def _replace_match_groups(self, mask_string: str, mask_match_groups: List[str],
                              filename_match_groups: List[str]) -> str:

        # validate if all groups exists
        # look only at first match
        first_match = filename_match_groups[0]
        if isinstance(first_match, tuple):
            if any([int(group.replace('$', '')) > len(first_match) for group in mask_match_groups]):
                # not all groups are present
                return ''
            for group in mask_match_groups:
                mask_string = mask_string.replace(group, first_match[int(group.replace('$', ''))])
        else:
            mask_string.replace('$1', first_match)

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
