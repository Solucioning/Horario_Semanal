
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

st.title("📋 Consulta de Horarios de Couriers por Ciudad")

# Selección de ciudad
ciudades = sorted(df["Ciudad"].dropna().unique())
ciudad_seleccionada = st.selectbox("🌆 Selecciona una ciudad", ciudades)

# Filtrar datos por ciudad
df_ciudad = df[df["Ciudad"] == ciudad_seleccionada]

# 1. Couriers con más de 4 franjas en un mismo día
franjas_dia = df_ciudad.groupby(["Courier ID", "Día"]).size().reset_index(name="Nº Franjas Día")
df_mas_4_franjas = franjas_dia[franjas_dia["Nº Franjas Día"] > 4].sort_values(["Courier ID", "Día"])

st.subheader("📊 Couriers con más de 4 franjas por día")
if not df_mas_4_franjas.empty:
    st.dataframe(df_mas_4_franjas)
else:
    st.info("No hay couriers con más de 4 franjas en un día para esta ciudad.")

# 2. Couriers que trabajan más de 6 días diferentes
dias_por_courier = df_ciudad.groupby("Courier ID")["Día"].nunique().reset_index(name="Días trabajados")
df_mas_6_dias = dias_por_courier[dias_por_courier["Días trabajados"] > 6].sort_values("Courier ID")

st.subheader("📅 Couriers que trabajan más de 6 días")
if not df_mas_6_dias.empty:
    st.dataframe(df_mas_6_dias)
else:
    st.info("No hay couriers que trabajen más de 6 días diferentes en esta ciudad.")

