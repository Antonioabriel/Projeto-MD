import pandas as pd
import io, os, re, json,shutil
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from .process import calcular_metricas_clusters, exportar_clusters_excel, gerar_clusters, tratar_csv,extrair_dados_pdf,gerar_grafico_cor_raca,gerar_tabela_cor_forma_ingresso,gerar_grafico_forma_ingresso,tratar_Coluna,extrair_ano_nome
from io import BytesIO
from django.conf import settings
from django.utils import timezone



def index(request):
    form = UploadFileForm()
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    return render(request, 'polls/index.html', {'form': form})

def index_sem_limpar(request):
    form = UploadFileForm()
    return render(request, 'polls/index.html', {'form': form})

def upload_armazenar(request):
    if request.method != 'POST':
        return render(request, 'polls/index.html', {'form': UploadFileForm()})

    arquivos = request.FILES.getlist('arquivos')
    if not arquivos:
        return render(request, 'polls/index.html', {
            'form': UploadFileForm(),
            'mensagem': 'Nenhum arquivo enviado.'
        })

    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    meta_path = os.path.join(temp_dir, 'uploads_meta.json')
    meta = {'pdfs': [], 'csvs': [], 'outros': []}
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except Exception:
            pass  # se der erro, recomeça um novo meta

    salvos = []
    for arquivo in arquivos:
        original = arquivo.name
        base, ext = os.path.splitext(original)
        ext = ext.lower()

        safe_base = re.sub(r'[^A-Za-z0-9._-]+', '_', base)[:100]
        unique_name = f"{safe_base}__{timezone.now().strftime('%Y%m%d%H%M%S%f')}{ext}"
        dest_path = os.path.join(temp_dir, unique_name)

        with open(dest_path, 'wb+') as out:
            for chunk in arquivo.chunks():
                out.write(chunk)

        entry = {"nome_original": original, "arquivo": unique_name}

        if ext == '.pdf':
            # use sua função se preferir: ano = extrair_ano_nome(original)
            meta['pdfs'].append(entry)
        elif ext == '.csv':
            meta['csvs'].append(entry)
        else:
            meta['outros'].append(entry)

        salvos.append(entry)

    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("Arquivos armazenados:", [e['arquivo'] for e in salvos])  # debug no console

    return render(request, 'polls/index.html', {
        'form': UploadFileForm(),
        'mensagem': f'{len(salvos)} arquivo(s) armazenado(s) com sucesso.',
        'arquivos_salvos': salvos,   # opcional para listar no template
    })

def listar_colunas_anos(request):
    try:
        print("Entramos no Listar colunas ")
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        arquivos = os.listdir(temp_dir)  # pega tudo que já foi salvo
        print(f"[DEBUG] lidos {len(arquivos)} arquivos em {temp_dir}: {arquivos}")
        dfs_pdf = []
        df_superior = None
        anos = set()

        for nome_arquivo in arquivos:
            caminho = os.path.join(temp_dir, nome_arquivo)



            if nome_arquivo.lower().endswith(".pdf"):
                try:
                    ano = extrair_ano_nome(nome_arquivo)
                    if ano:
                        anos.add(ano)
                except Exception as e:
                    print(f"[DEBUG] extrair_ano_nome falhou para {nome_arquivo}: {e}")

                print(f"[DEBUG] LENDO PDF: {nome_arquivo}")
                # Extrai dados do PDF já salvo
                with open(caminho, "rb") as f:
                    df_pdf = extrair_dados_pdf(f)
                if df_pdf is None or df_pdf.empty:
                    print(f"[DEBUG] PDF vazio/None: {nome_arquivo}")
                    continue

                
                df_pdf["numero_inscricao"] = df_pdf["numero_inscricao"].astype(str)
                dfs_pdf.append(df_pdf)

            elif nome_arquivo.lower().endswith(".csv"):
                print(f"[DEBUG] LENDO CSV: {nome_arquivo}")
                # Lê o CSV
                try:
                    df_superior = pd.read_csv(caminho, encoding="utf-8")
                except UnicodeDecodeError:
                    df_superior = pd.read_csv(caminho, encoding="latin1")
                df_superior["numero_inscricao"] = df_superior["numero_inscricao"].astype(str)

        # Junta PDFs
        df_cota = pd.concat(dfs_pdf, ignore_index=True) if dfs_pdf else pd.DataFrame()

        # Merge com CSV
        if df_superior is not None and not df_cota.empty:
            df_temp = df_superior.merge(df_cota, on="numero_inscricao", how="left")
        else:
            df_temp = df_superior if df_superior is not None else df_cota

        # Tratamento das colunas
        df_temp = tratar_Coluna(df_temp)

        df_bruto_path = os.path.join(temp_dir, "df_bruto.csv")
        df_temp.to_csv(df_bruto_path, index=False, encoding="utf-8")
        print(f"[DEBUG] df_bruto salvo em {df_bruto_path} | shape={df_temp.shape}")

        # Colunas e anos disponíveis
        colunas = df_temp.columns.tolist()
        anos_disponiveis = sorted(list(anos))

        return render(request, "polls/analiseEstatistica.html", {
            "colunas": colunas,
            "anos": anos_disponiveis
        })

    except Exception as e:
        return HttpResponse(f"Erro ao listar colunas e anos: {str(e)}", status=400)

