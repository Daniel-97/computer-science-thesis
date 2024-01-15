from pathlib import Path

class FileSplitterHelper:

    def __init__(self, file_prefix: str, output_folder: str, max_file_size_mb: int):
        self.file_prefix = file_prefix
        self.output_folder = output_folder
        self.max_file_size = max_file_size_mb * 1000000
        self.file = None
        self.file_size = 0
        self.file_number = 0

        Path(output_folder).mkdir(parents=True, exist_ok=True)

    def _file_size(self):
        return self.file_size
    
    def _start_new_file(self):
        self.file_number += 1
        self.file = open(self._file_name(), 'w')
        self.file.write('[')
        self.file.close()
        
        self.file = open(self._file_name(), 'a') #open the file in append mode

    def append(self, element: str):

        # If the actual file is bigger than the max file size, start a new one and close the old one
        if (self._file_size() + len(element)) > self.max_file_size or self._file_size() == 0:
            if self.file_size > 0:
                self.end_file()
            self._start_new_file()

        self.file.write((',\n' if self.file_size > 1 else '') + element)

        # Update the file size
        self.file_size += len(element)
        
    def end_file(self):
        self.file.write('\n]')
        self.file.close()
        print(f'File {self._file_name()} saved! ({self._file_size()} byte)')
        self.file_size = 0

    def _file_name(self):
        return f'{self.output_folder}/{self.file_prefix}-chunk-{self.file_number}.json'