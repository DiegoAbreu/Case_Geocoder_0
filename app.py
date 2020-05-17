# Portal Oi de Geocodificação - Caso de Uso: 

# Pacotes
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import geopy.distance

# Título:
st.image('https://www.oi.com.br/empresas/publicV2/brand-oi.svg', use_column_width=False)
st.title('Caso de uso do Portal Oi de Geocodificação:')
st.header('Aplicação para encontrar endereços mais próximos')

# Recursos
recursos_df = pd.read_csv('recursos.csv', sep=';', encoding = "ISO-8859-1")
recursos_df['Localidade'] = 'Recursos'
recursos_df['Bolha'] = 0.05

# Introdução
st.markdown("Um uso bastante comum de dados geocodificados é o cálculo de distância entre dois ou mais pontos. Diversos sites utilizam esse recurso para permitir que os usuários possam pesquisar e encontrar locais próximos.")
st.markdown("")
st.write('Veja o exemplo a seguir:')

# Plot Recursos
import plotly.express as px
fig1 = px.scatter_mapbox(recursos_df, lat="Latitude", lon="Longitude", hover_name="Ponto", zoom=10, height=500)
fig1.update_layout(mapbox_style="carto-positron")
fig1.update_layout(margin={"r":0,"t":25,"l":0,"b":0})
st.plotly_chart(fig1)

st.markdown("No mapa acima temos a localização de 100 escolas públicas da cidade do Rio de Janeiro. Insira um endereço no campo a a seguir e descubra quais escolas mais próximas.")

# Endereço para geocodificar:
endereco_usuario = st.text_input('Faça sua busca:','')

# Token:
Token_ = st.sidebar.text_input('Insira o token do Portal Oi de Geocodificação','')

