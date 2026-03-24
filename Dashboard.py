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
import datetime
import plotly.graph_objects as go # Librería para las velas interactivas

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Terminal Cuantitativa Pro", layout="wide")
st.title("📈 Terminal de Análisis Algorítmico y Sentimiento")
st.markdown("Plataforma interactiva con Velas Japonesas y Análisis de Noticias.")

# ==========================================
# 2. MENÚ LATERAL INTERACTIVO
# ==========================================
st.sidebar.header("⚙️ Configuración del Motor")
API_KEY = st.sidebar.text_input("Ingresa tu API Key de Alpha Vantage:", type="password")
simbolo = st.sidebar.selectbox("Selecciona la Empresa:", ["AAPL", "MSFT", "TSLA", "AMZN", "GOOGL"])

st.sidebar.divider()
st.sidebar.subheader("📅 Rango de Análisis")
# Definimos el rango de fechas (por defecto los últimos 3 meses)
fecha_inicio = st.sidebar.date_input("Fecha de inicio", datetime.date(2025, 1, 1))
fecha_fin = st.sidebar.date_input("Fecha de fin", datetime.date.today())

# ==========================================
# 3. EJECUCIÓN DEL MOTOR PRINCIPAL
# ==========================================
if API_KEY:
    with st.spinner(f"Conectando con Wall Street para extraer {simbolo}..."):
        # LLAMADA 1: Datos de Precios
        url_precios = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={simbolo}&apikey={API_KEY}&outputsize=full'
        res_precios = requests.get(url_precios)
        datos_crudos = res_precios.json()

        if 'Time Series (Daily)' in datos_crudos:
            # --- TRANSFORMACIÓN DE DATOS ---
            series_diarias = datos_crudos['Time Series (Daily)']
            df = pd.DataFrame.from_dict(series_diarias, orient='index')
            df.columns = ['Apertura', 'Maximo', 'Minimo', 'Cierre', 'Volumen']
            df.index = pd.to_datetime(df.index)
            
            # Convertir a números reales
            for col in df.columns:
                df[col] = df[col].astype(float)
            
            # Ordenar por fecha (antiguo a reciente)
            df = df.sort_index()

            # --- FILTRO DE FECHAS ---
            mascara = (df.index.date >= fecha_inicio) & (df.index.date <= fecha_fin)
            df = df.loc[mascara]

            if not df.empty:
                # ==========================================
                # 4. VISUALIZACIÓN: MÉTRICAS Y VELAS
                # ==========================================
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                precio_actual = df['Cierre'].iloc[-1]
                precio_ayer = df['Cierre'].iloc[-2] if len(df) > 1 else precio_actual
                variacion = precio_actual - precio_ayer
                
                col1.metric("Precio de Cierre", f"${precio_actual:.2f}", f"{variacion:.2f} USD")
                col2.metric("Volumen Diario", f"{df['Volumen'].iloc[-1]:,.0f}")
                col3.write("💡 *Usa el mouse para hacer zoom en la gráfica*")

                # GRÁFICO INTERACTIVO (PLOTLY)
                st.subheader(f"🕯️ Gráfico de Velas Japonesas - {simbolo}")
                fig = go.Figure(data=[go.Candlestick(
                    x=df.index,
                    open=df['Apertura'],
                    high=df['Maximo'],
                    low=df['Minimo'],
                    close=df['Cierre'],
                    name="Precio"
                )])
                
                fig.update_layout(xaxis_title="Fecha", yaxis_title="Precio (USD)", template="plotly_dark", height=500)
                st.plotly_chart(fig, use_container_width=True)

                # ==========================================
                # 5. MOTOR DE NOTICIAS CON ESCUDO PROTECTOR
                # ==========================================
                st.divider()
                st.subheader("📰 Noticias Recientes y Sentimiento")
                
                try:
                    # Hacemos la petición de noticias
                    url_noticias = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={simbolo}&apikey={API_KEY}&limit=3'
                    res_noticias = requests.get(url_noticias)
                    datos_noticias = res_noticias.json()
                    
                    if 'feed' in datos_noticias and datos_noticias['feed']:
                        for noticia in datos_noticias['feed'][:3]:
                            sentimiento = noticia['overall_sentiment_label']
                            # Emoji dinámico
                            emoji = "🟢" if "Bullish" in sentimiento else "🔴" if "Bearish" in sentimiento else "⚪"
                            
                            st.markdown(f"**[{noticia['title']}]({noticia['url']})**")
                            st.caption(f"Sentimiento IA: {emoji} {sentimiento}")
                            st.write("---")
                    else:
                        st.info("ℹ️ No hay noticias disponibles en este momento (Límite de API alcanzado).")
                except:
                    st.info("ℹ️ El motor de noticias está descansando para no saturar la API. Las gráficas siguen activas.")

                # ==========================================
                # 6. EXPORTACIÓN A EXCEL
                # ==========================================
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=f'Reporte_{simbolo}')
                
                st.download_button(
                    label=f"📥 Descargar Datos de {simbolo} en Excel",
                    data=buffer.getvalue(),
                    file_name=f"Reporte_{simbolo}.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                st.warning("No hay datos para las fechas seleccionadas. Ajusta el calendario en el menú lateral.")
        else:
            st.error("❌ Error: No se pudieron obtener los datos. Verifica tu API Key o espera 1 minuto.")
else:
    st.warning("👈 Por favor, ingresa tu API Key en el menú de la izquierda para arrancar.")