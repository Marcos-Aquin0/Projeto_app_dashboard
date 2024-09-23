import streamlit as st 
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go 
import openpyxl
import xlrd
import copy
import numpy as np

#função para categorizar os dados: direção do vento em graus na rosa dos ventos
def categorizar_direcao_16(dict_direcoes, graus, velocidade, indice):
    # Lista de direções com seus intervalos de graus
    direcoes = [
        ('N', (0, 11.25)), ('N', (348.75, 360)), ('NNE', (11.25, 33.75)), ('NE', (33.75, 56.25)),
        ('ENE', (56.25, 78.75)), ('E', (78.75, 101.25)), ('ESE', (101.25, 123.75)),
        ('SE', (123.75, 146.25)), ('SSE', (146.25, 168.75)), ('S', (168.75, 191.25)),
        ('SSO', (191.25, 213.75)), ('SO', (213.75, 236.25)), ('OSO', (236.25, 258.75)),
        ('O', (258.75, 281.25)), ('ONO', (281.25, 303.75)), ('NO', (303.75, 326.25)),
        ('NNO', (326.25, 348.75))]

    # Itera sobre a lista de direções e verifica o intervalo correspondente aos graus
    for direcao, (min_graus, max_graus) in direcoes:
        if min_graus <= graus < max_graus:
            dict_direcoes[direcao]['Frequencia'] += 1
            if indice not in dict_direcoes[direcao]['Indices']:
                dict_direcoes[direcao]['Indices'].append(indice)
            categorizar_velocidade(dict_direcoes[direcao], velocidade)
            break  # Sai do loop ao encontrar a direção correta

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

def velocidade_max(coluna_velocidade):
    vmax = 1
    for linha in coluna_velocidade:
        if linha > vmax:
            vmax = linha
    return vmax

#definição inicial do layout da página
st.set_page_config(layout="wide")

