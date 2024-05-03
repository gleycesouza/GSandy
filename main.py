import streamlit as st
import previsao_modelo
import base64
import pandas as pd
import plotly.express as px
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go

# Função para converter arquivos binários (como imagens) em base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Função para definir a imagem de fundo
def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f"""
    <style>
    .stApp {{
    background-image: url("data:image/jpg;base64,{bin_str}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed; 
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Configuração da página com ícone de logo
st.set_page_config(
    page_title="GSandy",
    page_icon="./logo_gsandy.png",  # Ajuste o caminho para o local correto do arquivo
    layout="centered",
    initial_sidebar_state="expanded",
)

# Definindo a imagem de fundo
# set_png_as_page_bg("./background3.jpg")  # Ajuste o caminho para o local correto do arquivo

header_html = "<img src='data:image/png;base64,{}' class='center' style='width: 50px; display: block;margin-left: auto; margin-right: auto;'>".format(
    get_base64_of_bin_file("logo_gsandy.png")
)
st.markdown(
    header_html, unsafe_allow_html=True,
)

with st.container():
    st.markdown("<h1 style='text-align: center;'>GSandy</h1>", unsafe_allow_html=True)
    # element = st.markdown('<p style="color:black; text-align: center; margin-bottom: .1em;"><button type="button">Click Me!</button></p>', unsafe_allow_html=True)


    # Exibir texto de introdução
    element = st.caption("""O GSandy é um software desenvolvido como parte de um projeto de dissertação de mestrado em Geotecnia pela PUC-Rio. 
Concebido como uma ferramenta acadêmica, o programa utiliza dados publicamente disponíveis de ensaios de cisalhamento direto e DSS da literatura acadêmica
para prever a relação tensão x deformação/deslocamento em areias.

A exatidão do GSandy deriva do emprego de modelos de aprendizado de máquina — Random Forest, SVR e FNN —, cada um treinado para simular as 
características de comportamento do material geotécnico. A base de dados para o treinamento consiste exclusivamente em areia, e, portanto, 
as simulações refletem as respostas típicas desse material.

É importante notar que, embora o GSandy forneça uma simulação baseada em dados acadêmicos e modelos preditivos validados, 
ele serve como um complemento e não um substituto para a análise geotécnica. Decisões técnicas ou de projeto devem 
sempre ser apoiadas por métodos de avaliação detalhados e específicos para cada contexto.

