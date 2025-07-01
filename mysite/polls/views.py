import pandas as pd
import io
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from .process import tratar_csv,extrair_dados_pdf,gerar_cluster_excel
from openpyxl import Workbook
from io import BytesIO

def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            cota_file = form.cleaned_data['cota']
            superior_file = form.cleaned_data['superior_pesquisa']


            try:
                resultado = tratar_csv(
                    cota_file,
                    superior_file
                )

                output = io.StringIO()
                resultado.to_csv(output, index=False, encoding='latin1')
                output.seek(0)

                response = HttpResponse(output.getvalue().encode('latin1'), content_type='text/csv; charset=latin1')
                response['Content-Disposition'] = 'attachment; filename="resultado.csv"'
                return response

            except Exception as e:
                return HttpResponse(f"Erro ao processar os arquivos: {str(e)}", status=400)
    else:
        form = UploadFileForm()

    return render(request, 'polls/index.html', {'form': form})

def mesclar(request):
    return render(request, 'polls/mesclar.html')


def processar_mesclagem(request):
    if request.method == 'POST' and request.FILES.get('arquivo_mesclar'):
        arquivo = request.FILES['arquivo_mesclar']
        try:
            df = extrair_dados_pdf(arquivo)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="resultado_pdf.csv"'
            df.to_csv(response, index=False)
            return response
        except Exception as e:
            return render(request, 'polls/mesclar.html', {'mensagem': f'Erro ao processar o PDF: {str(e)}'})
    return render(request, 'polls/mesclar.html')


def clusters_view(request):
    if request.method == 'POST' and request.FILES.get('arquivo_cluster'):
        arquivo = request.FILES['arquivo_cluster']
        try:
            try:
                df = pd.read_csv(io.TextIOWrapper(arquivo, encoding='utf-8'))
            except UnicodeDecodeError:
                arquivo.seek(0)
                df = pd.read_csv(io.TextIOWrapper(arquivo, encoding='latin1'))


            # Aqui você já deve ter a coluna 'cluster' no DataFrame.
            # Se não tiver, adicione sua lógica de clusterização antes.

            df_resultado = gerar_cluster_excel(df)

            # Gerar Excel


            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_resultado.to_excel(writer, index=False, sheet_name='Clusters')

            output.seek(0)
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="clusters.xlsx"'
            return response

        except Exception as e:
            return render(request, 'polls/clusters.html', {'mensagem': f'Erro: {str(e)}'})

    return render(request, 'polls/clusters.html')
