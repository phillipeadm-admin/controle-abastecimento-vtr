import streamlit as st
import pandas as pd
from datetime import datetime
import pytz  # Biblioteca para fuso horário
import google.generativeai as genai

# 1. CONFIGURAÇÃO DA INTELIGÊNCIA (AI STUDIO)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Configure a GOOGLE_API_KEY nos Secrets do Streamlit.")

# 2. SEUS CADASTROS (Menus Suspensos)
POLICIAIS = ["Sd Raquel", "Sd L. Dias", "Sgt Silva", "Ten Castro"]
EQUIPAMENTOS = ["Gerador QCG", "Gerador APMB", "Gerador 1BPM", "Viatura 01"]

# --- LÓGICA DO HORÁRIO DE BRASÍLIA ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M:%S")

# CONFIGURAÇÃO DO APP
st.set_page_config(page_title="Abastecimento VTR", layout="centered")
st.title("⛽ Sistema de Abastecimento")

tab1, tab2 = st.tabs(["📝 Registro", "📊 Dashboard"])

with tab1:
    st.subheader("Novo Lançamento")
    
    # Exibe o carimbo de Brasília automaticamente
    st.info(f"📅 Horário Oficial (Brasília): {agora_br}")

    with st.form("meu_formulario", clear_on_submit=True):
        policial_select = st.selectbox("Policial:", POLICIAIS)
        equip_select = st.selectbox("Equipamento:", EQUIPAMENTOS)
        litros_input = st.number_input("Litros:", min_value=0.0, step=0.1)
        foto_input = st.camera_input("Foto do Cupom")
        
        enviar = st.form_submit_button("Salvar Registro")
        
        if enviar:
            # Aqui usamos o 'agora_br' para garantir que o registro salvo seja preciso
            st.success(f"Registrado em {agora_br}: {policial_select} - {litros_input}L no {equip_select}")
            st.balloons()

with tab2:
    st.subheader("Painel de Controle")
    dados_grafico = pd.DataFrame({
        'Equipamento': EQUIPAMENTOS,
        'Litros': [45, 65, 27, 180] 
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
