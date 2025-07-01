from django import forms

class UploadFileForm(forms.Form):
    cota = forms.FileField(label='Arquivo de cotas')
    superior_pesquisa = forms.FileField(label='Superior pesquisa')

