# GSandy

GSandy é um software desenvolvido como parte de uma dissertação de mestrado em Geotecnia pela PUC-Rio. Ele utiliza dados de ensaios de cisalhamento direto e DSS para prever a relação tensão x deformação/deslocamento em areias, empregando modelos de aprendizado de máquina (Random Forest, SVR, FNN).

## Pré-requisitos

- Python 3.9
- Pipenv

## Instalação

1. Instale o Pipenv:
    ```bash
    pip install pipenv
    ```

2. Navegue até a pasta do projeto e instale as dependências:
    ```bash
    pipenv install
    ```

3. Ative o ambiente virtual:
    ```bash
    pipenv shell
    ```

## Executando o GSandy

Para iniciar o GSandy, execute:
```bash
streamlit run main.py
```
## Licença

Este projeto está registrado e licenciado sob a Licença de Software Livre / GNU General Public License (GPL). 

## Notas
GSandy é uma ferramenta acadêmica e deve ser usada como complemento à análise geotécnica tradicional. Consulte a dissertação "Machine Learning para Previsão do Comportamento de Areias em Ensaios de Cisalhamento Direto e DSS" (Baptista, 2024) para mais detalhes.