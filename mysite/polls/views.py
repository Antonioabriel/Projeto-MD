import pandas as pd
import io, os
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from .process import tratar_csv,extrair_dados_pdf,gerar_cluster_excel,gerar_grafico_cor_raca,gerar_tabela_cor_forma_ingresso,gerar_grafico_forma_ingresso,tratar_Coluna,extrair_ano_nome
from openpyxl import Workbook
from io import BytesIO
from django.conf import settings


def index(request):
    form = UploadFileForm()
    return render(request, 'polls/index.html', {'form': form})

def selecionar_colunas(request):
    if request.method == 'POST':
        try:
            arquivos = request.FILES.getlist("arquivos")  # vários arquivos de uma vez
            print("Arquivos recebidos:", [a.name for a in arquivos])
            dfs_pdf = []
            df_superior = None
            anos = set()

            for arquivo in arquivos:
                nome = arquivo.name.lower()

                # pega ano pelo nome
                ano = extrair_ano_nome(arquivo.name)
                if ano:
                    anos.add(ano)

                if nome.endswith(".pdf"):
                    # Extrai dados dos PDFs
                    df_pdf = extrair_dados_pdf(arquivo)
                    df_pdf["numero_inscricao"] = df_pdf["numero_inscricao"].astype(str)
                    dfs_pdf.append(df_pdf)

                elif nome.endswith(".csv"):
                    # Lê o CSV (superior pesquisa)
                    try:
                        df_superior = pd.read_csv(io.TextIOWrapper(arquivo.file, encoding="utf-8"))
                    except UnicodeDecodeError:
                        arquivo.seek(0)
                        df_superior = pd.read_csv(io.TextIOWrapper(arquivo.file, encoding="latin1"))
                    df_superior["numero_inscricao"] = df_superior["numero_inscricao"].astype(str)

            # Junta todos os PDFs em um só
            df_cota = pd.concat(dfs_pdf, ignore_index=True) if dfs_pdf else pd.DataFrame()

            # Faz merge com o CSV
            if df_superior is not None and not df_cota.empty:
                df_temp = df_superior.merge(df_cota, on="numero_inscricao", how="left")
            else:
                df_temp = df_superior if df_superior is not None else df_cota

            # Pequeno pré-processamento de nomes de colunas (se tiver função sua)
            df_temp = tratar_Coluna(df_temp)
            print("Colunas do df_temp:", df_temp.columns.tolist())

            # Garante que a pasta temp exista
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)

            # Salva o DataFrame bruto temporário
            temp_path = os.path.join(temp_dir, 'df_bruto.csv')
            df_temp.to_csv(temp_path, index=False, encoding='utf-8')

            # Lista de colunas e anos
            colunas = df_temp.columns.tolist()
            anos_disponiveis = sorted(list(anos))

            return render(request, 'polls/index.html', {
                'colunas': colunas,
                'anos': anos_disponiveis
            })

        except Exception as e:
            return HttpResponse(f"Erro ao processar os arquivos: {str(e)}", status=400)

    return render(request, 'polls/index.html', {'form': UploadFileForm()})

def gerar(request):
    print("Método recebido:", request.method)
    print("Dados recebidos:", request.POST)  # DEBUG

    if request.method == 'POST':
        colunas_selecionadas = request.POST.getlist('colunas')  # colunas escolhidas pelo usuário
        Ano_do_processo = request.POST.getlist('anos')

        try:
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            df_bruto_path = os.path.join(temp_dir, 'df_bruto.csv')

            # Carrega o bruto
            df_bruto = pd.read_csv(df_bruto_path, encoding='latin1')

            # Aplica o tratamento usando só as colunas escolhidas
            resultado = tratar_csv(df_bruto, colunas_selecionadas,Ano_do_processo)

            # Salva o resultado tratado
            resultado_path = os.path.join(temp_dir, 'resultado.csv')
            resultado.to_csv(resultado_path, index=False, encoding='latin1')

            # Remove o bruto
            if os.path.exists(df_bruto_path):
                os.remove(df_bruto_path)

            # Retorna para download
            output = io.BytesIO()
            resultado.to_csv(output, index=False, encoding='latin1')
            output.seek(0)

            response = HttpResponse(
                output.getvalue(),
                content_type='text/csv; charset=latin1'
            )
            response['Content-Disposition'] = 'attachment; filename="resultado.csv"'
            return response


        except Exception as e:
            return HttpResponse(f"Erro ao processar os arquivos: {str(e)}", status=400)

    # se for GET, volta pro index
    return render(request, 'polls/index.html', {'form': UploadFileForm()})


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