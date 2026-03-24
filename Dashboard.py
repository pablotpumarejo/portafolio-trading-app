# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 13:07:51 2026

@author: pablo
"""
import streamlit as st
import yfinance as yf # <-- NUESTRO NUEVO MOTOR SIN LÍMITES
import pandas as pd
from io import BytesIO
import datetime
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Terminal Cuantitativa Pro", layout="wide")
st.title("📈 Terminal de Análisis Algorítmico")
st.markdown("Plataforma interactiva impulsada por **Yahoo Finance** (Sin límites de API ni bloqueos).")

# ==========================================
# 2. MENÚ LATERAL (Sin API Keys)
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
# Agregamos un botón para que no se recargue solo a cada rato
if st.sidebar.button("🚀 Extraer Datos de Wall Street"):
    with st.spinner(f"Conectando con Yahoo Finance para extraer {simbolo}..."):
        try:
            # Magia pura: yfinance descarga todo en una sola línea de código
            ticker = yf.Ticker(simbolo)
            # Le sumamos 1 día a la fecha final para asegurar que incluya el día de hoy
            df = ticker.history(start=fecha_inicio, end=fecha_fin + datetime.timedelta(days=1))

            if not df.empty:
                # Limpiamos la zona horaria para evitar problemas con las gráficas
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
                # 5. NOTICIAS EN TIEMPO REAL (De Yahoo Finance)
                # ==========================================
                st.divider()
                st.subheader("📰 Noticias Recientes")
                noticias = ticker.news
                if noticias:
                    for noticia in noticias[:3]:
                        titulo = noticia.get('title', 'Sin título')
                        enlace = noticia.get('link', '#')
                        editor = noticia.get('publisher', 'Desconocido')
                        
                        st.markdown(f"**[{titulo}]({enlace})**")
                        st.caption(f"Fuente: {editor}")
                        st.write("---")
                else:
                    st.info("ℹ️ No hay noticias recientes para mostrar.")

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