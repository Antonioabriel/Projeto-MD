import pandas as pd
import io
import fitz  # PyMuPDF
import re
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import base64


def tratar_csv(superior_pesquisa_file,colunas_selecionadas,Ano_do_processo):
    def read_csv(file):
        file.seek(0)
        try:
            return pd.read_csv(io.TextIOWrapper(file, encoding='utf-8'))
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(io.TextIOWrapper(file, encoding='latin1'))

    
    # Ainda é CSV
    df_1 = superior_pesquisa_file


    # Garante que a coluna e os anos sejam do mesmo tipo (string)
    df_1 = df_1.dropna(subset=["ano_do_processo"])
    df_1["ano_do_processo"] = df_1["ano_do_processo"].astype(int).astype(str)
    
    Ano_do_processo = [str(ano) for ano in Ano_do_processo]
    print(Ano_do_processo)
    print(df_1["ano_do_processo"])
    df_1 = df_1[df_1["ano_do_processo"].isin(Ano_do_processo)]

 
    print(df_1.columns.tolist())
    # Padronizando o nome do arquivo classificados e Cota
    df_1.rename(columns={'Número de Inscrição': 'numero_inscricao'}, inplace=True)
    
    print("df_1:")
    print(df_1['numero_inscricao'].dtype)
    print(df_1['numero_inscricao'].head())

    
    # Retirando as escrições dublicadas
    df_1 = df_1.drop_duplicates(subset=['numero_inscricao'], keep=False)

    
    # Garantir que a coluna 'numero_inscricao' é do mesmo tipo
    df_1['numero_inscricao'] = df_1['numero_inscricao'].astype(str)

    # Passando as colunas Forma de Ingresso para base do Superior tendo o número de inscrição como parametro
    print(df_1['Forma de Ingresso'].unique())
 


    # Verificar se o candidato tem uma inscrição duplicada
    df_1['duplicado'] = df_1.duplicated(subset=['nome_candidato'], keep=False)

    # Remover a coluna 'nome_social_candidato' se não for necessária
    df_1.drop(['nome_social_candidato'], axis=1, inplace=True)

    df_1 = df_1.astype({'processo_seletivo': 'string'})
    df_1['data_nascimento_candidato'] = pd.to_datetime(df_1['data_nascimento_candidato'], errors='coerce')

    

    #adicionar string vazia para os valores de renda mensal não informadas
    df_1['renda_mensal_familia'].fillna(False)

    # Corrigir textos com erros de digitação
    df_1['renda_mensal_familia'].replace({
        "Entre meio salário mínimo e uma salário mínimo e meio": "Entre meio salário mínimo e um salário mínimo e meio",
        "Entre um salário mínimo e um salário mínimos e meio": "Entre um salário mínimo e um salário mínimo e meio"
    }, inplace=True)

    # Padronizar faixas de renda com intervalos
    df_1['renda_mensal_familia'].replace({
        "Até meio salário mínimo": "x < 1,5",
        "Entre meio salário mínimo e um salário mínimo": "x < 1,5",
        "Entre meio salário mínimo e um salário mínimo e meio": "x < 1,5",
        "Entre um salário mínimo e um salário mínimo e meio": "x < 1,5",
        "1 < x < 1,5": "x < 1,5",
        "0,5 < x < 1": "x < 1,5",
        "1,5 < x < 2,5": "1,5 < x < 2,5",
        "Entre um salário mínimo e meio e dois salários mínimos e meio": "1,5 < x < 2,5",
        "Entre dois salários mínimos e meio e três salários mínimos e meio": "x > 2,5",
        "Entre dois salários mínimos e meio e três salários mínimos": "x > 2,5",
        "Acima de três salários mínimos e meio": "x > 2,5",
        "Acima de três salários mínimos": "x > 2,5",
        "2,5 < x < 3": "x > 2,5",
        "2,5 < x < 3,5": "x > 2,5",
        "x > 3,5": "x > 2,5",
        "x > 3": "x > 2,5"
    }, inplace=True)

    #Adicionar valor False a linhas vazias na coluna curso
    df_1['nome_curso'].fillna(False)



    # Combinar as diferentes entradas para CAMPOS DOS GOYTACAZES. Atualizar todas as entradas para caixa alta.
    df_1.loc[df_1['cidade_candidato'].str.contains("Campos dos Goytacazes| CAMPOS DOS GOYTACAZES|CAMPOS DOS GOYTACAZES  |CAMPOS DOS GOYTACAZES- RJ|CAMPOS DOS GOYTACAZESALAIR|CAMPOS DOS GOYTACAZES - RJ|DORES DE MACABU ( CAMPOS DOS GOYTACAZES )|SANTA MARIA DE CAMPOS DOS GOYTACAZES|campos dos goytacazes-rj|CAMPOS DOS GOYTACAZES'|CAMPOS DOS GOYTACAZES]|GOITACAZES (CAMPOS DOS GOYTACAZES)|CAMPOS DOS GOYTACAZES L|GOITACAZES (CAMPOS DOS GOYTACAZES)|campos dos goytacazes.|CAMPOS DOS GOYTACAZES- RJ|DORES DE MACABU ( CAMPOS DOS GOYTACAZES )|SANTA MARIA DE CAMPOS DOS GOYTACAZES|campos dos goytacazes-rj|CAMPOS DOS GOYTACAZES'|CAMPOS DOS GOYTACAZES]|GOITACAZES (CAMPOS DOS GOYTACAZES)|CAMPOS DOS GOYTACAZES L|GOITACAZES (CAMPOS DOS GOYTACAZES)|campos dos goytacazes.|CAMPOS DOS GOYTACAZES- RJ|Campos dos Goytacazes, Rio de Janeiro, Brasil|CAMPOS DOS GOYTCAZES|SANTO EDUARDO (CAMPOS DOS GOYTACAZES)|Campos dos Goytacazesr|GOITACAZES (CAMPOS DOS GOYTACAZES)|Campos dos Goytacazes, Rio de Janeiro, Brasil|GOITACAZES (CAMPOS DOS GOYTACAZES)|campos dos goytacazes- RJ|Campos dos Goytacazes, Rio de Janeiro, Brasil|CAMPOS DOS GOYTACAZES]|CAMPOS DOS GOYTACAZES//GUARUS|Campos dos Goytacazesr|GOITACAZES (CAMPOS DOS GOYTACAZES)|campos dos goytacazes- RJ|CAMPOS DOS GOYTACAZESR|CAMPOS DOS GOYTACAZES/RJ|SANTO AMARO DE CAMPOS (CAMPOS DOS GOYTACAZES)|CAMPOS DOS GOYTACAZES/RJ| CAMPOS|CAMPOS DOS GOYTACAZES RJ| CAMPOS DOS GOITACAZES|GOYTACAZES|Goytacazes|goytacazes|Goitacazes|Campos dos|GOYTACAZ|campos dos|CAMPOS.RJ|CAMPOS", case=False, na=False), 'cidade_candidato'] = "CAMPOS DOS GOYTACAZES"
    df_1['cidade_candidato'] = df_1['cidade_candidato'].str.upper()

    #Criar uma coluna para armazenar se o ingressante mora em Campos ou não
    df_1['morador_de_campos'] = df_1['cidade_candidato'].str.contains('CAMPOS DOS GOYTACAZES', case=False, na=False).map({True: 'mora_em_campos', False: 'nao_mora_em_campos'})

    # Criar a coluna com base na presença de padrões indicativos de escola pública
    padrao_publica = r'Federal|Instituto Federal|Estadual|Estatal|Municipal|CIEP|Brizolão|IFF|IFFluminense|CEFET|E\.M\.|EM|EE|E\.E\.|C\.E|Liceu|Otaviano|Nilo'

    df_1['escola_publica'] = df_1['colegio_fundamental'].str.contains(padrao_publica, case=False, na=False)\
                                    .map({True: 'publica', False: 'privada'})

    print(df_1['Forma de Ingresso'].unique())

    print("Iniciando substituição de caracteres especiais...")
    print("Colunas do tipo object:", df_1.select_dtypes(include='object').columns.tolist())
  # Substituições de acentos e caracteres especiais
    substituicoes = {
        'Ã': 'A', 'Á': 'A', 'Â': 'A', 'Ó': 'O', 'Í': 'I', 'í': 'i',
        'º': '', 'ª': '', '\.': '', '–': '', '´': '', '`': '', '^': '', '"': '',
        'ó': 'o', 'ô': 'o', 'Ô': 'O', 'á': 'a', 'â': 'a', 'ç': 'c',
        'ã': 'a', 'é': 'e', 'ê': 'e', 'à': 'a', 'ú': 'u', 'Ú': 'U'
    }

    for col in df_1.select_dtypes(include='object').columns:
        try:
            df_1[col] = df_1[col].astype(str).replace(substituicoes, regex=True)
        except Exception as e:
            print(f"Erro na coluna '{col}': {e}")

    # Remover qualquer texto entre parênteses (com parênteses)
    df_1.replace(r"\([^()]*\)", "", regex=True, inplace=True)

    # Remover aspas simples da coluna 'cidade_candidato' e de todo o DataFrame
    df_1['cidade_candidato'] = df_1['cidade_candidato'].astype(str).str.replace("'", "", regex=False)
    df_1.replace("'", "", regex=True, inplace=True)

    df_1.drop(['colegio_fundamental'], axis=1, inplace=True)


    
    df_1['cor_ou_raca'] = df_1['cor_ou_raca'].replace({
        'Branco': 'Branco',
        'Pardo': 'Pardo',
        'Amarela': 'Pardo',
        'Indigena': 'Pardo',
        'Preto': 'Negro',
        'Negro': 'Negro',

    })

    df_1['atividade_remunerada'] = df_1['atividade_remunerada'].replace({
        'Sim, em tempo parcial (cerca de 20 horas semanais)': 'Sim, em tempo integral (cerca de 30 horas semanais)',

    })


    #Excluindo colunas que não seram usadas
    #df_1.drop(columns=[
    #'numero_inscricao', 'ano_do_processo', 'motivo_escolha_curso', 'nome_candidato',
    #'data_nascimento_candidato', 'ano', 'idade', 'processo_seletivo', 'declarado_pcd',
    #'requerimento_concorrencia_cota_pcd', 'deferimento_concorrencia_cota_pcd', 'inscricao_isenta',
    #'negro_pardo_indigena', 'fontes_iff', 'regiao_oportunidades', 'costume_computador',
    #'duplicado','morador_de_campos','cor_ou_raca'
    #], inplace=True)


    #Exclindo curso da pós graduação
    cursos_para_excluir = ['Mestrado Profissional em Ensino e suas Tecnologias',
    'Mestrado em Engenharia Ambiental', 'Mestrado em Sistemas Aplicados a Engenharia e Gestao',
    'Docencia no Seculo XXI: Educacao e Tecnologias Digitais','Gestao, Design e Marketing','Manutencao Industrial']

    # Filtrar o DataFrame para excluir linhas com esses cursos
    df_1 = df_1[~df_1['nome_curso'].isin(cursos_para_excluir)]

    df_1.drop(['nome_curso'],axis=1, inplace=True)
    # Remove espaços
    df_1['Forma de Ingresso'] = df_1['Forma de Ingresso'].astype(str).str.strip()

    # Converte strings "nan" (texto) para NaN reais
    df_1['Forma de Ingresso'].replace(['', 'nan', 'NaN', 'None'], pd.NA, inplace=True)

    # Remove linhas com NaN
    df_1.dropna(subset=['Forma de Ingresso'], inplace=True)

    df_1 = df_1[colunas_selecionadas]
        

    return df_1



