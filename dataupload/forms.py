from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            allowed_types = ['application/json', 'text/csv']
            if file.content_type not in allowed_types:
                raise forms.ValidationError("Unsupported file type. Only JSON and CSV files are allowed.")
        return file

