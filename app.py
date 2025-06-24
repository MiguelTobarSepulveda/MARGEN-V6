import streamlit as st
import pandas as pd
import requests
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from io import BytesIO

# --------- CONFIGURACIÓN DE LOGIN ---------
with open('usuarios.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

auth_result = authenticator.login('main')

if auth_result:
    name = auth_result['name']
    authentication_status = auth_result['authentication_status']
    username = auth_result['username']
else:
    name = None
    authentication_status = None
    username = None



if authentication_status is False:
    st.error('Usuario/contraseña incorrectos')
if authentication_status is None:
    st.warning('Por favor ingresa tus credenciales')

if authentication_status:
    authenticator.logout('Cerrar sesión', 'sidebar')
    st.sidebar.success(f'Bienvenido, {name}!')

    # --------- CARGA AUTOMÁTICA DEL ARCHIVO DESDE GOOGLE DRIVE ---------
    url_drive = 'https://docs.google.com/spreadsheets/d/1QhyIyTnKyupJ7Cg_TUMHUX0jcu-RbJuj/edit?usp=sharing&ouid=109595435915826227233&rtpof=true&sd=true'
    @st.cache_data(show_spinner=False)
    def cargar_excel_drive(url):
        response = requests.get(url)
        if response.status_code == 200:
            return pd.ExcelFile(BytesIO(response.content))
        else:
            st.error('No se pudo descargar el archivo de Google Drive.')
            return None

    excel = cargar_excel_drive(url_drive)
    if excel is not None:
        st.success("Archivo cargado correctamente.")

        # ------ Lee tus hojas aquí ------
        ventas = pd.read_excel(excel, sheet_name="LIBRO DE VENTAS")
        recetas = pd.read_excel(excel, sheet_name="RECETAS DE PRODUCTOS")
        precios = pd.read_excel(excel, sheet_name="PRECIO DE INSUMOS")
        
        # --------- FILTROS DE CONSULTA ---------
        cliente_sel = st.sidebar.selectbox("Cliente", ["Todos"] + sorted(ventas["CLIENTE"].unique().tolist()))
        producto_sel = st.sidebar.selectbox("Producto", ["Todos"] + sorted(ventas["NOMBRE DE PRODUCTO"].unique().tolist()))
        mes_sel = st.sidebar.selectbox("Mes", ["Todos"] + sorted(pd.to_datetime(ventas["FECHA"]).dt.strftime('%Y-%m').unique()))

        # --------- APLICAR FILTROS ---------
        data = ventas.copy()
        if cliente_sel != "Todos":
            data = data[data["CLIENTE"] == cliente_sel]
        if producto_sel != "Todos":
            data = data[data["NOMBRE DE PRODUCTO"] == producto_sel]
        if mes_sel != "Todos":
            data = data[pd.to_datetime(data["FECHA"]).dt.strftime('%Y-%m') == mes_sel]

        # --------- RESULTADOS FILTRADOS ---------
        st.write("Resultados filtrados:")
        st.dataframe(data)
        
        st.info("Pronto podrás ver márgenes y más detalles. ¿Qué filtro te gustaría agregar?")

    else:
        st.error("No se pudo cargar el archivo.")