def extrair_dados_pdf(arquivo_pdf):
    doc = fitz.open(stream=arquivo_pdf.read(), filetype="pdf")
    dados = []
    curso = ""
    tipo_vaga = ""

    for pagina in doc:
        texto = pagina.get_text()
        linhas = texto.split("\n")

        i = 0
        while i < len(linhas):
            linha = linhas[i].strip()

            # Detecta curso e tipo de vaga
            if " - Ampla Concorrência" in linha or " - Cota" in linha:
                partes = linha.rsplit(" - ", 1)
                curso = partes[0].strip()
                tipo_vaga = partes[1].strip()
                i += 1
                continue

            # Detecta padrão de candidato: 5 linhas seguidas
            if re.match(r"\d+º", linha) and i + 4 < len(linhas):
                inscricao = linhas[i + 1].strip()
                # nome = linhas[i + 2].strip()  # ignorado
                nota = linhas[i + 3].strip().replace(",", ".")
                situacao = linhas[i + 4].strip()

                dados.append([curso, tipo_vaga, inscricao, nota, situacao])
                i += 5
            else:
                i += 1

    df = pd.DataFrame(dados, columns=['nome_curso_FI', 'Forma de Ingresso', 'numero_inscricao', 'Nota', 'Situação'])
    df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce')
    return df