#pede para o usuário escolher o arquivo excel. Válido adicionar o formato csv depois
st.title("Análise de dados metereológicos")
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
    df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M').dt.time
    df=df.sort_values(by=["Data", "Hora"])

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

    st.sidebar.write("Filtro de mês e dia para os gráficos de linha")
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
    st.subheader("Tabela com os dados diários de acordo com os filtros de mês e dia")
    st.dataframe(dados_filtrados.iloc[:, list(range(0, 13))+ [15]])

    #plotagem de gráficos de linha, com marcadores para cada 15 min
    st.header("Gráficos de linha para Temperatura, Umidade, Radiações, Precipitação, Pressão Atmosférica, Classe do Vento e Desvio Padrão")
    for coluna in df.iloc[:, list(range(2, 5)) + [9, 10, 12, 15, 11]]: 
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
            if df[coluna].name == 'Direção do Vento (Graus)':
                eixo_y = dados_filtrados['Velocidade do Vento (m/s)']
                nome_eixo = 'Velocidade do Vento (m/s)'
                maxima = ''
            elif df[coluna].name == 'Direção do Vento Máxima (Graus)':
                eixo_y = dados_filtrados['Velocidade do Vento Máxima (m/s)']
                nome_eixo = 'Velocidade do Vento Máxima (m/s)'
                maxima = ' Máxima'
            
            st.header(f"Gráficos de linha e Rosa dos Ventos para Velocidade e Direção do Vento {maxima}")
            #gráfico com dois eixos y
            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=dados_filtrados['Hora'], y=eixo_y, mode='lines+markers',
                    name=nome_eixo,
                    hovertext=[f'Hora = {t.strftime("%H:%M")}<br>Velocidade = {v} m/s' for t, v in zip(dados_filtrados['Hora'], eixo_y)],
                    yaxis='y1', hoverinfo='text')
            )
                
            fig.add_trace(
                go.Scatter(
                    x=dados_filtrados['Hora'], y=dados_filtrados[coluna], mode='lines+markers',
                    name=dados_filtrados[coluna].name,
                    hovertext=[f'Hora = {t.strftime("%H:%M")}<br>Graus = {v}º' for t, v in zip(dados_filtrados['Hora'], dados_filtrados[coluna])],
                    yaxis='y2', hoverinfo='text')
            )

            # Atualizar o layout para adicionar o eixo y2
            fig.update_layout(
                title=f"Velocidade e Direção do Vento{maxima} do dia {day} de {month}",
                xaxis=dict(title='Hora'),
                yaxis=dict(title=nome_eixo, range=[0, velocidade_max(dados_filtrados[nome_eixo])]),  # Escala para velocidade
                yaxis2=dict(title=df[coluna].name, range=[0, 360], overlaying='y', side='right'),  # Eixo secundário
                legend=dict(x=0.5, y=1.01, xanchor='center', yanchor='bottom', orientation='h')
            )
              
            st.plotly_chart(fig, use_container_width=True)

            col1, col2 = st.columns(2) #divide a tela em 2 
            #plotagem da rosa dos ventos com 16 direções
            with col1:
                with st.container():
                    #filtro de 6 em 6 horas, ou dia inteiro           
                    lista_horas = ['00:00:00', '01:00:00', '02:00:00', '03:00:00', '04:00:00', '05:00:00', 
                                   '06:00:00', '07:00:00', '08:00:00', '09:00:00', '10:00:00', '11:00:00', 
                                   '12:00:00', '13:00:00', '14:00:00', '15:00:00', '16:00:00', '17:00:00', 
                                   '18:00:00', '19:00:00', '20:00:00', '21:00:00', '22:00:00', '23:00:00', '23:45:00']

                    mes1 = st.selectbox(f"Selecione o mês inicial do intervalo para {coluna}:", df["Month"].unique())
                    dia1 = st.selectbox(f"Selecione o dia inicial do intervalo para {coluna}:", sorted(df["Day"].unique()))

                    filtro1 = df[(df["Month"] == mes1) & (df["Day"] == dia1)]

                    hora_inicial = st.selectbox(f'Selecione o horário inicial para {coluna}:', lista_horas)
                    
                    mes2 = st.selectbox(f"Selecione o mês final do intervalo para {coluna}:", df["Month"].unique())
                    dia2 = st.selectbox(f"Selecione o dia final do intervalo para {coluna}:", sorted(df["Day"].unique()))

                    lista_horas2 = lista_horas.copy()
                    if (mes1 == mes2 and dia1 == dia2): 
                        for hora in lista_horas:
                            if hora <= hora_inicial:
                                lista_horas2.remove(hora)
                            else: break
                        hora_final = st.selectbox(f'Selecione o horário final para {coluna}:', lista_horas2)
                    else: hora_final = st.selectbox(f'Selecione o horário final para {coluna}: ', lista_horas)
                    
                    filtro2 = df[(df["Month"] == mes2) & (df["Day"] == dia2)]
                    
                    filtro1['Hora_str'] = filtro1['Hora'].astype(str)
                    filtro2['Hora_str'] = filtro2['Hora'].astype(str) 
                    
                    #encontrar o índice do dataframe para o mês, dia e hora 00h do filtro, para gerar a rosa dos ventos
                    linha_inicial = filtro1[filtro1['Hora_str'] == hora_inicial]
                    linha_final = filtro2[filtro2['Hora_str'] == hora_final]
                    if not linha_inicial.empty and not linha_final.empty:
                        indice_inicial = linha_inicial.index[0]
                        indice_final = linha_final.index[0]  # Pega o primeiro índice, caso haja múltiplas linhas
                        if indice_final < indice_inicial:
                            st.warning("O índice final é menor que o índice inicial. O período inicial deve ser anterior ao final.")

                        #cada direção recebe um dicionário de velocidades
                        #deepcopy é recomendado para elementos mais complexos, pois garante que todos os níveis da estrutura sejam copiados de forma independente.
                        dict_vel = {'Frequencia': 0, 'Calmaria': 0, '0.5 - 2.1': 0, '2.1 - 3.6': 0, '3.6 - 5.7': 0, '5.7 - 8.8': 0, '8.8 - 11.1': 0, '>= 11.1': 0, 'Indices':[]}
                        dict_direcoes = {'N': copy.deepcopy(dict_vel), 'NNE': copy.deepcopy(dict_vel), 'NE': copy.deepcopy(dict_vel), 'ENE': copy.deepcopy(dict_vel), 'E': copy.deepcopy(dict_vel), 'ESE': copy.deepcopy(dict_vel), 'SE': copy.deepcopy(dict_vel), 'SSE': copy.deepcopy(dict_vel),
                                        'S': copy.deepcopy(dict_vel), 'SSO': copy.deepcopy(dict_vel), 'SO': copy.deepcopy(dict_vel), 'OSO': copy.deepcopy(dict_vel), 'O': copy.deepcopy(dict_vel), 'ONO': copy.deepcopy(dict_vel), 'NO': copy.deepcopy(dict_vel), 'NNO': copy.deepcopy(dict_vel)}
                        total = 0  

                        filtro3 = df.iloc[indice_inicial:indice_final+1, [0, 1, df.columns.get_loc('Velocidade do Vento (m/s)'), 6, 8]]
                        filtro3 = filtro3.sort_values(by=['Data', 'Hora'])

                        for indice, linha in enumerate(filtro3[coluna][0:indice_final-indice_inicial+1]):
                                categorizar_direcao_16(dict_direcoes, linha, df['Velocidade do Vento (m/s)'][indice_inicial+indice], indice)
                                total +=1  
                                print(indice_inicial, indice_final, indice)             
                    else:
                        st.warning(f"Nenhuma linha com a hora pedida {hora_inicial} ou {hora_final} foi encontrada.")
    
            with col2:                     
                    #separando as informações de direção, velocidade e frequência para tratar como dataframe
                    evitar = ['Frequencia', 'Indices']
                    data = []
                    for direcao, info in dict_direcoes.items():
                        for velocidade, frequencia in info.items():
                            if velocidade not in evitar:
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
                                    title=f"Rosa dos Ventos {coluna} - {hora_inicial} {dia1} de {mes1} à {hora_final} {dia2} de {mes2}",
                                    barmode='stack')

                    st.plotly_chart(fig, use_container_width=True)
            
            st.write(f"Filtro do período escolhido - {hora_inicial} {dia1} de {mes1} à {hora_final} {dia2} de {mes2}")
            st.dataframe(filtro3.iloc[:,[0, 1, filtro3.columns.get_loc(coluna)]])    
    
            # Multiselect para escolher múltiplas opções
            options_dir = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
            selected_options = st.multiselect(f"Filtro de Direções para Rosa dos Ventos de Velocidade e Direção do Vento {maxima}", options_dir, placeholder="Escolha uma ou mais direções")

            if selected_options:
                todos_indices = []
                for direcao in selected_options:
                    todos_indices.extend(dict_direcoes[direcao]["Indices"])

                final_filtered_df = dados_filtrados.iloc[todos_indices]            
                final_filtered_df = final_filtered_df.sort_values('Hora')
                #adicionar um filtro por intervalo (ou por direção) e mostrar em um dataframe todos os resultados com dias e horas em que apareceu aquela direção    
                st.write(f"Tabela Filtro por Direção - {df[coluna].name} - {day} de {month}")
                st.dataframe(final_filtered_df.iloc[:, [0, 1, dados_filtrados.columns.get_loc(coluna)]]) # mostra data, hora e coluna do laço 

else:
    st.write("Aguardando a sua planilha!")