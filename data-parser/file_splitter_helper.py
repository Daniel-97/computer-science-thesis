from pathlib import Path

class FileSplitterHelper:

    def __init__(self, file_prefix: str, output_folder: str, max_file_size_mb: int):
        self.file_prefix = file_prefix
        self.output_folder = output_folder
        self.max_file_size = max_file_size_mb * 1000000
        self.file_number = 0
        self.file_size = 0

        Path(output_folder).mkdir(parents=True, exist_ok=True)

    def _start_new_file(self):
        self.file_number += 1
        with open(self._get_file_name(), 'w') as f:
            f.write('[')
            f.close()
        self.file_size = 1

    def append(self, element: str):

        # If the actual file is bigger than the max file size, start a new one and close the old one
        if self.file_size + len(element) > self.max_file_size or self.file_size == 0:
            if self.file_size > 0:
                self._end_file()
            self._start_new_file()

        with open(self._get_file_name(), 'a') as f:
            f.write((',\n' if self.file_size > 1 else '') + element)
            f.close()

        # Update the file size
        self.file_size = self.file_size + len(element)
        
    def _end_file(self):
        with open(self._get_file_name(), 'a') as f:
            f.write('\n]')
            f.close()

    def _get_file_name(self):
        return f'{self.output_folder}/{self.file_prefix}-chunk-{self.file_number}.json'