def gerar_cluster_excel(df_1):
    # Converte booleanos em inteiros
    for col in df_1.columns:
        if df_1[col].dtype == 'bool':
            df_1[col] = df_1[col].astype(int)

    # Codifica variáveis categóricas
    df_d = pd.get_dummies(df_1, columns=df_1.select_dtypes(include=['object', 'category']).columns)

    # Remove colunas com soma zero (vazias)
    df_d = df_d.loc[:, df_d.sum(axis=0) != 0]

    # Normaliza
    X = df_d.div(df_d.sum(axis=1), axis='rows')
    
    # Remove linhas com NaN
    X = X.dropna()
    df_1 = df_1.loc[X.index].copy()

    # Clusterização
    km = KMeans(n_clusters=3, max_iter=10000, n_init=100, random_state=61658)
    X_T = km.fit_predict(X)

    # Adiciona os clusters aos DataFrames
    df_1['cluster'] = X_T
    df_d['cluster'] = X_T

    # Análise dos clusters
    linhas = []
    for col in df_1.drop('cluster', axis=1).columns:
        for cl in np.sort(df_1['cluster'].unique()):
            if df_1[col].dtype == object:
                vc = 100 * df_1[df_1.cluster == cl][col].value_counts() / (df_1.cluster == cl).sum()
                for cat, cnt in vc.reset_index().values:
                    linhas.append([cl, f"{col}_{cat}", f"{cnt:.2f}%"])
            else:
                media = df_1[df_1.cluster == cl][col].mean()
                linhas.append([cl, col, f"{media:.2f}"])

    # Totais gerais
    for col in df_1.drop('cluster', axis=1).columns:
        if df_1[col].dtype == object:
            vc = 100 * df_1[col].value_counts() / df_1.shape[0]
            for cat, cnt in vc.reset_index().values:
                linhas.append(['All', f"{col}_{cat}", f"{cnt:.2f}%"])
        else:
            media = df_1[col].mean()
            linhas.append(['All', col, f"{media:.2f}"])

    return pd.DataFrame(linhas, columns=['cluster', 'variavel', 'valor'])