def gerar(request):
    if request.method == 'POST':
        colunas_selecionadas = request.POST.getlist('colunas')
        anos_selecionados = request.POST.getlist('anos')

        try:
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            df_bruto_path = os.path.join(temp_dir, 'df_bruto.csv')

            # Carrega o bruto
            df_bruto = pd.read_csv(df_bruto_path, encoding='latin1')

            # Aplica o tratamento
            resultado = tratar_csv(df_bruto, colunas_selecionadas, anos_selecionados)

            # Salva o resultado tratado
            resultado_path = os.path.join(temp_dir, 'resultado.csv')
            resultado.to_csv(resultado_path, index=False, encoding='latin1')

            # ⚠️ Não devolve download aqui, só confirma
            return render(request, 'polls/analiseEstatistica.html', {
                'mensagem': "Filtros aplicados com sucesso! Agora você pode baixar o CSV."
            })

        except Exception as e:
            return HttpResponse(f"Erro ao processar os arquivos: {str(e)}", status=400)

    return render(request, 'polls/index.html', {'form': UploadFileForm()})

def baixar_resultado(request):
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    resultado_path = os.path.join(temp_dir, 'resultado.csv')

    if not os.path.exists(resultado_path):
        return HttpResponse("Nenhum resultado encontrado. Gere o CSV primeiro.", status=404)

    with open(resultado_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='text/csv; charset=latin1')
        response['Content-Disposition'] = 'attachment; filename="resultado.csv"'
        return response

def analiseEstatistica(request):
    return render(request, 'polls/analiseEstatistica.html')

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
    temp_path = os.path.join(settings.MEDIA_ROOT, "temp", "resultado.csv")
    temp_cluster_path = os.path.join(settings.MEDIA_ROOT, "temp", "clusters_features.csv")

    if not os.path.exists(temp_path):
        return render(request, "polls/clusters.html", {"mensagem": "Nenhum dado encontrado. Gere o CSV primeiro."})

    df = pd.read_csv(temp_path, encoding="latin1")

    if request.method == "POST":
        try:
            n_clusters = int(request.POST.get("n_clusters", 3))
            colunas = request.POST.getlist("colunas")
            metodo_norm = request.POST.get("normalizacao", "soma")
            tratamento_nulos = request.POST.get("nulos", "drop")

            if colunas:
                df = df[colunas]

            # --- gera clusters ---
            df_clusterizado, inercia = gerar_clusters(df, n_clusters, metodo_norm, tratamento_nulos)

            # --- salva no temp ---
            df_clusterizado.to_csv(temp_cluster_path, index=False, encoding="latin1")

            return render(request, "polls/clusters.html", {
                "mensagem": f"Clusters gerados com sucesso! Inércia: {inercia:.2f}",
                "colunas": df.columns.tolist()
            })

        except Exception as e:
            return render(request, "polls/clusters.html", {"mensagem": f"Erro: {str(e)}"})

    return render(request, "polls/clusters.html", {"colunas": df.columns.tolist()})


def baixar_clusters_excel(request):
    temp_cluster_path = os.path.join(settings.MEDIA_ROOT, "temp", "clusters_features.csv")

    if not os.path.exists(temp_cluster_path):
        return HttpResponse("Nenhum cluster disponível. Gere os clusters primeiro.", status=404)

    df = pd.read_csv(temp_cluster_path, encoding="latin1")
    output = exportar_clusters_excel(df)

    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="clusters.xlsx"'
    return response


def analise_clusters(request):
    try:
        caminho = os.path.join(settings.MEDIA_ROOT, 'temp', 'clusters_features.csv')
        if not os.path.exists(caminho):
            return HttpResponse("Arquivo de features não encontrado. Execute a clusterização primeiro.", status=404)

        metricas, clusters = calcular_metricas_clusters(caminho)

        return render(request, "polls/analise_clusters.html", {
            "metricas": metricas,
            "clusters": clusters
        })

    except Exception as e:
        return HttpResponse(f"Erro na análise de clusters: {str(e)}", status=400)

def gerar_grafico_view(request):
    caminho = os.path.join(settings.MEDIA_ROOT, 'temp', 'resultado.csv')

    if not os.path.exists(caminho):
        return HttpResponse("Arquivo não encontrado. Envie os dados primeiro.", status=404)

    df = pd.read_csv(caminho, encoding='latin1')

    acao = request.GET.get('grafico')  # Ex: ?grafico=cor_raca

    if acao == 'cor_raca':
        imagem_base64 = gerar_grafico_cor_raca(df)
        return render(request, 'polls/analiseEstatistica.html', {'imagem': imagem_base64})

    elif acao == 'forma_ingresso':
        imagem_base64 = gerar_grafico_forma_ingresso(df)
        return render(request, 'polls/analiseEstatistica.html', {'imagem': imagem_base64})

    elif acao == 'tabela_cor_ingresso':
        tabela_html = gerar_tabela_cor_forma_ingresso(df)
        return render(request, 'polls/analiseEstatistica.html', {'tabela_html': tabela_html})

    else:
        return HttpResponse("Gráfico não reconhecido.", status=400)