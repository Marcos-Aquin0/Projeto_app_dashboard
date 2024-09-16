import streamlit as st 
import pandas as pd 
import plotly.express as px 
import openpyxl
import xlrd
import copy
import numpy as np

#função para categorizar os dados: direção do vento em graus na rosa dos ventos
def categorizar_direcao_16(dict_direcoes, graus, velocidade):
    if 0 <= graus < 11.25 or 348.75 <= graus <= 360:
        dict_direcoes['N']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['N'], velocidade)
    elif 11.25 <= graus < 33.75:
        dict_direcoes['NNE']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['NNE'], velocidade)
    elif 33.75 <= graus < 56.25:
        dict_direcoes['NE']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['NE'], velocidade)
    elif 56.25 <= graus < 78.75:
        dict_direcoes['ENE']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['ENE'], velocidade)
    elif 78.75 <= graus < 101.25:
        dict_direcoes['E']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['E'], velocidade)
    elif 101.25 <= graus < 123.75:
        dict_direcoes['ESE']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['ESE'], velocidade)
    elif 123.75 <= graus < 146.25:
        dict_direcoes['SE']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['SE'], velocidade)
    elif 146.25 <= graus < 168.75:
        dict_direcoes['SSE']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['SSE'], velocidade)
    elif 168.75 <= graus < 191.25:
        dict_direcoes['S']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['S'], velocidade)
    elif 191.25 <= graus < 213.75:
        dict_direcoes['SSO']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['SSO'], velocidade)
    elif 213.75 <= graus < 236.25:
        dict_direcoes['SO']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['SO'], velocidade)
    elif 236.25 <= graus < 258.75:
        dict_direcoes['OSO']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['OSO'], velocidade)
    elif 258.75 <= graus < 281.25:
        dict_direcoes['O']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['O'], velocidade)
    elif 281.25 <= graus < 303.75:
        dict_direcoes['ONO']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['ONO'], velocidade)
    elif 303.75 <= graus < 326.25:
        dict_direcoes['NO']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['NO'], velocidade)
    elif 326.25 <= graus < 348.75:
        dict_direcoes['NNO']['Frequencia'] += 1
        categorizar_velocidade(dict_direcoes['NNO'], velocidade)

#função para categorizar a velocidade do vento de acordo com a direção
def categorizar_velocidade(dict_velocidade, velocidade):
    if 0 <= velocidade < 0.5:
        dict_velocidade['Calmaria'] += 1
    elif 0.5 <= velocidade < 2.1:
        dict_velocidade['0.5 - 2.1'] += 1
    elif 2.1 <= velocidade < 3.6:
        dict_velocidade['2.1 - 3.6'] += 1
    elif 3.6 <= velocidade < 5.7:
        dict_velocidade['3.6 - 5.7'] += 1
    elif 5.7 <= velocidade < 8.8:
        dict_velocidade['5.7 - 8.8'] += 1
    elif 8.8 <= velocidade < 11.1:
        dict_velocidade['8.8 - 11.1'] += 1
    elif velocidade >= 11.1:
        dict_velocidade['>= 11.1'] += 1

#definição inicial do layout da página
st.set_page_config(layout="wide")

#pede para o usuário escolher o arquivo excel. Válido adicionar o formato csv depois
st.write("Análise de dados metereológicos")
tipo = st.selectbox("Escolha o tipo do arquivo excel: ", ['xls', 'xlsx'])
upload_file = st.file_uploader(f"Escolha o arquivo excel {tipo}: ", type = [tipo])

if tipo == 'xls':
    ferramenta = 'xlrd'
elif tipo == 'xlsx':
    ferramenta = 'openpyxl'
else:
    ferramenta = ''