def gerar_grafico_cor_raca(df):
    counts = df['cor_ou_raca'].value_counts()

    def autopct_generator(limit):
        def inner_autopct(pct):
            return ('%1.1f%%' % pct) if pct > limit else ''
        return inner_autopct

    limite_pct = 1
    porcentagens = counts / counts.sum() * 100
    legendas_filtradas = porcentagens[porcentagens > limite_pct].index

    fig, ax = plt.subplots(figsize=(10, 7))
    counts.plot(
        kind='pie',
        autopct=autopct_generator(limite_pct),
        labels=None,
        ax=ax
    )
    ax.set_title('Distribuição por Cor ou Raça')
    ax.set_ylabel('')
    ax.legend(
        labels=legendas_filtradas,
        title="Cor ou Raça",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )
    plt.tight_layout()

    return _fig_para_base64(fig)


def gerar_grafico_forma_ingresso(df):
    counts = df['Forma de Ingresso'].value_counts()

    fig, ax = plt.subplots(figsize=(10, 7))
    counts.plot(
        kind='pie',
        autopct='%1.1f%%',
        labels=None,
        ax=ax
    )
    ax.set_title('Distribuição Forma de Ingresso')
    ax.set_ylabel('')
    ax.legend(
        labels=counts.index,
        title="Legenda",
        bbox_to_anchor=(1.02, 0.6)
    )
    plt.tight_layout()

    return _fig_para_base64(fig)


def gerar_tabela_cor_forma_ingresso(df):
    tabela = pd.crosstab(df['cor_ou_raca'], df['Forma de Ingresso'], normalize=True)
    tabela = tabela * 100
    tabela_formatada = tabela.style.format("{:.1f}%")
    return tabela_formatada.to_html()


def _fig_para_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    imagem_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return imagem_base64


def tratar_Coluna(df_temp):
    
    df_1 = df_temp
