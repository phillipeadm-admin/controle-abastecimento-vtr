import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import google.generativeai as genai
from streamlit_js_eval import streamlit_js_eval # Componente de localização

# 1. CONFIGURAÇÃO DA INTELIGÊNCIA (AI STUDIO)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Configure a GOOGLE_API_KEY nos Secrets do Streamlit.")

# 2. LISTAS OFICIAIS (POLICIAIS E EQUIPAMENTOS)
POLICIAIS = ["ST J. CARLOS", "SGT VALTER", "SGT JOSÉ LOPES", "SGT MARCOS PAULO", "SGT RODRIGUES", "SGT ADELSON", "SGT DANTAS", "SGT ELSON", "SGT JOSÉ", "SGT LEANDRO", "SGT MARCONI", "SGT MARCELO", "SGT CARVALHO", "SGT ANDERSON", "SGT NILTON", "SGT R. MARQUES", "CB ANDERSON", "CB ROBSON", "CB LUCIANO", "CB GOMES", "CB ISRAEL", "CB DOUGLAS", "CB C. LEITE", "SD RAQUEL", "SD L. DIAS", "SD CARLOS", "SD PEREIRA", "SD BRUNO"]
EQUIPAMENTOS = ["GERADOR QCG", "GERADOR APMB", "GERADOR 1º BPM", "GERADOR 2º BPM", "GERADOR 3º BPM", "GERADOR 4º BPM", "GERADOR 5º BPM", "GERADOR 6º BPM", "GERADOR 7º BPM", "GERADOR 8º BPM", "GERADOR 9º BPM", "GERADOR 10º BPM", "GERADOR 11º BPM", "GERADOR 12º BPM", "GERADOR 13º BPM", "GERADOR 14º BPM", "GERADOR 15º BPM", "GERADOR CMT GERAL", "GERADOR SUB CMT GERAL"]

# --- LÓGICA DO HORÁRIO E LOCALIZAÇÃO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M:%S")

# Captura a localização via navegador
loc = streamlit_js_eval(js_expressions="screen.width", key="L1") # Força atualização
pos_json = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(success => { return {lat: success.coords.latitude, lon: success.coords.longitude} })", key="L2")

st.set_page_config(page_title="Abastecimento VTR", layout="centered")
st.title("⛽ Sistema de Abastecimento")

tab1, tab2 = st.tabs(["📝 Registro", "📊 Dashboard"])

with tab1:
    st.subheader("Novo Lançamento")
    st.info(f"📅 Horário: {agora_br}")
    
    # Exibe se a localização foi capturada
    if pos_json:
        st.success(f"📍 Localização capturada com sucesso!")
    else:
        st.warning("📍 Aguardando sinal de GPS (Certifique-se que o GPS está ligado).")

    with st.form("meu_formulario", clear_on_submit=True):
        policial_select = st.selectbox("Selecione o Policial:", POLICIAIS)
        equip_select = st.selectbox("Selecione o Equipamento:", EQUIPAMENTOS)
        litros_input = st.number_input("Quantidade de Litros:", min_value=0.0, step=0.1)
        foto_input = st.camera_input("Foto do Comprovante")
        
        enviar = st.form_submit_button("Salvar Registro")
        
        if enviar:
            loc_str = f"{pos_json['lat']}, {pos_json['lon']}" if pos_json else "Não capturada"
            st.success(f"Registrado! Policial: {policial_select} | Localização: {loc_str}")
            st.balloons()