#se recebeu um arquivo válido
if upload_file is not None and ferramenta != '':
    df = pd.read_excel(upload_file, engine=ferramenta)
    #convertendo colunas em string, tratando a vírgula (,) e depois convertendo para float
    for coluna in df.iloc[:, list(range(2, 13)) + [15]]: #os dados da coluna 13 e 14 não serão utilizados no momento
        df[coluna] = df[coluna].astype(str)
        df[coluna] = df[coluna].str.replace(',', '.').astype(float)
        df[coluna] = pd.to_numeric(df[coluna], errors='coerce')

    #formatando data e hora
    df["Data"] = pd.to_datetime(df["Data"], format='%d/%m/%Y')
    df=df.sort_values("Data")

    df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M').dt.time

    #streamlit não reconheceu a biblioteca locale, foi necessário realizar essa conversão manualmente:
    meses_pt = {
    'January de 2024': 'Janeiro de 2024',
    'February de 2024': 'Fevereiro de 2024',
    'March de 2024': 'Março de 2024',
    'April de 2024': 'Abril de 2024',
    'May de 2024': 'Maio de 2024',
    'June de 2024': 'Junho de 2024',
    'July de 2024': 'Julho de 2024',
    'August de 2024': 'Agosto de 2024',
    'September de 2024': 'Setembro de 2024',
    'October de 2024': 'Outubro de 2024',
    'November de 2024': 'Novembro de 2024',
    'December de 2024': 'Dezembro de 2024'
    }

    #caixa de seleção
    df['Month2'] = df['Data'].dt.strftime('%B de %Y')
    df['Month'] = df['Month2'].replace(meses_pt, regex=True)
    month = st.sidebar.selectbox("Mês", df["Month"].unique())

    df['Day'] = df['Data'].dt.strftime('%d')
    day = st.sidebar.selectbox("Dia", sorted(df["Day"].unique()))

    #dois filtros = mês e dia, para análise mais precisa dos dados
    dados_filtrados = df[(df["Month"] == month) & (df["Day"] == day)]

    #ordenar os dados filtrados por hora
    dados_filtrados = dados_filtrados.sort_values('Hora')

    # As colunas ocultadas na apresentação do dataframe são: colunas_a_ocultar = ['Month', 'Day', 'Bateria (V)', 'Temperatura Interna (ºC)']
    st.dataframe(dados_filtrados.iloc[:, list(range(0, 13))+ [15]])

    #plotagem de gráficos de linha, com marcadores para cada 15 min
    for coluna in df.iloc[:, list(range(2, 6)) + [7, 9, 10, 12, 15, 11]]: 
        # Verificando se há dados para plotar
        if dados_filtrados.empty:
            st.warning("Não há dados para o dia selecionado.") 
        else:
            # Criação do gráfico
            fig_date = px.line(dados_filtrados, x='Hora', y=df[coluna].name, 
                            title=f'{df[coluna].name} do Dia {day} de {month}',
                            markers=True)
            
            st.plotly_chart(fig_date, use_container_width=True)

    #informações do dataframe em graus
    for coluna in df.iloc[:, [6, 8]]:
        if dados_filtrados.empty:
            st.warning("Não há dados para o dia selecionado.")
        else:
            col1, col2 = st.columns(2) #divide a tela em 2 

            with col1:
                #primeiro o gráfico de linha correspondente
                fig3 = px.line(dados_filtrados, x='Hora', y=df[coluna].name, 
                            title=f'{df[coluna].name} - {day} de {month}',
                            markers=True)
                st.plotly_chart(fig3, use_container_width=True)

            #plotagem da rosa dos ventos com 16 direções
            with col2:
                with st.container():
                    #filtro de 6 em 6 horas, ou dia inteiro           
                    horas_6 = st.selectbox('Selecione o horário:', [f'Dia inteiro: {df[coluna].name}', f'0h-5h45: {df[coluna].name}', f'6h-11h45: {df[coluna].name}', f'12h-17h45: {df[coluna].name}', f'18h-23h45: {df[coluna].name}'])
                    
                    #cada direção recebe um dicionário de velocidades
                    #deepcopy é recomendado para elementos mais complexos, pois garante que todos os níveis da estrutura sejam copiados de forma independente.
                    dict_vel = {'Frequencia': 0, 'Calmaria': 0, '0.5 - 2.1': 0, '2.1 - 3.6': 0, '3.6 - 5.7': 0, '5.7 - 8.8': 0, '8.8 - 11.1': 0, '>= 11.1': 0}
                    dict_direcoes = {'N': copy.deepcopy(dict_vel), 'NNE': copy.deepcopy(dict_vel), 'NE': copy.deepcopy(dict_vel), 'ENE': copy.deepcopy(dict_vel), 'E': copy.deepcopy(dict_vel), 'ESE': copy.deepcopy(dict_vel), 'SE': copy.deepcopy(dict_vel), 'SSE': copy.deepcopy(dict_vel),
                                     'S': copy.deepcopy(dict_vel), 'SSO': copy.deepcopy(dict_vel), 'SO': copy.deepcopy(dict_vel), 'OSO': copy.deepcopy(dict_vel), 'O': copy.deepcopy(dict_vel), 'ONO': copy.deepcopy(dict_vel), 'NO': copy.deepcopy(dict_vel), 'NNO': copy.deepcopy(dict_vel)}
                    total = 0

                    dados_filtrados['Data_str'] = dados_filtrados['Data'].astype(str)
                    dados_filtrados['Hora_str'] = dados_filtrados['Hora'].astype(str) 
                    
                    #encontrar o índice do dataframe para o mês, dia e hora 00h do filtro, para gerar a rosa dos ventos
                    linha_00h = dados_filtrados[dados_filtrados['Hora_str'] == '00:00:00']
                    if not linha_00h.empty:
                        indice_00h = linha_00h.index[0]  # Pega o primeiro índice, caso haja múltiplas linhas
                        
                    else:
                        st.warning("Nenhuma linha com hora 00:00:00 encontrada.")
                    
                    if 'Dia inteiro' in horas_6:
                        dict_vel = {'Frequencia': 0, 'Calmaria': 0, '0.5 - 2.1': 0, '2.1 - 3.6': 0, '3.6 - 5.7': 0, '5.7 - 8.8': 0, '8.8 - 11.1': 0, '>= 11.1': 0}
                        dict_direcoes = {'N': copy.deepcopy(dict_vel), 'NNE': copy.deepcopy(dict_vel), 'NE': copy.deepcopy(dict_vel), 'ENE': copy.deepcopy(dict_vel), 'E': copy.deepcopy(dict_vel), 'ESE': copy.deepcopy(dict_vel), 'SE': copy.deepcopy(dict_vel), 'SSE': copy.deepcopy(dict_vel),
                                         'S': copy.deepcopy(dict_vel), 'SSO': copy.deepcopy(dict_vel), 'SO': copy.deepcopy(dict_vel), 'OSO': copy.deepcopy(dict_vel), 'O': copy.deepcopy(dict_vel), 'ONO': copy.deepcopy(dict_vel), 'NO': copy.deepcopy(dict_vel), 'NNO': copy.deepcopy(dict_vel)}
                        total = 0

                        for indice, linha in enumerate(dados_filtrados[coluna][0:96]):
                            categorizar_direcao_16(dict_direcoes, linha, dados_filtrados['Velocidade do Vento (m/s)'][indice_00h+indice])
                            total +=1   

                    elif '0h-5h45' in horas_6:
                        dict_vel = {'Frequencia': 0, 'Calmaria': 0, '0.5 - 2.1': 0, '2.1 - 3.6': 0, '3.6 - 5.7': 0, '5.7 - 8.8': 0, '8.8 - 11.1': 0, '>= 11.1': 0}
                        dict_direcoes = {'N': copy.deepcopy(dict_vel), 'NNE': copy.deepcopy(dict_vel), 'NE': copy.deepcopy(dict_vel), 'ENE': copy.deepcopy(dict_vel), 'E': copy.deepcopy(dict_vel), 'ESE': copy.deepcopy(dict_vel), 'SE': copy.deepcopy(dict_vel), 'SSE': copy.deepcopy(dict_vel),
                                         'S': copy.deepcopy(dict_vel), 'SSO': copy.deepcopy(dict_vel), 'SO': copy.deepcopy(dict_vel), 'OSO': copy.deepcopy(dict_vel), 'O': copy.deepcopy(dict_vel), 'ONO': copy.deepcopy(dict_vel), 'NO': copy.deepcopy(dict_vel), 'NNO': copy.deepcopy(dict_vel)}
                        total = 0

                        for indice, linha in enumerate(dados_filtrados[coluna][0:24]):
                            categorizar_direcao_16(dict_direcoes, linha, dados_filtrados['Velocidade do Vento (m/s)'][indice_00h+indice])
                            total +=1 

                    elif '6h-11h45' in horas_6:
                        dict_vel = {'Frequencia': 0, 'Calmaria': 0, '0.5 - 2.1': 0, '2.1 - 3.6': 0, '3.6 - 5.7': 0, '5.7 - 8.8': 0, '8.8 - 11.1': 0, '>= 11.1': 0}
                        dict_direcoes = {'N': copy.deepcopy(dict_vel), 'NNE': copy.deepcopy(dict_vel), 'NE': copy.deepcopy(dict_vel), 'ENE': copy.deepcopy(dict_vel), 'E': copy.deepcopy(dict_vel), 'ESE': copy.deepcopy(dict_vel), 'SE': copy.deepcopy(dict_vel), 'SSE': copy.deepcopy(dict_vel),
                                         'S': copy.deepcopy(dict_vel), 'SSO': copy.deepcopy(dict_vel), 'SO': copy.deepcopy(dict_vel), 'OSO': copy.deepcopy(dict_vel), 'O': copy.deepcopy(dict_vel), 'ONO': copy.deepcopy(dict_vel), 'NO': copy.deepcopy(dict_vel), 'NNO': copy.deepcopy(dict_vel)}
                        total = 0

                        for indice, linha in enumerate(dados_filtrados[coluna][24:48]):
                            categorizar_direcao_16(dict_direcoes, linha, dados_filtrados['Velocidade do Vento (m/s)'][indice_00h+indice+24])
                            total +=1 

                    elif '12h-17h45' in horas_6:
                        dict_vel = {'Frequencia': 0, 'Calmaria': 0, '0.5 - 2.1': 0, '2.1 - 3.6': 0, '3.6 - 5.7': 0, '5.7 - 8.8': 0, '8.8 - 11.1': 0, '>= 11.1': 0}
                        dict_direcoes = {'N': copy.deepcopy(dict_vel), 'NNE': copy.deepcopy(dict_vel), 'NE': copy.deepcopy(dict_vel), 'ENE': copy.deepcopy(dict_vel), 'E': copy.deepcopy(dict_vel), 'ESE': copy.deepcopy(dict_vel), 'SE': copy.deepcopy(dict_vel), 'SSE': copy.deepcopy(dict_vel),
                                         'S': copy.deepcopy(dict_vel), 'SSO': copy.deepcopy(dict_vel), 'SO': copy.deepcopy(dict_vel), 'OSO': copy.deepcopy(dict_vel), 'O': copy.deepcopy(dict_vel), 'ONO': copy.deepcopy(dict_vel), 'NO': copy.deepcopy(dict_vel), 'NNO': copy.deepcopy(dict_vel)}
                        total = 0

                        for indice, linha in enumerate(dados_filtrados[coluna][48:72]):
                            categorizar_direcao_16(dict_direcoes, linha, dados_filtrados['Velocidade do Vento (m/s)'][indice_00h+indice+48])
                            total +=1 

                    elif '18h-23h45' in horas_6:
                        dict_vel = {'Frequencia': 0, 'Calmaria': 0, '0.5 - 2.1': 0, '2.1 - 3.6': 0, '3.6 - 5.7': 0, '5.7 - 8.8': 0, '8.8 - 11.1': 0, '>= 11.1': 0}
                        dict_direcoes = {'N': copy.deepcopy(dict_vel), 'NNE': copy.deepcopy(dict_vel), 'NE': copy.deepcopy(dict_vel), 'ENE': copy.deepcopy(dict_vel), 'E': copy.deepcopy(dict_vel), 'ESE': copy.deepcopy(dict_vel), 'SE': copy.deepcopy(dict_vel), 'SSE': copy.deepcopy(dict_vel),
                                         'S': copy.deepcopy(dict_vel), 'SSO': copy.deepcopy(dict_vel), 'SO': copy.deepcopy(dict_vel), 'OSO': copy.deepcopy(dict_vel), 'O': copy.deepcopy(dict_vel), 'ONO': copy.deepcopy(dict_vel), 'NO': copy.deepcopy(dict_vel), 'NNO': copy.deepcopy(dict_vel)}
                        total = 0

                        for indice, linha in enumerate(dados_filtrados[coluna][72:96]):
                            categorizar_direcao_16(dict_direcoes, linha, dados_filtrados['Velocidade do Vento (m/s)'][indice_00h+indice+72])
                            total +=1             
                    
                    #separando as informações de direção, velocidade e frequência para tratar como dataframe
                    data = []
                    for direcao, info in dict_direcoes.items():
                        for velocidade, frequencia in info.items():
                            if velocidade != 'Frequencia':
                                data.append({'Direção': direcao, 'Velocidade': velocidade, 'Frequencia': frequencia})

                    df2 = pd.DataFrame(data)
                    #normalização em porcentagem da frequencia obtida de cada direção e velocidade
                    df2['Frequencia: '] = (round((df2['Frequencia'] / total) * 100, 2))

                    #cores para a legenda de velocidades
                    colors = ['lightblue', 'blue', 'purple', 'green', 'yellow', 'orange', 'red']
                    
                    #rosa dos ventos é um gráfico polar, com barras
                    fig = px.bar_polar(df2, r="Frequencia: ", theta="Direção",
                                    color="Velocidade",
                                    color_discrete_sequence=colors,
                                    template="plotly_white",
                                    title=f"Rosa dos Ventos {df[coluna].name} - {horas_6}",
                                    barmode='stack')

                    st.plotly_chart(fig, use_container_width=True)    
   
else:
    st.write("Aguardando a sua planilha!")