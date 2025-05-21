
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Autenticación y conexión
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["GCP_SERVICE_ACCOUNT"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1zKh2Gc6zyA2BFZOfbr1G9aWd0n7-V0zVrq9R6eV3ZXI").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("📋 Gestión de Horarios de Couriers")

# Selección de ciudad
ciudades = sorted(df["Ciudad"].dropna().unique())
ciudad_seleccionada = st.selectbox("🌆 Selecciona una ciudad", ciudades)

# Filtro de couriers con más de 4 franjas por día en esa ciudad
df_filtrado = df[df["Ciudad"] == ciudad_seleccionada]
franjas_dia = df_filtrado.groupby(["Courier ID", "Día"]).size().reset_index(name="Nº Franjas Día")
df_franjas_dia = franjas_dia[franjas_dia["Nº Franjas Día"] > 4].sort_values(["Courier ID", "Día"])

st.subheader(f"📊 Couriers con más de 4 franjas por día en {ciudad_seleccionada}")
if not df_franjas_dia.empty:
    st.dataframe(df_franjas_dia)
else:
    st.info("Ningún courier tiene más de 4 franjas por día en esta ciudad.")

# Consultar y editar un courier específico
st.divider()
st.header("🔍 Revisar y editar horarios por Courier")

courier_id = st.text_input("Introduce el Courier ID para revisar o editar", placeholder="Ej: 198085585")

if courier_id:
    try:
        courier_id_int = int(courier_id)
        df_courier = df[df["Courier ID"] == courier_id_int]

        if df_courier.empty:
            st.warning("No se encontraron franjas para este Courier.")
        else:
            st.success(f"{len(df_courier)} franjas encontradas.")
            edited_df = st.data_editor(df_courier, num_rows="dynamic")

            if st.button("💾 Guardar Cambios"):
                df_updated = df[df["Courier ID"] != courier_id_int]
                df_final = pd.concat([df_updated, edited_df], ignore_index=True)
                sheet.clear()
                sheet.update([df_final.columns.values.tolist()] + df_final.values.tolist())
                st.success("Cambios guardados correctamente.")
    except ValueError:
        st.error("El Courier ID debe ser un número entero.")

# Agregar nueva franja
st.divider()
st.header("➕ Agregar nueva franja")

with st.form("add_form"):
    new_id = st.text_input("Courier ID", value=courier_id)
    new_city = st.text_input("Ciudad", value=ciudad_seleccionada)
    new_day = st.date_input("Día")
    new_start = st.text_input("Hora Inicio (HH:MM)")
    new_end = st.text_input("Hora Final (HH:MM)")
    submitted = st.form_submit_button("Agregar")

    if submitted:
        try:
            new_row = {
                "Courier ID": int(new_id),
                "Ciudad": new_city,
                "Día": str(new_day),
                "Hora Inicio": new_start,
                "Hora Final": new_end
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            sheet.clear()
            sheet.update([df.columns.values.tolist()] + df.values.tolist())
            st.success("Franja agregada correctamente.")
        except Exception as e:
            st.error(f"Error al agregar franja: {e}")
