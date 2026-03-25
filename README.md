# 📈 Terminal Cuantitativa Pro & Oráculo Predictivo (Machine Learning)

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Live-red.svg)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-orange.svg)
![Finance](https://img.shields.io/badge/Finance-YFinance-green.svg)

## 📌 Visión General
Este proyecto es una aplicación web interactiva diseñada para la extracción, visualización y análisis predictivo de activos financieros en tiempo real. 

A diferencia de los dashboards tradicionales que solo reportan datos históricos, esta terminal integra un **Motor de Inteligencia Artificial** basado en Machine Learning para proyectar el comportamiento a corto plazo del mercado, demostrando capacidades de *Feature Engineering* y análisis cuantitativo.

## 🚀 Características Principales

* **📊 Extracción de Datos sin Límites:** Conexión directa a la API de Yahoo Finance (`yfinance`) para descargar históricos de precios y volúmenes sin restricciones de peticiones diarias.
* **🤖 Oráculo Predictivo (Machine Learning):** Implementación de un modelo de **Random Forest Classifier** (`scikit-learn`) entrenado en tiempo real. El modelo evalúa la inercia del mercado (medias móviles de 2 y 5 días) para emitir un veredicto direccional (Alcista/Bajista) para la siguiente jornada.
* **🕯️ Visualización Interactiva:** Gráficos de Velas Japonesas (Candlesticks) generados con `Plotly` para un análisis técnico profundo.
* **📰 Flujo de Noticias en Vivo:** Web scraping ético y automatizado utilizando el feed RSS oficial de Wall Street, integrando cabeceras (`User-Agent`) para evitar bloqueos de servidor.
* **📥 Exportación de Datos:** Generación dinámica de reportes en Excel (`pandas` + `openpyxl`) para análisis secundario.

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python
* **Frontend / Deployment:** Streamlit (Cloud)
* **Manipulación de Datos:** Pandas
* **Machine Learning:** Scikit-Learn
* **Visualización:** Plotly
* **Ingeniería de Datos:** YFinance, Requests, XML ElementTree

## 🧠 Lógica del Modelo Predictivo (El Oráculo)
El modelo de Machine Learning fue diseñado con un enfoque de *Momentum Trading* (Corto Plazo). 
1. **Target:** Predecir si el precio de cierre de mañana será mayor al de hoy (Clasificación Binaria).
2. **Feature Engineering:** Se construyeron variables financieras sintéticas (`Ratio_Cierre_2` y `Ratio_Cierre_5`) para enseñarle al algoritmo a identificar el impulso inmediato del precio respecto a sus medias móviles recientes, evitando el "ruido" macroeconómico a largo plazo.
3. **Algoritmo:** Un ensamble de 100 árboles de decisión (`n_estimators=100`) para reducir la varianza y evitar el sobreajuste (overfitting).

## 💡 Valor de Negocio
Este proyecto demuestra la capacidad de transformar datos crudos y dispersos de la web en un producto de datos consumible, automatizado y orientado a la toma de decisiones estratégicas mediante el uso de Inteligencia Artificial.
