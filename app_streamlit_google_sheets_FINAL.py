
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["GCP_SERVICE_ACCOUNT"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1zKh2Gc6zyA2BFZOfbr1G9aWd0n7-V0zVrq9R6eV3ZXI").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("📋 Dashboard de Horarios por Ciudad")

# Selección de ciudad
ciudades = sorted(df["Ciudad"].dropna().unique())
ciudad_seleccionada = st.selectbox("🌆 Selecciona una ciudad", ciudades)

# Filtrar por ciudad
df_ciudad = df[df["Ciudad"] == ciudad_seleccionada]

# Preparar datos
# 1. Más de 4 franjas por día
franjas_dia = df_ciudad.groupby(["Courier ID", "Día"]).size().reset_index(name="Nº Franjas Día")
df_mas_4_franjas = franjas_dia[franjas_dia["Nº Franjas Día"] > 4].sort_values(["Courier ID", "Día"])

# 2. Más de 6 días trabajados
dias_por_courier = df_ciudad.groupby("Courier ID")["Día"].nunique().reset_index(name="Días trabajados")
df_mas_6_dias = dias_por_courier[dias_por_courier["Días trabajados"] > 6].sort_values("Courier ID")

# Mostrar en dos columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Couriers con +4 franjas por día")
    if not df_mas_4_franjas.empty:
        st.dataframe(df_mas_4_franjas)
    else:
        st.info("Ningún courier tiene más de 4 franjas por día.")

with col2:
    st.subheader("📅 Couriers con +6 días trabajados")
    if not df_mas_6_dias.empty:
        st.dataframe(df_mas_6_dias)
    else:
        st.info("Ningún courier trabaja más de 6 días.")

