import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# 1. CONFIGURAÇÃO DA INTELIGÊNCIA (AI STUDIO)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Configure a GOOGLE_API_KEY nos Secrets do Streamlit.")

# 2. SEUS CADASTROS (Menus Suspensos)
POLICIAIS = ["Sd Raquel", "Sd L. Dias", "Sgt Airton", "Sgt Araujo","Sgt Rondinele","Sgt Vaz"]
EQUIPAMENTOS = ["Gerador QCG", "Gerador APMB", "Gerador 1BPM", "Viatura 01"]

# CONFIGURAÇÃO DO APP
st.set_page_config(page_title="Abastecimento VTR", layout="centered")
st.title("⛽ Sistema de Abastecimento")

tab1, tab2 = st.tabs(["📝 Registro", "📊 Dashboard"])

with tab1:
    st.subheader("Novo Lançamento")
    
    # Carimbo de data/hora automático
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.info(f"📅 Data/Hora: {agora}")

    with st.form("meu_formulario", clear_on_submit=True):
        policial_select = st.selectbox("Policial:", POLICIAIS)
        equip_select = st.selectbox("Equipamento:", EQUIPAMENTOS)
        litros_input = st.number_input("Litros:", min_value=0.0, step=0.1)
        foto_input = st.camera_input("Foto do Cupom")
        
        enviar = st.form_submit_button("Salvar Registro")
        
        if enviar:
            st.success(f"Registrado: {policial_select} - {litros_input}L no {equip_select}")
            st.balloons()

with tab2:
    st.subheader("Painel de Controle")
    
    # Criando os dados para o gráfico (Evita o NameError)
    dados_grafico = pd.DataFrame({
        'Equipamento': EQUIPAMENTOS,
        'Litros': [45, 65, 27, 180] # Valores de exemplo
    })
    
    st.bar_chart(data=dados_grafico, x='Equipamento', y='Litros')

    if st.button("Analisar com IA"):
        prompt = f"Analise estes abastecimentos: {dados_grafico.to_string()}"
        try:
            res = model.generate_content(prompt)
            st.write("🤖 **IA Studio:**")
            st.write(res.text)
        except:
            st.write("IA indisponível no momento.")
