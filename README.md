# IACD - Trabalho Prático 1

## 1. Identificação
* **Inês Santos** 
* **51563**
* **Inteligência Artificial e Ciência de Dados** 
* **Interação com Modelos de Larga Escala** 
* **Modelo LLM:** `llama3.1:8b` (via Ollama)


## 2. Configuração do Ambiente
Para preparar o ambiente e instalar as bibliotecas necessárias, execute:
```bash
# Instalação de dependências
pip install pandas tqdm ollama
Nota: Certifique-se de que o Ollama está a correr com o modelo llama3.1:8b ativo.3. Instruções de Execução.
```
* A pipeline deve ser executada na seguinte ordem para garantir a integridade dos dados:

```bash
# Stitching: Reconstrução de trajetórias
python src/stitcher.py --input data/events.csv --output output/journeys.csv

# Analytics: Cálculo de métricas e anomalias
python src/analytics.py --input output/journeys.csv --output output/metrics.json

# Insights: Geração de inteligência via LLM
python src/insights.py --input output/metrics.json --output output/insights.json --strategy few-shot

# Report: Geração do relatório final 
python src/report.py --input output/insights.json --output output/weekly_report.md

# Evaluate: Validar a qualidade da reconstrução
python evaluate.py --data data/events.csv --output output/evaluation_report.json
```

## 3. Performance e Métricas de Avaliação
O sistema foi testado com o dataset original de 250.015 eventos, apresentando os seguintes resultados de performance e eficácia:
* Tempo de Execução (Stitching): ~40 segundos (Complexidade $O(n)$).
* Consistência: 100.00% (Garantia de que não há sobreposição de zonas).
* Cobertura: 100.00% (Todos os eventos foram processados e integrados).
* Completude: 42.86% (Capacidade de reconstrução de jornadas longas).


## 4. Testes de Robustez
Conforme exigido no enunciado, foram realizados testes de robustez através da injeção de anomalias controladas:
A utilização do ficheiro data/test_anomalies.csv com uma quebra artificial de 80% no tráfego da zona Z_FAT. O módulo de Analytics detetou o desvio estatístico com precisão e o módulo de Insights gerou recomendações operacionais adequadas à gravidade da situação.


## 5. Reprodutibilidade
Temperature: Definida como 0 em todas as interações com o LLM.Seeds (utilização de sementes fixas para garantir que os resultados da IA e da deteção de anomalias sejam consistentes em cada execução).