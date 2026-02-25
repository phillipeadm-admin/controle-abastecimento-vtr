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

# --- CUSTOMIZAÇÃO VISUAL (CSS) ---
st.markdown("""
    <style>
    /* Fundo do App em Branco */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Estilização dos Botões */
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        transition: all 0.3s ease;
    }

    /* Efeito ao passar o mouse (Azul) */
    div.stButton > button:hover {
        background-color: #007BFF !important;
        color: white !important;
        border-color: #007BFF !important;
    }
    
    /* Estilo das abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stWidgetLabel"] {
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LISTAS OFICIAIS
POLICIAIS = ["Selecione o Policial..."] + ["ST J. CARLOS", "SGT VALTER", "SGT JOSÉ LOPES", "SGT MARCOS PAULO", "SGT RODRIGUES", "SGT ADELSON", "SGT DANTAS", "SGT ELSON", "SGT JOSÉ", "SGT LEANDRO", "SGT MARCONI", "SGT MARCELO", "SGT CARVALHO", "SGT ANDERSON", "SGT NILTON", "SGT R. MARQUES", "CB ANDERSON", "CB ROBSON", "CB LUCIANO", "CB GOMES", "CB ISRAEL", "CB DOUGLAS", "CB C. LEITE", "SD RAQUEL", "SD L. DIAS", "SD CARLOS", "SD PEREIRA", "SD BRUNO"]
EQUIPAMENTOS = ["Selecione o Equipamento..."] + ["GERADOR QCG", "GERADOR APMB", "GERADOR 1º BPM", "GERADOR 2º BPM", "GERADOR 3º BPM", "GERADOR 4º BPM", "GERADOR 5º BPM", "GERADOR 6º BPM", "GERADOR 7º BPM", "GERADOR 8º BPM", "GERADOR 9º BPM", "GERADOR 10º BPM", "GERADOR 11º BPM", "GERADOR 12º BPM", "GERADOR 13º BPM", "GERADOR 14º BPM", "GERADOR 15º BPM", "GERADOR CMT GERAL", "GERADOR SUB CMT GERAL"]

# 3. LÓGICA DE PERSISTÊNCIA
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

pos_json = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(success => { return {lat: success.coords.latitude, lon: success.coords.longitude} })", key="geo_location")

st.set_page_config(page_title="Abastecimento VTR", layout="centered")
st.title("⛽ Sistema de Abastecimento")

tab1, tab2 = st.tabs(["📝 Registro", "📊 Dashboard de Pesquisa"])

with tab1:
    st.subheader("Novo Lançamento")
    st.info(f"📅 Horário Oficial: {agora_str}")
    
    with st.form("form_abastecimento", clear_on_submit=True):
        policial_select = st.selectbox("Policial:", POLICIAIS)
        equip_select = st.selectbox("Equipamento:", EQUIPAMENTOS)
        litros_input = st.number_input("Quantidade de Litros:", min_value=0.0, step=0.1)
        
        st.write("**Anexar Imagem do Comprovante (Obrigatório)**")
        foto_anexo = st.file_uploader("Escolha um arquivo ou arraste aqui", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
        
        enviar = st.form_submit_button("Realizar Registro")
        
        if enviar:
            if policial_select != "Selecione o Policial..." and equip_select != "Selecione o Equipamento..." and litros_input > 0 and foto_anexo is not None:
                loc_info = f"{pos_json['lat']}, {pos_json['lon']}" if pos_json else "GPS não autorizado"
                novo_registro = {"Data/Hora": agora_str, "Policial": policial_select, "Equipamento": equip_select, "Litros": litros_input, "Localizacao": loc_info}
                salvar_dados(novo_registro)
                st.success("✅ REGISTRO SALVO COM SUCESSO!")
                st.balloons()
            else:
                st.error("⚠️ Erro: Preencha todos os campos obrigatórios!")

with tab2:
    st.subheader("🔎 Pesquisa de Registros")
    df_historico = carregar_dados()

    if not df_historico.empty:
        anos = sorted(df_historico['Data/Hora'].dt.year.unique(), reverse=True)
        meses_lista = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        
        col1, col2 = st.columns(2)
        with col1:
            ano_sel = st.selectbox("Filtrar por Ano:", anos)
        with col2:
            mes_sel_num = st.selectbox("Filtrar por Mês:", list(meses_lista.keys()), format_func=lambda x: meses_lista[x], index=agora.month-1)

        df_filtrado = df_historico[(df_historico['Data/Hora'].dt.year == ano_sel) & (df_historico['Data/Hora'].dt.month == mes_sel_num)]

        if not df_filtrado.empty:
            st.write(f"Registros de **{meses_lista[mes_sel_num]} de {ano_sel}**:")
            st.dataframe(df_filtrado, use_container_width=True)
            st.bar_chart(data=df_filtrado, x='Equipamento', y='Litros')
            
            if st.button("Analisar este período com Gemini"):
                resumo_texto = df_filtrado[['Equipamento', 'Litros']].to_string(index=False)
                prompt_ia = f"Analise estes dados de abastecimento policial do mês {meses_lista[mes_sel_num]}:\n\n{resumo_texto}\n\nO consumo está normal? Identifique o maior gasto."
                
                try:
                    with st.spinner('O Gemini está analisando os dados...'):
                        res = model.generate_content(prompt_ia)
                        st.write("🤖 **Análise da IA:**")
                        st.write(res.text)
                except Exception as e:
                    st.error(f"Erro na IA.")
        else:
            st.warning(f"Sem registros para {meses_lista[mes_sel_num]} de {ano_sel}.")
    else:
        st.info("O banco de dados está vazio.")
