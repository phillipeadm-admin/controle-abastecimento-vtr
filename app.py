import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import google.generativeai as genai
from streamlit_js_eval import streamlit_js_eval
import os

# 1. CONFIGURAÇÃO DA INTELIGÊNCIA (AI STUDIO)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Erro na Chave API. Verifique os Secrets do Streamlit.")

# 2. LISTAS OFICIAIS
POLICIAIS = ["Selecione o Policial..."] + ["ST J. CARLOS", "SGT VALTER", "SGT JOSÉ LOPES", "SGT MARCOS PAULO", "SGT RODRIGUES", "SGT ADELSON", "SGT DANTAS", "SGT ELSON", "SGT JOSÉ", "SGT LEANDRO", "SGT MARCONI", "SGT MARCELO", "SGT CARVALHO", "SGT ANDERSON", "SGT NILTON", "SGT R. MARQUES", "CB ANDERSON", "CB ROBSON", "CB LUCIANO", "CB GOMES", "CB ISRAEL", "CB DOUGLAS", "CB C. LEITE", "SD RAQUEL", "SD L. DIAS", "SD CARLOS", "SD PEREIRA", "SD BRUNO"]
EQUIPAMENTOS = ["Selecione o Equipamento..."] + ["GERADOR QCG", "GERADOR APMB", "GERADOR 1º BPM", "GERADOR 2º BPM", "GERADOR 3º BPM", "GERADOR 4º BPM", "GERADOR 5º BPM", "GERADOR 6º BPM", "GERADOR 7º BPM", "GERADOR 8º BPM", "GERADOR 9º BPM", "GERADOR 10º BPM", "GERADOR 11º BPM", "GERADOR 12º BPM", "GERADOR 13º BPM", "GERADOR 14º BPM", "GERADOR 15º BPM", "GERADOR CMT GERAL", "GERADOR SUB CMT GERAL"]

# 3. LÓGICA DE PERSISTÊNCIA (BANCO DE DADOS)
DB_FILE = "abastecimentos.csv"

def salvar_dados(dados):
    df = pd.DataFrame([dados])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False, header=True)
    else:
        df.to_csv(DB_FILE, mode='a', index=False, header=False)

def carregar_dados():
    if os.path.isfile(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'], dayfirst=True, errors='coerce')
        return df.dropna(subset=['Data/Hora'])
    return pd.DataFrame(columns=["Data/Hora", "Policial", "Equipamento", "Litros", "Localizacao"])

# --- HORÁRIO E LOCALIZAÇÃO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso_br)
agora_str = agora.strftime("%d/%m/%Y %H:%M:%S")
