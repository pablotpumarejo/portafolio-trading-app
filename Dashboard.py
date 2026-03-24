# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 13:07:51 2026

@author: pablo
"""
import streamlit as st
import yfinance as yf
import pandas as pd
from io import BytesIO
import datetime
import plotly.graph_objects as go
import requests
import xml.etree.ElementTree as ET

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Terminal Cuantitativa Pro", layout="wide")
st.title("📈 Terminal de Análisis Algorítmico")
st.markdown("Plataforma interactiva impulsada por **Yahoo Finance** (Sin límites de API ni bloqueos).")

# ==========================================
# 2. MENÚ LATERAL
# ==========================================
st.sidebar.header("⚙️ Configuración del Motor")
simbolo = st.sidebar.selectbox("Selecciona la Empresa:", ["AAPL", "MSFT", "TSLA", "AMZN", "GOOG"])

st.sidebar.divider()
st.sidebar.subheader("📅 Rango de Análisis")
fecha_inicio = st.sidebar.date_input("Fecha de inicio", datetime.date(2025, 1, 1))
fecha_fin = st.sidebar.date_input("Fecha de fin", datetime.date.today())

# ==========================================
# 3. EJECUCIÓN DEL MOTOR (YFINANCE)
# ==========================================
if st.sidebar.button("🚀 Extraer Datos de Wall Street"):
    with st.spinner(f"Conectando con Yahoo Finance para extraer {simbolo}..."):
        try:
            # Extracción de precios sin límites
            ticker = yf.Ticker(simbolo)
            df = ticker.history(start=fecha_inicio, end=fecha_fin + datetime.timedelta(days=1))

            if not df.empty:
                # Limpiamos la zona horaria
                df.index = df.index.tz_localize(None)
                
                # ==========================================
                # 4. VISUALIZACIÓN: MÉTRICAS Y VELAS
                # ==========================================
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                precio_actual = df['Close'].iloc[-1]
                precio_ayer = df['Close'].iloc[-2] if len(df) > 1 else precio_actual
                variacion = precio_actual - precio_ayer
                
                col1.metric("Precio de Cierre", f"${precio_actual:.2f}", f"{variacion:.2f} USD")
                col2.metric("Volumen Diario", f"{df['Volume'].iloc[-1]:,.0f}")
                col3.write("💡 *Conexión directa: Sin límites de peticiones.*")

                # GRÁFICO INTERACTIVO (PLOTLY)
                st.subheader(f"🕯️ Gráfico de Velas Japonesas - {simbolo}")
                fig = go.Figure(data=[go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name="Precio"
                )])
                
                fig.update_layout(xaxis_title="Fecha", yaxis_title="Precio (USD)", template="plotly_dark", height=500)
                st.plotly_chart(fig, use_container_width=True)

                # ==========================================
                # 5. NOTICIAS EN TIEMPO REAL (Vía RSS Oficial)
                # ==========================================
                st.divider()
                st.subheader("📰 Noticias Recientes")
                
                try:
                    url_rss = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={simbolo}&region=US&lang=en-US"
                    cabeceras = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    respuesta_rss = requests.get(url_rss, headers=cabeceras)
                    
                    raiz = ET.fromstring(respuesta_rss.text)
                    noticias_encontradas = raiz.findall('./channel/item')
                    
                    if noticias_encontradas:
                        for noticia in noticias_encontradas[:3]:
                            titulo = noticia.find('title').text
                            enlace = noticia.find('link').text
                            fecha_pub = noticia.find('pubDate').text
                            
                            st.markdown(f"**[{titulo}]({enlace})**")
                            st.caption(f"📅 Publicado: {fecha_pub}")
                            st.write("---")
                    else:
                        st.info("ℹ️ No hay noticias recientes para esta empresa.")
                except Exception as e:
                    st.warning("El muro de noticias está temporalmente en mantenimiento.")

                # ==========================================
                # 6. EXPORTACIÓN A EXCEL
                # ==========================================
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=f'Reporte_{simbolo}')
                
                st.download_button(
                    label=f"📥 Descargar Datos en Excel",
                    data=buffer.getvalue(),
                    file_name=f"Reporte_{simbolo}_YF.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                st.warning("No hay datos para las fechas seleccionadas. Ajusta el calendario.")
        except Exception as e:
            st.error(f"❌ Error al conectar con Yahoo Finance: {e}")
else:
    st.info("👈 Selecciona la empresa, ajusta las fechas y presiona 'Extraer Datos' en el menú lateral.")