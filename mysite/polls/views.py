import pandas as pd
import io, os
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from .process import tratar_csv,extrair_dados_pdf,gerar_cluster_excel,gerar_grafico_cor_raca,gerar_tabela_cor_forma_ingresso,gerar_grafico_forma_ingresso
from openpyxl import Workbook
from io import BytesIO
from django.conf import settings
import matplotlib.pyplot as plt

def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            cota_file = form.cleaned_data['cota']
            superior_file = form.cleaned_data['superior_pesquisa']
            

            try:
                # Trata os arquivos
                resultado = tratar_csv(cota_file, superior_file)

                # Garante que a pasta temp exista
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                os.makedirs(temp_dir, exist_ok=True)

                # Caminho onde será salvo o arquivo
                temp_path = os.path.join(temp_dir, 'resultado.csv')

                # Salva o DataFrame como CSV temporariamente
                resultado.to_csv(temp_path, index=False, encoding='latin1')

                # (Opcional) Salva o caminho na sessão para reutilizar depois
                request.session['caminho_csv_resultado'] = temp_path

                # Também retorna para download, se quiser manter essa funcionalidade
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


def gerar_grafico_view(request):
    caminho = os.path.join(settings.MEDIA_ROOT, 'temp', 'resultado.csv')

    if not os.path.exists(caminho):
        return HttpResponse("Arquivo não encontrado. Envie os dados primeiro.", status=404)

    df = pd.read_csv(caminho, encoding='latin1')

    acao = request.GET.get('grafico')  # Ex: ?grafico=cor_raca

    if acao == 'cor_raca':
        imagem_base64 = gerar_grafico_cor_raca(df)
        return render(request, 'polls/index.html', {'imagem': imagem_base64})

    elif acao == 'forma_ingresso':
        imagem_base64 = gerar_grafico_forma_ingresso(df)
        return render(request, 'polls/index.html', {'imagem': imagem_base64})

    elif acao == 'tabela_cor_ingresso':
        tabela_html = gerar_tabela_cor_forma_ingresso(df)
        return render(request, 'polls/index.html', {'tabela_html': tabela_html})

    else:
        return HttpResponse("Gráfico não reconhecido.", status=400)