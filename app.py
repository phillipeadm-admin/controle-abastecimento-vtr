import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import google.generativeai as genai
from streamlit_js_eval import streamlit_js_eval

# 1. CONFIGURAÇÃO DA INTELIGÊNCIA (AI STUDIO)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Erro: Configure a GOOGLE_API_KEY nos Secrets do Streamlit.")

# 2. LISTAS OFICIAIS (POLICIAIS E EQUIPAMENTOS)
# Adicionei uma opção vazia no início para forçar a seleção
POLICIAIS = ["Selecione o Policial..."] + ["ST J. CARLOS", "SGT VALTER", "SGT JOSÉ LOPES", "SGT MARCOS PAULO", "SGT RODRIGUES", "SGT ADELSON", "SGT DANTAS", "SGT ELSON", "SGT JOSÉ", "SGT LEANDRO", "SGT MARCONI", "SGT MARCELO", "SGT CARVALHO", "SGT ANDERSON", "SGT NILTON", "SGT R. MARQUES", "CB ANDERSON", "CB ROBSON", "CB LUCIANO", "CB GOMES", "CB ISRAEL", "CB DOUGLAS", "CB C. LEITE", "SD RAQUEL", "SD L. DIAS", "SD CARLOS", "SD PEREIRA", "SD BRUNO"]
EQUIPAMENTOS = ["Selecione o Equipamento..."] + ["GERADOR QCG", "GERADOR APMB", "GERADOR 1º BPM", "GERADOR 2º BPM", "GERADOR 3º BPM", "GERADOR 4º BPM", "GERADOR 5º BPM", "GERADOR 6º BPM", "GERADOR 7º BPM", "GERADOR 8º BPM", "GERADOR 9º BPM", "GERADOR 10º BPM", "GERADOR 11º BPM", "GERADOR 12º BPM", "GERADOR 13º BPM", "GERADOR 14º BPM", "GERADOR 15º BPM", "GERADOR CMT GERAL", "GERADOR SUB CMT GERAL"]

# --- LÓGICA DO HORÁRIO E LOCALIZAÇÃO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M:%S")

# Captura de Localização (GPS)
pos_json = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(success => { return {lat: success.coords.latitude, lon: success.coords.longitude} })", key="geo_location")

st.set_page_config(page_title="Abastecimento VTR", layout="centered")
st.title("⛽ Sistema de Abastecimento")

tab1, tab2 = st.tabs(["📝 Registro", "📊 Dashboard"])

with tab1:
    st.subheader("Novo Lançamento")
    st.info(f"📅 Horário Oficial (Brasília): {agora_br}")
    
    with st.form("meu_formulario", clear_on_submit=True):
        # Campos de Seleção
        policial_select = st.selectbox("Nome do Policial:", POLICIAIS)
        equip_select = st.selectbox("Equipamento:", EQUIPAMENTOS)
        
        # Campo de Litros (Inicia em 0.0)
        litros_input = st.number_input("Quantidade de Litros:", min_value=0.0, step=0.1)
        
        # Campo de Anexo (Obrigatório)
        foto_anexo = st.file_uploader("Anexar Imagem do Comprovante (Obrigatório)", type=['png', 'jpg', 'jpeg'])
        
        enviar = st.form_submit_button("Realizar Registro")
        
        if enviar:
            # --- VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS ---
            erros = []
            
            if policial_select == "Selecione o Policial...":
                erros.append("Selecione o nome do Policial.")
            
            if equip_select == "Selecione o Equipamento...":
                erros.append("Selecione o Equipamento.")
                
            if litros_input <= 0:
                erros.append("A quantidade de litros deve ser maior que zero.")
                
            if foto_anexo is None:
                erros.append("É obrigatório anexar a imagem do comprovante.")

            # Se houver erros, exibe todos e não salva
            if erros:
                for erro in erros:
                    st.error(erro)
                st.warning("⚠️ O registro não foi realizado. Preencha todos os campos.")
            else:
                # Se passar em tudo, realiza o registro
                loc_info = f"{pos_json['lat']}, {pos_json['lon']}" if pos_json else "GPS não autorizado"
                
                st.success("✅ REGISTRO REALIZADO COM SUCESSO!")
                st.write(f"**Policial:** {policial_select}")
                st.write(f"**Equipamento:** {equip_select}")
                st.write(f"**Litros:** {litros_input}")
                st.write(f"**Data/Hora:** {agora_br}")
                st.write(f"**Localização:** {loc_info}")
                st.balloons()

with tab2:
    st.subheader("Painel de Controle")
    st.write("Resumo de consumo (Dados Demonstrativos)")
    dados_exemplo = pd.DataFrame({
        'Equipamento': EQUIPAMENTOS[1:6], # Exclui o 'Selecione...'
        'Litros': [45, 65, 27, 180, 110] 
    })
    st.bar_chart(data=dados_exemplo, x='Equipamento', y='Litros')
