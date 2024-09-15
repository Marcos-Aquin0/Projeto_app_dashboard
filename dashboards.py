import streamlit as st 
import pandas as pd 
import plotly.express as px 
import openpyxl
import xlrd

def categorizar_direcao_16(dict_direcoes, graus):
    if 0 <= graus < 11.25 or 348.75 <= graus <= 360:
        dict_direcoes['N'] += 1
    elif 11.25 <= graus < 33.75:
        dict_direcoes['NNE'] += 1
    elif 33.75 <= graus < 56.25:
        dict_direcoes['NE'] += 1
    elif 56.25 <= graus < 78.75:
        dict_direcoes['ENE'] += 1
    elif 78.75 <= graus < 101.25:
        dict_direcoes['E'] += 1
    elif 101.25 <= graus < 123.75:
        dict_direcoes['ESE'] += 1
    elif 123.75 <= graus < 146.25:
        dict_direcoes['SE'] += 1
    elif 146.25 <= graus < 168.75:
        dict_direcoes['SSE'] += 1
    elif 168.75 <= graus < 191.25:
        dict_direcoes['S'] += 1
    elif 191.25 <= graus < 213.75:
        dict_direcoes['SSO'] += 1
    elif 213.75 <= graus < 236.25:
        dict_direcoes['SO'] += 1
    elif 236.25 <= graus < 258.75:
        dict_direcoes['OSO'] += 1
    elif 258.75 <= graus < 281.25:
        dict_direcoes['O'] += 1
    elif 281.25 <= graus < 303.75:
        dict_direcoes['ONO'] += 1
    elif 303.75 <= graus < 326.25:
        dict_direcoes['NO'] += 1
    elif 326.25 <= graus < 348.75:
        dict_direcoes['NNO'] += 1

st.set_page_config(layout="wide")

st.write("Análise de dados metereológicos")
#if csv
tipo = st.selectbox("Escolha o tipo do arquivo excel: ", ['xls', 'xlsx'])
upload_file = st.file_uploader(f"Escolha o arquivo excel {tipo}: ", type = [tipo])

if tipo == 'xls':
    ferramenta = 'xlrd'
elif tipo == 'xlsx':
    ferramenta = 'openpyxl'
else:
    ferramenta = ''

