import csv
import json
from abc import ABC, abstractmethod
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from .forms import UploadFileForm
from .models import FileUpload, DataRecord

# Strategy Interface
class FileParser(ABC):
    """
    Abstract base class for file parsers.
    Defines the interface for parsing files.
    """
    @abstractmethod
    def parse(self, file):
        """
        Parse the given file.

        :param file: The file to be parsed.
        :return: Parsed data.
        """
        pass

# Concrete Strategy for CSV
class CSVFileParser(FileParser):
    """
    Concrete implementation of FileParser for parsing CSV files.
    """
    def parse(self, file):
        """
        Parse the given CSV file.

        :param file: The CSV file to be parsed.
        :return: List of dictionaries representing the CSV data.
        """
        data = []
        reader = csv.DictReader(file.read().decode('utf-8').splitlines())
        for row in reader:
            data.append(row)
        return data

# Concrete Strategy for JSON
class JSONFileParser(FileParser):
    """
    Concrete implementation of FileParser for parsing JSON files.
    """
    def parse(self, file):
        """
        Parse the given JSON file.

        :param file: The JSON file to be parsed.
        :return: Parsed JSON data.
        """
        return json.load(file)

# Factory Class
class FileParserFactory:
    """
    Factory class for creating file parsers based on file extension.
    """
    @staticmethod
    def get_parser(file_name):
        """
        Get the appropriate file parser based on the file extension.

        :param file_name: The name of the file.
        :return: Tuple containing the file parser instance and the file type.
        :raises ValueError: If the file type is unsupported.
        """
        if file_name.endswith('.csv'):
            return CSVFileParser(), 'csv'
        elif file_name.endswith('.json'):
            return JSONFileParser(), 'json'
        else:
            raise ValueError("Unsupported file type")

# Upload File Handler
def upload_file(request):
    """
    Handle file upload requests.

    :param request: The HTTP request object.
    :return: JsonResponse indicating success or failure of the upload.
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                parser, file_type = FileParserFactory.get_parser(file.name)
                data = parser.parse(file)
                file_upload = FileUpload.objects.create(file=file)
                for record in data:
                    DataRecord.objects.create(file_upload=file_upload, data=record, type=file_type)
                return JsonResponse({'message': 'File uploaded successfully'})
            except ValueError as e:
                return HttpResponseBadRequest(str(e))
            except Exception as e:
                return JsonResponse({'error': 'An unexpected error occurred: ' + str(e)}, status=500)
        else:
            return HttpResponseBadRequest('Unsupported file type')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

# Query Data Handler
def query_data(request):
    """
    Handle requests to query data records.

    :param request: The HTTP request object.
    :return: JsonResponse containing the requested data records.
    """
    data_type = request.GET.get('type', None)
    if data_type:
        records = DataRecord.objects.filter(type=data_type).values()
    else:
        records = DataRecord.objects.all().values()
    return JsonResponse(list(records), safe=False)
