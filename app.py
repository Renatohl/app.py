import cx_Oracle
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import locale
import matplotlib.pyplot as plt

# Configurando a página para o modo de largura
st.set_page_config(layout="wide")

# Configurando a localização para o Brasil
locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')


# Incluindo Imagem da Logomarca na Sidebar
imagem_local = "assets/logo.png cardeal.png"
st.sidebar.image(imagem_local, use_column_width=True)


# Incluindo os dados da sidebar
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True) 
    # Adicionando campos de entrada de texto na sidebar para o número do pedido e número da nota fiscal
    numero_pedido = st.sidebar.text_input("Número do Pedido", "")
    numero_nota = st.sidebar.text_input("Número da Nota Fiscal", "")

# Função para estabelecer a conexão com o banco de dados
def conectar_banco():
    dsn = cx_Oracle.makedsn("181.41.174.203", "1521", service_name="CE2FZW_135075_W")
    username = "CLT135075CONSULTAUSER"
    password = "vxpot81503OMDEV!?"
    return create_engine(f'oracle+cx_oracle://{username}:{password}@{dsn}')


# Função para filtrar os dados com base nos números do pedido e da nota fiscal
@st.cache_data(show_spinner=False)
def filtrar_dados(numero_pedido=None, numero_nota=None):
    if numero_pedido or numero_nota:
        st.cache_data.clear()
        engine = conectar_banco()

        query = """
            SELECT DISTINCT C.DATA, C.DTLIBERA, D.DATAMON, A.DTFAT, A.NUMCAR, A.NUMPED, A.NUMNOTA, B.DESCRCA, B.DESCSUPERV, B.GERENTE, 
            A.CLIENTE, B.DESCROTA, A.MUNICIPIO, A.VLTOTAL, A.DTCANHOTO 
            FROM PCNFSAID A 
            JOIN XV_DAILY_NF_MERC B ON A.NUMNOTA = B.NUMNOTA 
            JOIN PCPEDC C ON A.NUMPED = C.NUMPED
            JOIN PCCARREG D ON A.NUMCAR = D.NUMCAR
            WHERE 1=1
        """
        if numero_pedido:
            query += f" AND A.NUMPED = '{numero_pedido}'"
        if numero_nota:
            query += f" AND A.NUMNOTA = '{numero_nota}'"

        df_resultado = pd.read_sql_query(query, engine)
        engine.dispose()  # Fechar a conexão
    else:
        # Retornar um DataFrame vazio caso nenhum número de pedido ou nota fiscal seja fornecido
        df_resultado = pd.DataFrame()

    return df_resultado

# Página principal do Streamlit
st.title('RELATÓRIO DE CONSULTA DE PEDIDO')
st.markdown("<br>", unsafe_allow_html=True)

# Filtrando os dados com base nos números fornecidos pelo usuário
df_resultado = filtrar_dados(numero_pedido, numero_nota)



try: 
    # Cria uma lista de datas das etapas do pedido
    status = df_resultado[['data', 'dtlibera', 'datamon', 'dtfat', 'dtcanhoto']].values

    # Determina o número total de etapas
    total_etapas = len(df_resultado) * 5  # Multiplicamos por 5 pois são 5 etapas possíveis para cada registro

    # Inicializa o contador de etapas concluídas
    etapas_concluidas = 0

    # Adiciona um container para abranger ambos os containers menores
    with st.container(border=True):
        # Exibe a barra de progresso
        progress = st.progress(0.0)


        #Quebra de colunas para exibição dos nomes dos status
        col1, col2, col3, col4, col5 = st.columns(5)

        # Itera sobre as linhas do DataFrame
        for idx, row in enumerate(status):
            # Itera sobre os status de cada linha
            for col_idx, status_col in enumerate(row):
                # Determina o texto do status com base na coluna atual
                if col_idx == 0:
                    with col1.container(border=False):
                        etapas_concluidas += 1
                        progress.progress(etapas_concluidas / total_etapas)
                        st.markdown("✅Pedido Digitado")
                elif col_idx == 1:
                    with col2.container(border=False):
                        if pd.isnull(status_col):
                            etapas_concluidas += 1
                            progress.progress(etapas_concluidas / total_etapas)
                            st.markdown("✅Pedido Liberado")
                        else:
                            etapas_concluidas += 1
                            progress.progress(etapas_concluidas / total_etapas)
                            st.markdown("✅Pedido Liberado")
                elif col_idx == 2:
                    with col3.container(border=False):
                        if pd.notnull(status_col):
                            etapas_concluidas += 1
                            progress.progress(etapas_concluidas / total_etapas)
                            st.markdown("✅Pedido Montado")
                        else:
                            st.markdown("❌Aguardando Montagem")
                elif col_idx == 3:
                    with col4.container(border=False):
                        if pd.notnull(status_col):
                            etapas_concluidas += 1
                            progress.progress(etapas_concluidas / total_etapas)
                            st.markdown("✅Pedido Faturado")
                        else:
                            st.markdown("❌Aguardando Faturamento")
                elif col_idx == 4:
                    with col5.container(border=False):
                        if pd.notnull(status_col):
                            etapas_concluidas += 1
                            progress.progress(etapas_concluidas / total_etapas)
                            st.markdown("✅Pedido Entregue")
                        else:
                            st.markdown("❌Aguardando Entrega")
except KeyError:
    pass  # Ignora a exceção caso o KeyError ocorra


st.markdown("<br>", unsafe_allow_html=True)



if df_resultado is not None and not df_resultado.empty:
    st.info('##### **📝Informações Gerais:**')
    # Adiciona um container para abranger ambos os containers menores
    with st.container(border=True):
        
        # Cria uma estrutura de duas colunas
        col1, col2 = st.columns(2)
        
        # Adiciona um container para cada coluna
        with col1.container(border=False):
            # Exibindo os resultados
            if df_resultado is not None and not df_resultado.empty:
                for index, row in df_resultado.iterrows():
                    st.write(f"**Número da Carga:** {row['numcar']}")
                    st.write(f"**Número do Pedido:** {row['numped']}")
                    st.write(f"**Número da Nota Fiscal:** {row['numnota']}")
                    st.write(f"**Valor Total:** {locale.currency(row['vltotal'])}")
                    st.write(f"**Data do Pedido:** {row['data'].strftime('%d/%m/%Y')}")
                    if row['dtlibera'] is None:  # Verifica se o valor é None
                        st.write(f"**Data de Liberação do pedido:** {row['data'].strftime('%d/%m/%Y')}")
                    else:
                        st.write(f"**Data de Liberação do pedido:** {row['dtlibera'].strftime('%d/%m/%Y %H:%M:%S')}")
                    st.write(f"**Data de Montagem da Carga:** {row['datamon'].strftime('%d/%m/%Y')}")
                    st.write(f"**Data do Faturamento:** {row['dtfat'].strftime('%d/%m/%Y')}")


        with col2.container(border=False):
            for index, row in df_resultado.iterrows():
                st.write(f"**Vendedor:** {row['descrca']}")
                st.write(f"**Supervisor:** {row['descsuperv']}")
                st.write(f"**Gerente:** {row['gerente']}")
                st.write(f"**Cliente:** {row['cliente']}")
                st.write(f"**Descrição da Rota:** {row['descrota']}")
                st.write(f"**Município:** {row['municipio']}")
                if row['dtcanhoto'] is not None:  # Verifica se o valor não é None
                    st.write(f"**Data da Entrega:** {row['dtcanhoto'].strftime('%d/%m/%Y')}")
                else:
                    st.write("**Data da Entrega:** Aguardando Informação")







        











   
           

           
     












