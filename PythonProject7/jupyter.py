import nbformat as nbf

# Criação do notebook
nb = nbf.v4.new_notebook()

# Célula Markdown - Introdução
markdown_introducao = """
# Introdução

Este projeto visa resolver um problema de agendamento de tarefas em um projeto utilizando programação com restrições (CP - Constraint Programming). A principal ferramenta utilizada foi a biblioteca OR-Tools da Google.

O objetivo é alocar e agendar tarefas de forma eficiente, respeitando restrições de precedência e recursos limitados, de forma a otimizar o tempo total de execução do projeto, chamado de *makespan*.

## Justificativa da Escolha do Problema
O problema de agendamento é central em áreas como engenharia de produção, gestão de projetos e otimização de recursos. Resolver este problema de forma eficiente permite otimizar a alocação de recursos limitados e minimizar o tempo necessário para a execução de um projeto.

**Equipa**: 
- Nome do estudante: Raquel Martins
- Número do estudante: 23999
"""

# Célula Markdown - Formulação do Objetivo
markdown_objetivo = """
# Formulação do Objetivo

O objetivo deste projeto é otimizar o agendamento de tarefas em um projeto, levando em consideração:
- A precedência das tarefas (algumas tarefas só podem ser iniciadas após a conclusão de outras).
- A alocação de recursos limitados para cada tarefa.

## Definição do Problema de Agendamento
O problema pode ser descrito como um **problema de alocação de recursos** com **restrições de precedência**. Cada tarefa tem uma duração fixa e requer uma certa quantidade de recursos. Algumas tarefas só podem ser executadas após outras, e não é possível que duas tarefas compartilhem o mesmo recurso ao mesmo tempo.

### Objetivo Principal
Minimizar o **makespan**, que é o tempo total necessário para completar todas as tarefas, respeitando as restrições de precedência e de recursos.
"""

# Célula Markdown - Design do Agente
markdown_agente = """
# Design do Agente

## Atributos do Agente (PEAS)

- **Performance measure (P)**: Minimizar o makespan, ou seja, o tempo total de execução do projeto.
- **Environment (E)**: O ambiente consiste nas tarefas a serem realizadas, nos recursos limitados e nas relações de precedência entre as tarefas.
- **Actuators (A)**: O agente deve alocar e agendar as tarefas no tempo adequado, respeitando as restrições de precedência e os recursos disponíveis.
- **Sensors (S)**: O agente deve monitorar os recursos e o progresso das tarefas para garantir que todas as restrições sejam atendidas.

## Formulação do Problema como Busca

### Variáveis e Restrições
- **Variáveis**: Os tempos de início e término de cada tarefa. 
  - Domínio: Intervalo de tempo disponível (de 0 até o horizonte do projeto).

- **Restrições**:
  - **Precedência**: Algumas tarefas devem ser concluídas antes que outras possam começar.
  - **Recursos**: Um recurso não pode ser utilizado simultaneamente por duas tarefas.

O modelo utilizado no solver OR-Tools combina **programação com restrições (CP)** e técnicas de busca para minimizar o makespan.
"""

# Célula Markdown - Estratégias de Busca
markdown_estrategias = """
# Estratégias de Busca e Resultados

## Estratégias Testadas
1. **AUTOMATIC_SEARCH**: O solver ajusta dinamicamente a técnica de busca.
2. **FIXED_SEARCH**: Utiliza uma técnica de busca fixa, pré-definida.
3. **PORTFOLIO_SEARCH**: Combina várias técnicas de busca em paralelo.

### Arquivo de Resultados
Os resultados são registrados em um arquivo CSV com o seguinte formato:

| Strategy       | WallTime | Conflicts | Branches | Makespan | ProcessTime | Efficiency |
|----------------|----------|-----------|----------|----------|-------------|------------|
| AUTOMATIC_SEARCH | 0.02     | 0         | 27       | 47.0     | 0.034       | 100.0      |
| FIXED_SEARCH     | 0.023    | 0         | 18       | 47.0     | 0.023       | 100.0      |
| PORTFOLIO_SEARCH | 0.024    | 0         | 3        | 47.0     | 0.024       | 97.2       |

## Explicação dos Resultados
- **Strategy**: A estratégia de busca utilizada.
- **WallTime**: Tempo total de execução.
- **Conflicts**: Número de inconsistências encontradas durante a busca.
- **Branches**: Número de ramificações realizadas pelo solver.
- **Makespan**: Tempo total necessário para concluir todas as tarefas (objetivo a ser minimizado).
- **ProcessTime**: Tempo efetivo de processamento da busca.
- **Efficiency**: Eficiência da estratégia (%).

### Comparação de Estratégias
- **AUTOMATIC_SEARCH**: Equilibrada, fornece um makespan ótimo com tempo mínimo.
- **FIXED_SEARCH**: Similar à AUTOMATIC_SEARCH em makespan, mas com menor eficiência.
- **PORTFOLIO_SEARCH**: Garante robustez ao explorar múltiplas abordagens, mas pode ser menos eficiente.

A escolha depende do **tempo disponível** e da **complexidade do problema**. Para situações com menor complexidade, **AUTOMATIC_SEARCH** é ideal.
"""

# Célula Markdown - Conclusão
markdown_conclusao = """
# Conclusão

O projeto demonstrou a eficiência da **programação com restrições (CP)** para resolver problemas de agendamento. A análise das estratégias de busca permitiu identificar a mais adequada para otimizar o **makespan** enquanto mantém a eficiência computacional.

**Melhor Estratégia Identificada**: **AUTOMATIC_SEARCH**, pela combinação de tempo de execução, eficiência e robustez.

### Futuras Melhorias
- Explorar novos modelos híbridos (como metaheurísticas combinadas com CP).
- Ajustar os parâmetros do solver para problemas mais complexos.
- Incluir restrições adicionais para adaptar o modelo a cenários reais.
"""

# Célula de código - Leitura do Arquivo de Resultados
code_resultados = """
import pandas as pd

# Função para ler os resultados de um arquivo CSV
def read_results(file_path):
    df = pd.read_csv(file_path)
    return df

# Exemplo de leitura de um arquivo de resultados
results_file_path = "search_results.csv"
results_df = read_results(results_file_path)
print(results_df)
"""

# Adicionando as células ao notebook
nb.cells.append(nbf.v4.new_markdown_cell(markdown_introducao))
nb.cells.append(nbf.v4.new_markdown_cell(markdown_objetivo))
nb.cells.append(nbf.v4.new_markdown_cell(markdown_agente))
nb.cells.append(nbf.v4.new_markdown_cell(markdown_estrategias))
nb.cells.append(nbf.v4.new_code_cell(code_resultados))
nb.cells.append(nbf.v4.new_markdown_cell(markdown_conclusao))

# Salvar o notebook
with open("combined_project_scheduling_report.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)