Para informações mais detalhadas sobre a metodologia e os dados utilizados, a dissertação "Machine Learning para Previsão do Comportamento de Areias em Ensaios de Cisalhamento Direto e DSS" (Baptista, 2024) pode ser consultada como um recurso adicional. 
O GSandy está aqui para auxiliar no estudo e na compreensão dos complexos fenômenos geotécnicos e esperamos que seja uma valiosa adição ao seu repertório 
acadêmico e profissional.""")
    
# element.empty()
    
with st.container():
    st.subheader('Configuração de Simulação')

    test_type = st.radio(
        "Selecione o tipo de ensaio",
        ["DSS", "Cisalhamento Direto"],
        horizontal=False
    )
    # Chama a função no predict_model.py, passando a seleção como argumento
    previsao_modelo.load_models_and_predict(test_type)

    # Generate test data based on the selection
    if test_type == "DSS":
        x_label = 'Deformação Cisalhante γ (%)'
        test_values = np.arange(0, 20, 0.7)  # Example test values
        result_path = f'results_train/results_dss.xlsx'
        min_gs=2.64
        max_gs=2.78
        min_cr = 12
        max_cr = 100
        min_e0=0.422
        max_e0=1.06
        max_sv=750
        min_sv=6
        initial_values = [2.685,0.808,40,40]
        image_path = f'results_train/validation_dss.png'
        
    else:
        x_label = 'Deslocamento Horizontal δ (mm)'
        test_values = np.arange(0, 5, 0.3)  # Different example test values
        result_path = f'results_train/results_ds.xlsx'
        min_gs=2.643
        max_gs=2.763
        min_cr = 8
        max_cr=100
        min_e0=0.428
        max_e0=0.726
        max_sv=1600
        min_sv=13
        initial_values = [2.656,0.5520,64,150]
        image_path = f'results_train/validation_ds.png'

    st.caption('')

    col1, col2 = st.columns(2)

    with col1:
        gs = st.number_input('$G_{s}$ (Densidade real dos grãos)', min_value=min_gs, max_value=max_gs, step=0.001, format="%.3f", value=initial_values[0])
        e_cisalhamento = st.number_input('$e_{0}$ (Índice de vazios inicial)', min_value=min_e0, max_value=max_e0, step=0.001, format="%.3f", value=initial_values[1])

    with col2:
        cr = st.number_input('$CR$ (Compacidade Relativa - %)', min_value=min_cr, max_value=max_cr, step=1, value=initial_values[2])
        tensao_sv = st.number_input('$\sigma_{v}$ (Tensão Vertical - kPa)', min_value=min_sv, max_value=max_sv, step=10, value=initial_values[3])

    if st.button("Simular Gráfico", key='simular'):
        models = previsao_modelo.load_models_and_predict(test_type)
        rf_pred, svr_pred, nn_pred = previsao_modelo.plot_predictions(test_values, models, gs, e_cisalhamento, cr, tensao_sv)

        st.success('Simulação concluída!')
        
        # Create a DataFrame that combines all predictions
        df = pd.DataFrame({
            x_label: np.concatenate([test_values, test_values, test_values]),  # Repeat for each model
            r'τ/σ': np.concatenate([rf_pred, svr_pred, nn_pred]),  # Combine predictions
            'Modelo': ['Random Forest'] * len(test_values) + ['SVR'] * len(test_values) + ['Neural Network'] * len(test_values)  # Label models
        })
        # Define um conjunto de cores RGBA com transparência
        colors_with_transparency = [
            'rgba(255, 0, 0, 0.7)',  # Vermelho com 50% de transparência
            'rgba(0, 200, 0, 0.7)',  # Verde com 50% de transparência
            'rgba(0, 0, 255, 0.7)'   # Azul com 50% de transparência
        ]
        # Create a line chart with Plotly Express
        fig = px.line(
            df,
            x=x_label,
            y=r'τ/σ',
            color='Modelo',  # This will create a line for each model
            title='Resultado da Simulação',
            markers=False,
            # color_discrete_sequence=colors_with_transparency  # Usa o conjunto de cores definido
        )
        # Atualizar todas as linhas para terem uma transparência de 50% e um estilo de linha específico
        fig.update_traces(
            line=dict(width=2, dash='dash'), # Exemplo de estilo de linha dash com transparência
            # marker=dict(size=5)  # Tamanho do marcador, se necessário
        )

        # Use Streamlit tabs to display the chart with different themes
        tab1, tab2, tab3, tab4, tab5= st.tabs(["Gráfico", "Dados", "Métricas","Validação","Fontes"])

        with tab1:
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        with tab2:
            st.caption("Conjunto de Dados")
            st.dataframe(df, use_container_width=True)

        with tab3:
            st.caption(f'Métricas do Treinamento e Teste do Ensaio de {test_type}')
            df_results = pd.read_excel(result_path)
            formatted_columns = {col: '{:.3f}' for col in df_results.columns[1:]}
            df_results_formatted = df_results.style.format(formatted_columns)
            st.dataframe(df_results_formatted, use_container_width=True)

        with tab4:
            st.caption(f'Resultados da Previsão do Modelo nos Ensaios Ensaio de validação do {test_type}')
            st.image(image_path, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")

        with tab5:
            st.caption("A tabela apresenta a compilação de ensaios, autores, títulos dos trabalhos, materiais e a quantidade de ensaios que constituem a base de dados utilizada no treinamento dos modelos. ")
            df_autores = pd.read_excel("fontes_autores.xlsx")
            st.dataframe(df_autores, use_container_width=True)

            referencias = st.expander("Referência Bibliográfica")
            referencias.write(f"""
                ADAMS, R. K. Near-Surface Response of Beach Sand: An Experimental Investigation. 2017. Corvallis: Oregon State University, 2017. 
                
                AL TARHOUNI, M. A.; HAWLADER, B. Monotonic and cyclic behaviour of sand in direct simple shear test conditions considering low stresses. Soil Dynamics and Earthquake Engineering, v. 150, 1 nov. 2021. 
                
                COUTINHO, J. V. M. Ensaios de Cisalhamento Direto na Areia da Praia de Ipanema. 2021. Dissertação de Mestrado—Rio de Janeiro: Pontifícia Universidade Católica do Rio de Janeiro, 2021. 
                
                KIM, Y. S. Static simple shear characteristics of Nak-dong River clean sand. KSCE Journal of Civil Engineering, v. 13, n. 6, p. 389–401, set. 2009.

                LASHKARI, A.; FALSAFIZADEH, S. R.; RAHMAN, M. M. Influence of linear coupling between volumetric and shear strains on instability and post-peak softening of sand in direct simple shear tests. Acta Geotechnica, v. 16, n. 11, p. 3467–3488, 1 nov. 2021. 
                
                LASHKARI, A.; FALSAFIZADEH, S. R.; SHOURIJEH, P. T.; ALIPOUR, M. J. Instability of loose sand in constant volume direct simple shear tests in relation to particle shape. Acta Geotechnica, v. 15, n. 9, p. 2507–2527, 1 set. 2020. 

                MARQUES, F. DE L. Ensaios de resistência ao cisalhamento com areia de Hokksund para projeto de revitalização da câmara de calibração. 2009. Iniciação Científica—Rio de Janeiro: Universidade Federal do Rio de Janeiro (UFRJ) - Fundação Carlos Chagas Filho de Amparo à Pesquisa do Estado do RJ (FAPERJ), 2009. 
                
                MONTEIRO, D. P.; DANZIGER, B. R.; LIMA, B. T. Caracterização Geotécnica da Areia do Porto do Açu. 2023, 10o Seminário de Engenharia de Fundações Especiais e Geotecnia, 2023.              
                              
                NUNES, V. P. Ensaios de Caracterização Geotécnica da Areia da Praia de Itaipuaçu. 2014. Projeto de Graduação—Rio de Janeiro: Universidade Federal do Rio de Janeiro, 2014. 

                PINHEIRO, G. P. Caracterização Geotécnica em Laboratório da Areia da Praia dos Cavaleiros-Macaé/RJ. 2018. Macaé: Universidade Federal do Rio de Janeiro, 2018. 
            
                SIMÕES, F. B. Caracterização Geotécnica da Areia da Praia de Ipanema. 2015. Projeto de Graduação—Rio de Janeiro: Universidade Federal do Rio de Janeiro, 2015. 

                SCHUCK, T. E. DE S. Ensaios de cisalhamento simples na areia da Praia de Ipanema. 2022. 177 p. Dissertação de Mestrado—Rio de Janeiro: Pontifícia Universidade Católica do Rio de Janeiro, 2022. 
                
                TELES, G. L. V. Estudo Sobre os Parâmetros de Resistência e Deformabilidade da Areia de Hokksund. 2013. Projeto de Graduação—Rio de Janeiro: Universidade Federal do Rio de Janeiro, 2013. 
                            
                VAID, Y. P.; SIVATHAYALAN, S. Static and cyclic liquefaction potential of Fraser Delta sand in simple shear and triaxial tests. Can. Geotech. , v. 33, p. 281–289, 1996. 
                            
                ZORZAN, L. G. Resistência ao Cisalhamento do Solo pelos Ensaios de Cisalhamento Direto e DSS: Análise Experimental e Aplicação na Estabilidade de Taludes. 2018. Trabalho Final de Conclusão de Curso—Curitiba: Universidade Federal do Paraná, 2018. 
                """)
            
    st.header("",divider='gray')
    st.caption("Informações de contato: Gleyce Souza ([gleycesouzaa@gmail.com](mailto:gleycesouzaa@gmail.com)) e Marina Corte ([marinabellaver@gmail.com](mailto:marinabellaver@gmail.com))", unsafe_allow_html=True)



