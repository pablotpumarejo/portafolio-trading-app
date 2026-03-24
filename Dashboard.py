# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 13:07:51 2026

@author: pablo
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
from io import BytesIO
import datetime # <-- NUEVA HERRAMIENTA PARA EL CALENDARIO

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA WEB
# ==========================================
st.set_page_config(page_title="Terminal Cuantitativa", layout="wide")
st.title("📈 Terminal de Análisis Algorítmico")
st.markdown("Plataforma interactiva para detección de señales de compra/venta.")

# ==========================================
# 2. MENÚ LATERAL INTERACTIVO (Con Calendario)
# ==========================================
st.sidebar.header("⚙️ Configuración del Motor")
API_KEY = st.sidebar.text_input("Ingresa tu API Key de Alpha Vantage:", type="password")
simbolo = st.sidebar.selectbox("Selecciona la Empresa a analizar:", ["AAPL", "MSFT", "TSLA", "AMZN", "GOOGL"])

st.sidebar.divider()
st.sidebar.subheader("📅 Rango de Análisis")
# Creamos dos selectores de fecha en el menú lateral
fecha_inicio = st.sidebar.date_input("Fecha de inicio", datetime.date(2025, 1, 1))
fecha_fin = st.sidebar.date_input("Fecha de fin", datetime.date.today())

# ==========================================
# 3. EJECUCIÓN DEL MOTOR
# ==========================================
if API_KEY:
    with st.spinner(f"Extrayendo historial completo de {simbolo}..."):
        # NUEVO: Agregamos '&outputsize=full' a la URL para pedir toda la historia
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={simbolo}&apikey={API_KEY}&outputsize=full'
        respuesta = requests.get(url)
        datos_crudos = respuesta.json()

        if 'Time Series (Daily)' in datos_crudos:
            series_diarias = datos_crudos['Time Series (Daily)']
            df = pd.DataFrame.from_dict(series_diarias, orient='index')
            df.columns = ['Apertura', 'Maximo', 'Minimo', 'Cierre', 'Volumen']
            
            # Convertimos el índice (las fechas) a formato de tiempo real para poder filtrarlas
            df.index = pd.to_datetime(df.index)
            df['Cierre'] = df['Cierre'].astype(float)
            df['Volumen'] = df['Volumen'].astype(float)
            df = df.iloc[::-1]

            # ==========================================
            # FILTRO DE FECHAS MAESTRO
            # ==========================================
            # Recortamos la tabla para que solo muestre las fechas que eligió el usuario
            mascara = (df.index.date >= fecha_inicio) & (df.index.date <= fecha_fin)
            df = df.loc[mascara]

            # El Cerebro Cuantitativo (Se calcula sobre las fechas filtradas)
            df['Media_Rapida_7d'] = df['Cierre'].rolling(window=7).mean()
            df['Media_Lenta_21d'] = df['Cierre'].rolling(window=21).mean()
            df['Tendencia'] = np.where(df['Media_Rapida_7d'] > df['Media_Lenta_21d'], 1, 0)
            df['Señal'] = df['Tendencia'].diff()

            # ==========================================
            # 4. LA CARA VISUAL
            # ==========================================
            st.divider()
            if not df.empty:
                precio_actual = df['Cierre'].iloc[-1]
                precio_ayer = df['Cierre'].iloc[-2] if len(df) > 1 else precio_actual
                variacion = precio_actual - precio_ayer
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Precio Actual en el Periodo", f"${precio_actual:.2f}", f"{variacion:.2f} USD vs día anterior")
                
                ultimas_senales = df[df['Señal'] != 0].dropna()
                if not ultimas_senales.empty:
                    ultima_senal = ultimas_senales.iloc[-1]
                    tipo_senal = "COMPRA ✅" if ultima_senal['Señal'] == 1.0 else "VENTA ⚠️"
                    col2.metric("Última Señal en este Rango", tipo_senal, str(ultimas_senales.index[-1].date()))
                
                st.subheader(f"📊 Comportamiento de {simbolo}")
                st.line_chart(df[['Cierre', 'Media_Rapida_7d', 'Media_Lenta_21d']])

                st.subheader("📊 Volumen de Transacciones Diarias")
                st.bar_chart(df['Volumen'], color="#FF4B4B")

                # Botón de Descarga
                st.divider()
                st.subheader("💾 Exportar Información")
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=f'Reporte_{simbolo}')
                
                st.download_button(
                    label=f"📥 Descargar Excel de {simbolo} (Periodo seleccionado)",
                    data=buffer.getvalue(),
                    file_name=f"Reporte_{simbolo}_Filtrado.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                st.warning("No hay datos para este rango de fechas. Intenta ampliar el calendario.")
        else:
            st.error("❌ Error de conexión. Revisa tu API Key o el límite de velocidad.")
else:
    st.warning("👈 Por favor, ingresa tu API Key para arrancar el motor.")