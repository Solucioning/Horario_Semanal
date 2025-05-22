
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

st.title("📋 Consulta de Horarios de Couriers")

# Selección de ciudad
ciudades = sorted(df["Ciudad"].dropna().unique())
ciudad_seleccionada = st.selectbox("🌆 Selecciona una ciudad", ciudades)

# Filtro: couriers con más de 4 franjas por día en esa ciudad
df_filtrado = df[df["Ciudad"] == ciudad_seleccionada]
franjas_dia = df_filtrado.groupby(["Courier ID", "Día"]).size().reset_index(name="Nº Franjas Día")
df_franjas_dia = franjas_dia[franjas_dia["Nº Franjas Día"] > 4].sort_values(["Courier ID", "Día"])

st.subheader(f"📊 Couriers con más de 4 franjas por día en {ciudad_seleccionada}")
if not df_franjas_dia.empty:
    st.dataframe(df_franjas_dia)
else:
    st.info("Ningún courier tiene más de 4 franjas por día en esta ciudad.")

# Consultar un Courier específico y recuento de días trabajados
st.divider()
st.header("🔍 Revisar horarios y días trabajados por Courier")

courier_id = st.text_input("Introduce el Courier ID", placeholder="Ej: 198085584")

if courier_id:
    try:
        courier_id_int = int(courier_id)
        df_courier = df[(df["Courier ID"] == courier_id_int) & (df["Ciudad"] == ciudad_seleccionada)]

        if df_courier.empty:
            st.warning("No se encontraron franjas para este Courier en esa ciudad.")
        else:
            dias_trabajados = df_courier["Día"].nunique()
            st.info(f"🗓 Este courier tiene {dias_trabajados} días diferentes trabajados.")

            if dias_trabajados > 6:
                st.error("⚠️ Este courier trabaja más de 6 días diferentes.")

            st.subheader("📅 Franjas asignadas:")
            st.dataframe(df_courier.sort_values(["Día", "Hora Inicio"]))
    except ValueError:
        st.error("El Courier ID debe ser un número entero.")

