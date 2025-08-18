from django import forms

class UploadFileForm(forms.Form):
    cota = forms.FileField(label='Arquivo de cotas')
    cota2 = forms.FileField(label='Arquivo de cotas .2')
    superior_pesquisa = forms.FileField(label='Superior pesquisa')