if upload_file is not None and ferramenta != '':
    df = pd.read_excel(upload_file, engine=ferramenta)
    #convertendo colunas em string, tratando comma e depois convertendo para float
    for coluna in df.iloc[:, list(range(2, 13)) + [15]]:
        df[coluna] = df[coluna].astype(str)
        df[coluna] = df[coluna].str.replace(',', '.').astype(float)
        df[coluna] = pd.to_numeric(df[coluna], errors='coerce')

    #formatando data e hora
    df["Data"] = pd.to_datetime(df["Data"], format='%d/%m/%Y')
    df=df.sort_values("Data")

    df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M').dt.time

    meses_pt = {
    'January': 'Janeiro',
    'February': 'Fevereiro',
    'March': 'Março',
    'April': 'Abril',
    'May': 'Maio',
    'June': 'Junho',
    'July': 'Julho',
    'August': 'Agosto',
    'September': 'Setembro',
    'October': 'Outubro',
    'November': 'Novembro',
    'December': 'Dezembro'
    }
    #caixa de seleção
    df['Month'] = df['Data'].dt.strftime('%B de %Y').str.replace('%B', lambda x: meses_pt[x.group()])

    month = st.sidebar.selectbox("Mês", df["Month"].unique())

    df['Day'] = df['Data'].dt.strftime('%d')
    day = st.sidebar.selectbox("Dia", sorted(df["Day"].unique()))

    dados_filtrados = df[(df["Month"] == month) & (df["Day"] == day)]

    #ordenar por hora
    dados_filtrados = dados_filtrados.sort_values('Hora')

    # Criando um novo DataFrame sem as colunas a serem ocultadas
    colunas_a_ocultar = ['Month', 'Day', 'Bateria (V)', 'Temperatura Interna (ºC)']
    st.dataframe(dados_filtrados.iloc[:, list(range(0, 13))+ [15]])

    for coluna in df.iloc[:, list(range(2, 6)) + [7, 9, 10, 12, 15, 11]]: #falta em graus, 6, 8, 11
        # Verificando se há dados para plotar
        if dados_filtrados.empty:
            st.warning("Não há dados para o dia selecionado.")
        else:
            # Criação do gráfico com Plotly
            fig_date = px.line(dados_filtrados, x='Hora', y=df[coluna].name, 
                            title=f'{df[coluna].name} do Dia {day} de {month}',
                            markers=True)
            
            st.plotly_chart(fig_date, use_container_width=True)

    for coluna in df.iloc[:, [6, 8]]:
        if dados_filtrados.empty:
            st.warning("Não há dados para o dia selecionado.")
        else:
            col1, col2 = st.columns(2) #divide a tela em 2 

            with col1:
                fig3 = px.line(dados_filtrados, x='Hora', y=df[coluna].name, 
                            title=f'{df[coluna].name} - {day} de {month}',
                            markers=True)
                st.plotly_chart(fig3, use_container_width=True)

            with col2:
                with st.container():           
                    horas_6 = st.selectbox('Selecione o horário:', [f'Dia inteiro: {df[coluna].name}', f'0h-5h45: {df[coluna].name}', f'6h-11h45: {df[coluna].name}', f'12h-17h45: {df[coluna].name}', f'18h-23h45: {df[coluna].name}'])
                    dict_direcoes = {'N':0, 'NNE':0, 'NE':0, 'ENE':0, 'E':0, 'ESE':0, 'SE':0, 'SSE':0,
                        'S':0, 'SSO':0, 'SO':0, 'OSO':0, 'O':0, 'ONO':0, 'NO':0, 'NNO':0}
                    total = 0

                    if 'Dia inteiro' in horas_6:
                        dict_direcoes = {'N':0, 'NNE':0, 'NE':0, 'ENE':0, 'E':0, 'ESE':0, 'SE':0, 'SSE':0,
                        'S':0, 'SSO':0, 'SO':0, 'OSO':0, 'O':0, 'ONO':0, 'NO':0, 'NNO':0}
                        total = 0
                        for linha in dados_filtrados[coluna]:
                            categorizar_direcao_16(dict_direcoes, linha)
                            total +=1  

                    elif '0h-5h45' in horas_6:
                        dict_direcoes = {'N':0, 'NNE':0, 'NE':0, 'ENE':0, 'E':0, 'ESE':0, 'SE':0, 'SSE':0,
                        'S':0, 'SSO':0, 'SO':0, 'OSO':0, 'O':0, 'ONO':0, 'NO':0, 'NNO':0}
                        total = 0
                        
                        for indice, linha in enumerate(dados_filtrados[coluna][0:24]):
                            # print(indice+72, df['Hora'][indice+72], dados_filtrados[coluna][indice+72])
                            categorizar_direcao_16(dict_direcoes, linha)
                            total +=1

                    elif '6h-11h45' in horas_6:
                        dict_direcoes = {'N':0, 'NNE':0, 'NE':0, 'ENE':0, 'E':0, 'ESE':0, 'SE':0, 'SSE':0,
                        'S':0, 'SSO':0, 'SO':0, 'OSO':0, 'O':0, 'ONO':0, 'NO':0, 'NNO':0}
                        total = 0
                        for linha in dados_filtrados[coluna][24:48]:
                            categorizar_direcao_16(dict_direcoes, linha)
                            total +=1

                    elif '12h-17h45' in horas_6:
                        dict_direcoes = {'N':0, 'NNE':0, 'NE':0, 'ENE':0, 'E':0, 'ESE':0, 'SE':0, 'SSE':0,
                        'S':0, 'SSO':0, 'SO':0, 'OSO':0, 'O':0, 'ONO':0, 'NO':0, 'NNO':0}
                        total = 0
                        for linha in dados_filtrados[coluna][48:72]:
                            categorizar_direcao_16(dict_direcoes, linha)
                            total +=1

                    elif '18h-23h45' in horas_6:
                        dict_direcoes = {'N':0, 'NNE':0, 'NE':0, 'ENE':0, 'E':0, 'ESE':0, 'SE':0, 'SSE':0,
                        'S':0, 'SSO':0, 'SO':0, 'OSO':0, 'O':0, 'ONO':0, 'NO':0, 'NNO':0}
                        total = 0
                        for linha in dados_filtrados[coluna][72:96]:
                            categorizar_direcao_16(dict_direcoes, linha)
                            total +=1             
                    
                    df2 = pd.DataFrame({'Direção': dict_direcoes.keys(), 'Frequencia': dict_direcoes.values()})
                    df2['Frequencia_Normalizada'] = round((df2['Frequencia'] / total) * 100, 2)
                            
                    fig = px.bar_polar(df2, r="Frequencia_Normalizada", theta="Direção",
                                        color="Direção", color_discrete_sequence=px.colors.sequential.Viridis,
                                        template="plotly_white",
                                        title=f"Rosa dos Ventos para {df[coluna].name} - {horas_6}")
                        
                    st.plotly_chart(fig, use_container_width=True)    
   
else:
    st.write("Aguardando a sua planilha!")