# Renomear colunas para remover números dos nomes
    df_1.rename(columns={
        "1_estado_civil": "estado_civil",
        "2_cor_ou_raca": "cor_ou_raca",
        "3_periodo_fundamental": "periodo_fundamental",
        "4_colegio_fundamental": "colegio_fundamental",
        "4_situacao_superior": "situacao_superior",
        "5_motivo_escolha_curso": "motivo_escolha_curso",
        "6_fontes_iff": "fontes_iff",
        "7_atividade_remunerada": "atividade_remunerada",
        "8_renda_mensal_familia": "renda_mensal_familia",
        "9_participacao_economia_familia": "participacao_economia_familia",
        "10_costume_computador": "costume_computador",
        "11_regiao_oportunidades": "regiao_oportunidades"
    }, inplace=True)

        #Criar uma coluna para armazenar a idade do canditado no ano que a inscrição foi realizada
    df_1['idade'] = None

    #Extraindo e tratando o ano de nascimento dos alunos
    df_1['data_nascimento_candidato'] = df_1['data_nascimento_candidato'].fillna(pd.NaT)
    df_1 = df_1[(df_1['data_nascimento_candidato'] != '-') & (df_1['data_nascimento_candidato'] != '#N/D')]
    df_1['data_nascimento_candidato'] = pd.to_datetime(df_1['data_nascimento_candidato'], errors='coerce')
    df_1 = df_1.dropna(subset=['data_nascimento_candidato'])
    ano_aluno = pd.DatetimeIndex(df_1['data_nascimento_candidato'])
    df_1['ano'] = ano_aluno.year

    #Extraindo o ano do processo seletivo
    import re
    def extrair_ano_processo(frase):
        ano = re.search(r'\b\d{4}\b', frase)
        if ano:
            return int(ano.group())  # Retorna o ano encontrado como um inteiro
        else:
            return None  # Retorna None se nenhum ano for encontrado


    df_1['ano_do_processo'] = df_1['processo_seletivo'].apply(extrair_ano_processo)

        #Preenchendo a idade do aluno
    df_1['idade'] = df_1['ano_do_processo'] - df_1['ano']

    #df_1 = df_1[df_1['ano_do_processo'] == 2019]

    bins = [16, 20, 25, 30, 35, 40]
    labels = ['17-20', '21-25', '26-30', '31-35', '36-40']
    df_1['faixa_etaria'] = pd.cut(df_1['idade'], bins=bins, labels=labels, right=True)


        # Mapear cursos para suas grandes áreas
    mapeamentos = {
        'Arquitetura e Urbanismo': 'CIENCIAS SOCIAIS APLICADAS',
        'Biologia': 'CIENCIAS BIOLOGICAS',
        'Cidades e suas Tecnologias': 'CIENCIAS SOCIAIS APLICADAS',
        'Ciência e Tecnologia dos Alimentos': 'CIENCIAS AGRÁRIAS',
        'CIENCIAS da Natureza': 'CIENCIAS BIOLOGICAS',
        'Design Gráfico': 'CIENCIAS SOCIAIS APLICADAS',
        'Educação Básica e Saberes Pedagógicos na Contemporaneidade': 'CIENCIAS HUMANAS',
        'Educação, Ambiente e Sustentabilidade': 'CIENCIAS HUMANAS',
        'Educação Ambiental': 'CIENCIAS HUMANAS',
        'Educação Física': 'CIENCIAS DA SAUDE',
        'Engenharia Ambiental': 'ENGENHARIAS',
        'Engenharia Elétrica': 'ENGENHARIAS',
        'Engenharia de Computação': 'ENGENHARIAS',
        'Engenharia de Controle e Automação': 'ENGENHARIAS',
        'Engenharia Mecânica': 'ENGENHARIAS',
        'Física': 'CIENCIAS EXATAS E DA TERRA',
        'Gastronomia': 'CIENCIAS SOCIAIS APLICADAS',
        'Gestão, Design e Marketing': '',
        'Geografia': 'CIENCIAS HUMANAS',
        'História': 'CIENCIAS HUMANAS',
        'Hotelaria': 'CIENCIAS HUMANAS',
        'Letras - Português e Literaturas': 'LINGUISTICA, LETRAS E ARTES',
        'Literatura, Memória Cultural e Sociedade': 'LINGUISTICA, LETRAS E ARTES',
        'Manutenção Industrial': '',
        'Matemática': 'CIENCIAS EXATAS E DA TERRA',
        'Mestrado Profissional em Ensino e suas Tecnologias': 'CIENCIAS HUMANAS',
        'Mestrado SAEG - Linha de Pesquisa I - Sistemas Aplicados à Engenharia': 'CIENCIAS EXATAS E DA TERRA',
        'Mestrado SAEG - Linha de Pesquisa II - Sistemas Aplicados à Gestão': 'CIENCIAS EXATAS E DA TERRA',
        'Práticas Educacionais na Docência do Século XXI': 'CIENCIAS HUMANAS',
        'Pós-Graduação em Energias e Sustentabilidade': 'ENGENHARIAS',
        'Música': 'LINGUISTICA, LETRAS E ARTES',
        'Sistemas de Informação': 'CIENCIAS EXATAS E DA TERRA',
        'Sistemas de Telecomunicações': 'ENGENHARIAS',
        'Química': 'CIENCIAS EXATAS E DA TERRA',
        'Teatro': 'LINGUISTICA, LETRAS E ARTES'
    }

    # Inicializar coluna
    df_1['grande_area_do_curso'] = '-'

    # Aplicar mapeamento
    for curso, area in mapeamentos.items():
        df_1.loc[df_1['nome_curso'].str.contains(curso, na=False), 'grande_area_do_curso'] = area

    return df_1


def extrair_ano_nome(nome_arquivo):
    match = re.search(r"(20\d{2})", nome_arquivo)  # pega anos tipo 2017, 2018, 2019...
    if match:
        return match.group(1)
    return None