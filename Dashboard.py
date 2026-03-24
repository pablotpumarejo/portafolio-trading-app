# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 13:07:51 2026

@author: pablo
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
from io import BytesIO # <-- Herramienta para crear el Excel descargable

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA WEB
# ==========================================
st.set_page_config(page_title="Terminal Cuantitativa", layout="wide")
st.title("📈 Terminal de Análisis Algorítmico")
st.markdown("Plataforma interactiva para detección de señales de compra/venta y exportación de datos.")

# ==========================================
# 2. MENÚ LATERAL INTERACTIVO
# ==========================================
st.sidebar.header("⚙️ Configuración del Motor")
API_KEY = st.sidebar.text_input("Ingresa tu API Key de Alpha Vantage:", type="password")
simbolo = st.sidebar.selectbox("Selecciona la Empresa a analizar:", ["AAPL", "MSFT", "TSLA", "AMZN", "GOOGL"])

# ==========================================
# 3. EJECUCIÓN DEL MOTOR
# ==========================================
if API_KEY:
    with st.spinner(f"Conectando a Wall Street para extraer {simbolo}..."):
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={simbolo}&apikey={API_KEY}'
        respuesta = requests.get(url)
        datos_crudos = respuesta.json()

        if 'Time Series (Daily)' in datos_crudos:
            # Transformación
            series_diarias = datos_crudos['Time Series (Daily)']
            df = pd.DataFrame.from_dict(series_diarias, orient='index')
            df.columns = ['Apertura', 'Maximo', 'Minimo', 'Cierre', 'Volumen']
            df.index.name = 'Fecha'
            
            # Convertimos a números para poder operar y graficar
            df['Cierre'] = df['Cierre'].astype(float)
            df['Volumen'] = df['Volumen'].astype(float)
            df = df.iloc[::-1]

            # El Cerebro Cuantitativo
            df['Media_Rapida_7d'] = df['Cierre'].rolling(window=7).mean()
            df['Media_Lenta_21d'] = df['Cierre'].rolling(window=21).mean()
            df['Tendencia'] = np.where(df['Media_Rapida_7d'] > df['Media_Lenta_21d'], 1, 0)
            df['Señal'] = df['Tendencia'].diff()

            # ==========================================
            # 4. LA CARA VISUAL (Métricas y Gráficas)
            # ==========================================
            st.divider()
            
            # Fila de Métricas Principales
            precio_actual = df['Cierre'].iloc[-1]
            precio_ayer = df['Cierre'].iloc[-2]
            variacion = precio_actual - precio_ayer
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Precio Actual de Cierre", f"${precio_actual:.2f}", f"{variacion:.2f} USD vs ayer")
            
            ultimas_senales = df[df['Señal'] != 0].dropna()
            if not ultimas_senales.empty:
                ultima_senal = ultimas_senales.iloc[-1]
                tipo_senal = "COMPRA ✅" if ultima_senal['Señal'] == 1.0 else "VENTA ⚠️"
                fecha_senal = str(ultimas_senales.index[-1])
                col2.metric("Última Señal Detectada", tipo_senal, fecha_senal)
            
            # Gráfica Principal (Precios)
            st.subheader(f"📊 Comportamiento y Medias Móviles de {simbolo}")
            st.line_chart(df[['Cierre', 'Media_Rapida_7d', 'Media_Lenta_21d']])

            # NUEVO: Gráfica de Volumen Inferior
            st.subheader("📊 Volumen de Transacciones Diarias")
            st.bar_chart(df['Volumen'], color="#FF4B4B")

            # NUEVO: Botón de Descarga de Excel
            st.divider()
            st.subheader("💾 Exportar Información")
            st.markdown("Descarga la base de datos completa con los cálculos de medias móviles y señales ya integrados.")
            
            # Magia para crear el Excel en la memoria web
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=f'Reporte_{simbolo}')
            
            st.download_button(
                label="📥 Descargar Reporte en Excel",
                data=buffer.getvalue(),
                file_name=f"Reporte_Cuantitativo_{simbolo}.xlsx",
                mime="application/vnd.ms-excel"
            )

        else:
            st.error("❌ Error de conexión. Revisa tu API Key o el límite de velocidad del servidor.")
else:
    st.warning("👈 Por favor, ingresa tu API Key en el menú de la izquierda para arrancar el motor.")