from pathlib import Path
import json
import csv
import io

class FileSplitterHelper:

    def __init__(self, file_prefix: str, output_folder: str, max_file_size_mb: int, file_format: str):
        self.file_prefix = file_prefix
        self.output_folder = output_folder + '/' + file_prefix
        self.max_file_size = max_file_size_mb * 1000000
        self.format = file_format
        self.file = None
        self.file_size = 0
        self.file_number = 0

        Path(self.output_folder).mkdir(parents=True, exist_ok=True)

    def _file_size(self):
        return self.file_size
    
    def _start_new_file(self):
        self.file_number += 1
        self.file = open(self._file_name(), 'w')
        self.file.close()
        
        self.file = open(self._file_name(), 'a') #open the file in append mode

    def append(self, element: dict):
        
        row = self._generate_row(element)

        # If the actual file is bigger than the max file size, start a new one and close the old one
        if (self.max_file_size > 0 and (self._file_size() + len(row)) > self.max_file_size) or self._file_size() == 0:
            if self.file_size > 0:
                self.end_file()
            self._start_new_file()

        bytes_wrote = self.file.write(row)

        # Update the file size
        self.file_size += bytes_wrote
    
    def _generate_row(self, element: dict):

        if_first_row = self.file_size == 0

        if self.format == "csv":
            csv_buffer = io.StringIO()
            csv_writer = csv.DictWriter(csv_buffer, element.keys(), extrasaction='ignore')

            if if_first_row:
                csv_writer.writeheader()

            # Flatten all array items
            for key in element:
                if type(element[key]) is list:
                    element[key] = ','.join(element[key]) 

            csv_writer.writerow(element)
            csv_string = csv_buffer.getvalue()
            csv_buffer.close()

            return csv_string
        
        elif self.format == "json":
            return ('[\n' if if_first_row else ',\n') + json.dumps(element)
        
        else:
            raise ValueError(f'Unsupported format ${self.format}')

    def end_file(self):
        if self.file is not None:

            if self.format == 'json':
                self.file.write('\n]')

            self.file.close()
            print(f'File {self._file_name()} saved! ({self._file_size()} byte)')
            self.file_size = 0

    def _file_name(self):
        return f'{self.output_folder}/{self.file_prefix}-{self.file_number}.{self.format}'