def consulta(x):
    if x == '':
        return
    else:
        #Consulta:
        headers = {'accept': '*/*','Authorization': Token_}
        params = (('endereco', x),)
        response = requests.get('https://geosite.oi.net.br/geocodificacao-api/api/v1/geocode/json', headers=headers, params=params)
        
        # Resultados:
        resultado = pd.DataFrame(response.json())
        Loc_usuario = pd.DataFrame()
        Loc_usuario['Ponto'] = resultado['endereco']
        Loc_usuario['Latitude'] = resultado['latitude']
        Loc_usuario['Longitude'] = resultado['longitude']
        Loc_usuario['Bolha'] = 0.3
        Loc_usuario['Localidade'] = "Você"

        # Usuário + Recursos
        usu_recs = pd.concat([Loc_usuario, recursos_df])

        # Concatenação de lat_longs
        ref_usuario = list(zip(Loc_usuario['Latitude'], Loc_usuario['Longitude']))
        lat_long = list(zip(usu_recs['Latitude'], usu_recs['Longitude']))

        # Distancia ref_usu
        list_dist = list(map(lambda x: round(geopy.distance.distance(x, ref_usuario).km,3), lat_long))
        usu_recs["Distancia(km)"] = list_dist
        usu_recs["Distancia(km)"] = usu_recs["Distancia(km)"].round(2)
        usu_recs = usu_recs.reset_index(drop=True)
        usu_recs = usu_recs.sort_values(by=['Distancia(km)'])
        usu_recs = usu_recs.reset_index(drop=True)
        usu_recs["Distancia(km)"] = usu_recs["Distancia(km)"].astype(str)
        usu_recs["Distancia(km)"] = usu_recs["Distancia(km)"].replace('00','')

        # Tag top 5
        usu_recs.loc[usu_recs.index <= 5, 'Localidade'] = 'Escolas mais próximas' 
        usu_recs.loc[usu_recs.index > 5, 'Localidade'] = 'Escolas' 
        usu_recs.loc[usu_recs.index == 0, 'Localidade'] = 'Você' 
        usu_recs = usu_recs.rename(columns={'Ponto': 'Endereço', 'Localidade': 'Ponto' })

        # Top 5 mais próximas
        st.markdown("***")
        st.write('Essas são as 5 escolas mais próximas do seu endereço:')

        # DataFrame Top5
        top_5 = (usu_recs.loc[1:]).head()
        top_5 = top_5[['Endereço', 'Ponto','Distancia(km)']]
        top_5
        st.markdown("Veja no Mapa:")

        # Plot
        import plotly.express as px
        fig2 = px.scatter_mapbox(usu_recs, lat="Latitude", lon="Longitude", hover_name="Endereço", zoom=10, height=500, color="Ponto", size= 'Bolha')
        fig2.update_layout(mapbox_style="carto-positron")
        fig2.update_layout(margin={"r":0,"t":25,"l":0,"b":0})
        fig2.update_layout({'legend_orientation':'h'})
        st.plotly_chart(fig2)
        st.markdown("Confira a lista completa ordenada por proximidade:")
        lista_completa = usu_recs[['Endereço', 'Ponto', 'Distancia(km)']]
        lista_completa
        st.markdown("***")
        
        # Detalhes técnicos
        if st.checkbox('Ver detalhes técnicos'):
            # Texto sobre o uso do Geocoder Oi
            #st.markdown("***")
            st.header('Onde e como foi utilizado o Portal Oi de Geocodificação nessa aplicação?')
            st.markdown("A Geocodificação de endereços foi aplicada em dois momentos nessa solução:")
            st.markdown("**1 - ** Obter os pontos de latitude e longitude dos endereços das Lojas Oi. Para isso utilizamos o recurso de processamento em lote do Portal. Onde fazemos o upload de nossa tabela de endereços e após o processamento recebemos um arquivo com seus respectivos valores de coordenadas.")
            st.markdown("Função de processamento em lote do Portal Oi de Geocodificação:")
            st.image('img/01.png', use_column_width=True)
            st.markdown("Tabela inicial:")
            entrada_basica = recursos_df['Ponto']
            entrada_basica
            st.markdown("Tabela com informações de coordenadas após o processamento:")
            entrada_latlng = recursos_df[['Ponto', 'Latitude', 'Longitude']]
            entrada_latlng
            st.markdown("Com essas informações de Latitude e Longititude agora disponíveis é possivel exibir os endereços graficamente como pontos em uma mapa.")
            st.plotly_chart(fig1)
            st.markdown("**2 - ** A segunda geocodificação ocorre sempre que um usuário pesquisa por um endereço. Para essa etapa utilizamos o recurso de consumo via API que nos permite geocodificar fora da Portal, ou seja dentro de nossa aplicação.")
            st.markdown("Na opção de documentação, temos todos os recursos do Portal que podemos consumir via API. Nesse caso usamos o Geocode Get.")
            st.image('img/02.png', use_column_width=True)
            st.markdown("É necessário definir o formato em que você quer receber a geocodificação (json ou xml). Você também pode inserir uma consulta de teste para verificar como será a saída.")
            st.image('img/03.png', use_column_width=True)
            st.markdown("Após executar é exibido um script curl, juntamente com a URL de requisição para você adicionar ao código. Dentro do código Curl temos o token (em destaque) que permite o consumo via API. Logo abaixo, temos a amostra de como a consulta será enviada para sua aplicação. ")
            st.image('img/04.png', use_column_width=True)
            st.markdown("Com a latitude e longitude do endereço pesquisado, podemos então calcular as distâncias entre os pontos, ordená-los e apresentar o resultado final.")
            st.plotly_chart(fig2)
            st.markdown("***")
            st.markdown("**Tecnologias utilizadas na criação deste caso de uso:**")
            st.markdown("* Python - Linguagem de Programação;\n* Streamlit - Framework de Interface Visual;\n* GitHub - Hospedagem de código e arquivos;\n* Heroku - Ambiente de produção;\n* Portal Oi de Geocodificação - Conversão de endereços em coordenadas.")
            st.markdown("Código do projeto disponível [aqui.](https://github.com/DiegoAbreu/Case_Geocoder_0 )")
            st.markdown("***")

        return
consulta(endereco_usuario)

