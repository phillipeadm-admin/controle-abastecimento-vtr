import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# 1. CONFIGURAÇÃO DA INTELIGÊNCIA (AI STUDIO)
# O Streamlit vai procurar a chave nos "Secrets" que configurou
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Erro: Chave API não configurada nos Secrets do Streamlit.")

# 2. CADASTROS DOS MENUS SUSPENSOS
# Edite estas listas para adicionar ou remover nomes e equipamentos
POLICIAIS = ["Sd Raquel", "Sd L. Dias", "Sgt Silva", "Ten Castro"]
EQUIPAMENTOS = ["Gerador QCG", "Gerador APMB", "Gerador 1BPM", "Viatura 01"]

# CONFIGURAÇÃO VISUAL DO APP
st.set_page_config(page_title="Controle de Abastecimento", page_icon="⛽")

st.title("⛽ Sistema de Abastecimento")

# Criar as abas: uma para o policial preencher e outra para o comando ver
tab1, tab2 = st.tabs(["📝 Registro de Campo", "📊 Painel de Controle"])

with tab1:
    st.subheader("Novo Lançamento")
    
    # CAMPO: Data e Hora Automática (Carimbo)
    carimbo_tempo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.info(f"📅 Registro em: {carimbo_tempo}")

    with st.form("form_abastecimento", clear_on_submit=True):
        # CAMPO: Menu Suspenso de Policiais
        nome_policial = st.selectbox("Selecione o Policial:", POLICIAIS)
        
        # CAMPO: Menu Suspenso de Equipamentos
        equipamento = st.selectbox("Selecione o Equipamento:", EQUIPAMENTOS)
        
        # CAMPO: Quantidade de Litros
        litros = st.number_input("Quantidade de Litros:", min_value=0.0, step=0.1)
        
        # CAMPO: Anexar Imagem (Ativa a câmera do telemóvel)
        foto = st.camera_input("Tirar foto do comprovante/bomba")
        
        submeter = st.form_submit_button("Salvar Registro")

        if submeter:
            if litros > 0:
                st.success(f"Registro de {nome_policial} salvo com sucesso!")
                st.balloons()
            else:
                st.warning("Por favor, insira a quantidade de litros.")

with tab2:
    st.subheader("Análise Inteligente")
    
    # Exemplo de Dashboard que o App gera
    st.write("Resumo de consumo por equipamento:")
    
    # Simulando dados para o gráfico (No futuro, isto lerá a sua planilha)
    dados_grafico
