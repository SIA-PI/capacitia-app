# 🚀 CapacitIA - Dashboard de Análise de Capacitações e Projetos de IA

![Banner SIA](https://sia.pi.gov.br/wp-content/uploads/2024/01/SIA_Banner.png)
![Banner CapacitIA](https://www.pi.gov.br/wp-content/uploads/2025/03/CAPACITIA-01-1024x443.png)

## 🎯 Sobre o Projeto

Este é um dashboard interativo desenvolvido com Streamlit para analisar e visualizar dados de duas frentes principais:

1.  **Dashboard de Capacitações**: Monitoramento do desempenho de cursos e masterclasses, analisando métricas como número de inscritos, certificados, taxa de evasão e engajamento por secretaria e cargo.
2.  **Monitoramento de Resultados - CapacitIA**: Acompanhamento dos projetos de Inteligência Artificial desenvolvidos no âmbito do programa CapacitIA, o engajamento dos participantes e os desafios enfrentados.

A aplicação permite que gestores e equipes explorem os dados de forma dinâmica através de filtros interativos, gráficos e tabelas detalhadas.

## ✨ Funcionalidades Principais

### Análise de Capacitações (`app.py`)

-   **Visão Geral Agregada**: KPIs (Indicadores-Chave de Desempenho) dinâmicos que mostram o total de inscritos, certificados, e as taxas de certificação e evasão, atualizados com base nos filtros.
-   **Filtros Dinâmicos**: Filtre os dados por tipo de capacitação (Masterclass, Cursos) e por Secretaria/Órgão.
-   **Análise Comparativa**: Gráficos interativos que comparam o desempenho (inscritos, certificados, taxa de permanência) entre diferentes Secretarias e Cargos.
-   **Funil de Conversão**: Visualização clara da jornada do participante, desde a inscrição até a certificação.
-   **Rankings Detalhados**: Tabelas e gráficos que classificam cargos e secretarias por número de inscritos e taxa de certificação.

### Monitoramento de Projetos de IA (`app_ia.py`)

-   **Panorama Geral do Programa**: KPIs sobre o número de projetos mapeados, participantes, secretarias envolvidas e soluções em uso.
-   **Detalhes por Secretaria**: Explore os projetos específicos desenvolvidos por cada secretaria, com descrição e link para a ferramenta.
-   **Análise dos Participantes**: Gráficos sobre o perfil dos participantes, incluindo o desenvolvimento de assistentes, o uso atual das soluções e os principais desafios enfrentados.
-   **Visualização de Dados Brutos**: Tabelas para consulta direta dos dados de projetos e respostas dos participantes.

## 🛠️ Tecnologias Utilizadas

-   **Python**: Linguagem principal do projeto.
-   **Streamlit**: Framework para a criação do dashboard interativo.
-   **Pandas**: Para manipulação e análise dos dados.
-   **Plotly Express**: Para a criação de gráficos interativos e visualmente atraentes.

## 📂 Estrutura do Projeto

```
Capacitia/
│
├── app.py                      # Script principal do Dashboard de Capacitações
├── app_ia.py                   # Script do Dashboard de Monitoramento do CapacitIA
├── requirements.txt            # Dependências do projeto
├── exploration.ipynb           # Notebook para exploração inicial dos dados (opcional)
├── README.md                   # Este arquivo
│
└─── dados/
     ├── capacitia-dados.xlsx    # Planilha com dados de inscrições, certificados, etc.
     ├── CapacitIA - Trabalhos _ Assistentes - ASSISTENTES.csv  # CSV com os projetos de IA
     └── Utilização de Assistentes de IA (respostas) - ... .csv # CSV com respostas dos participantes
```

## 🚀 Como Executar a Aplicação

1.  **Clone o repositório (se aplicável):**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd Capacitia
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o dashboard principal:**
    ```bash
    streamlit run app.py
    ```

A aplicação será aberta no seu navegador padrão. O dashboard de monitoramento do CapacitIA é acessível através da aba "Assistentes de IA" no dashboard principal.
