import json
import argparse
import os
from datetime import datetime

def run_report(input_path, output_path):
    print(f"A gerar Relatório Semanal:")
    
    if not os.path.exists(input_path):
        print(f"Erro: Ficheiro {input_path} não encontrado.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    insights = data.get('insights', [])

    # construção do conteúdo em markdown
    md = f"#Relatório Semanal de Inteligência operacional\n"
    md += f"**Data de geração:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    # resumo executivo 
    md += "## 1. Resumo Executivo\n"
    md += "Este relatório apresenta os factos mais críticos observados na última semana de operação. "
    md += "A análise foca-se em padrões de tráfego, eficiência de conversão e anomalias detetadas.\n\n"
    
    # 3 primeiros insights para o resumo
    for ins in insights[:3]:
        md += f"* **{ins.get('titulo')}**: {ins.get('observacao')}\n"

    # insights detalhados 
    md += "\n## 2. Análise Detalhada e Anomalias\n"
    for ins in insights:
        md += f"### {ins.get('titulo')}\n"
        md += f"**Categoria:** {ins.get('categoria')} | **Urgência:** {ins.get('urgencia')}\n\n"
        md += f"* **Observação:** {ins.get('observacao')}\n"
        md += f"* **Implicação:** {ins.get('implicacao')}\n"
        md += f"* **Recomendação:** {ins.get('recomendacao')}\n\n"
        md += "---\n"

    # recomendações prioritárias 
    md += "\n## 3. Recomendações para a Próxima Semana\n"
    # filtrar por urgência imediata ou mostrar as primeiras 5
    for i, ins in enumerate(insights[:5]):
        md += f"{i+1}. **{ins.get('recomendacao')}** (Prioridade: {ins.get('urgencia')})\n"

    # guardar o ficheiro
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Sucesso: Relatório gerado em {output_path}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="insights.json")
    parser.add_argument("--output", required=True, help="weekly_report.md")
    args = parser.parse_args()
    run_report(args.input, args.output)