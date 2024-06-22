import csv
import json
import logging
from abc import ABC, abstractmethod
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from .forms import UploadFileForm
from .models import FileUpload, DataRecord

# Get an instance of a logger for the 'dataupload' application
logger = logging.getLogger('dataupload')

# FileParser to parse different kind of files
class FileParser(ABC):
    @abstractmethod
    def parse(self, file):
        pass

# Concrete Strategy for CSV
class CSVFileParser(FileParser):
    def parse(self, file):
        data = []
        reader = csv.DictReader(file.read().decode('utf-8').splitlines())
        for row in reader:
            data.append(row)
        return data

# Concrete Strategy for JSON
class JSONFileParser(FileParser):
    def parse(self, file):
        return json.load(file)

# Factory Class
class FileParserFactory:
    @staticmethod
    def get_parser(file_name):
        if file_name.endswith('.csv'):
            return CSVFileParser(), 'csv'
        elif file_name.endswith('.json'):
            return JSONFileParser(), 'json'
        else:
            raise ValueError("Unsupported file type")

# Upload the File and save the data into postgres DB
def upload_file(request):
    """
    Handle file upload requests.

    :param request: The HTTP request object.
    :return: JsonResponse indicating success or failure of the upload.
    """
    message = None  # Initialize the message variable
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
                message = 'File uploaded successfully'
                logger.info(f"File '{file.name}' uploaded and processed successfully.")
            except ValueError as e:
                message = str(e)
                logger.error(f"File upload failed due to unsupported file type: {str(e)}")
            except Exception as e:
                message = 'An unexpected error occurred: ' + str(e)
                logger.exception(f"An unexpected error occurred during file upload: {str(e)}")
        else:
            message = 'Unsupported file type'
            logger.warning("File upload failed due to invalid form submission.")
        return render(request, 'upload.html', {'form': form, 'message': message})
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form, 'message': message})

# handle the query from user input based on type json or csv return the stored values
def query_data(request):
    data_type = request.GET.get('type', None)
    if data_type:
        records = DataRecord.objects.filter(type=data_type).values()
        logger.info(f"Querying data records of type '{data_type}'.")
    else:
        records = DataRecord.objects.all().values()
        logger.info("Querying all data records.")
    return JsonResponse(list(records), safe=False)
