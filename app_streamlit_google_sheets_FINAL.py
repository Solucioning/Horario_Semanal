import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configurar credenciales desde st.secrets (ya es dict)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["GCP_SERVICE_ACCOUNT"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Acceder a la hoja
sheet = client.open_by_key("1zKh2Gc6zyA2BFZOfbr1G9aWd0n7-V0zVrq9R6eV3ZXI").sheet1

# Cargar datos
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("📋 App Horarios Couriers (Google Sheets)")

# Buscar por Courier ID
courier_id = st.text_input("🔎 Buscar Courier ID", placeholder="Ej: 198085584")

if courier_id:
    try:
        courier_id_int = int(courier_id)
        df_courier = df[df["Courier ID"] == courier_id_int]

        if df_courier.empty:
            st.warning("No se encontraron franjas.")
        else:
            st.success(f"{len(df_courier)} franjas encontradas.")
            edited_df = st.data_editor(df_courier, num_rows="dynamic")

            if st.button("💾 Guardar Cambios"):
                df_updated = df[df["Courier ID"] != courier_id_int]
                df_final = pd.concat([df_updated, edited_df], ignore_index=True)
                sheet.clear()
                sheet.update([df_final.columns.values.tolist()] + df_final.values.tolist())
                st.success("Cambios guardados en Google Sheets.")

    except ValueError:
        st.error("Courier ID inválido. Debe ser un número.")

# Agregar nueva franja
st.divider()
st.header("➕ Agregar nueva franja")

with st.form("add_form"):
    new_id = st.text_input("Courier ID", value=courier_id)
    new_city = st.text_input("Ciudad")
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
