import json
import argparse
import os
import ollama

def get_prompt_zero_shot(metrics):
    """Estratégia A: Zero-shot Prompting"""
    return f"""
    És um analista de dados de retalho sénior. Analisa as métricas de tráfego de uma loja e gera insights estratégicos.
    
    DADOS:
    {json.dumps(metrics, indent=2)}
    
    Responde exxclusivamente em formato JSON seguindo rigorosamente esta estrutura:
    {{
      "insights": [
        {{
          "id": "INS_001",
          "categoria": "trafego|zona|funil|anomalia|demografico",
          "titulo": "Título curto e profissional",
          "observacao": "Descrição factual com números do ficheiro",
          "implicacao": "Consequência para o negócio",
          "recomendacao": "Ação concreta para o gestor da loja",
          "urgencia": "imediata|esta_semana|proximo_mes",
          "confianca": 0.95
        }}
      ]
    }}
    """

def get_prompt_few_shot(metrics):
    return f"""
    És um consultor de gestão de retalho. Analisa estes dados e cria EXATAMENTE 4 insights estratégicos. Não te limites a descrever os números; explica o porquê e dá recomendações.
    
    DADOS: {json.dumps(metrics)}

    Responde apenas em JSON com esta estrutura exata (não inventes chaves novas como 'zone' ou 'deviations'):
    {{
      "insights": [
        {{
          "id": "INS_01",
          "categoria": "trafego",
          "titulo": "Título do Insight",
          "observacao": "Frase com dados reais (ex: A zona Z_C2 tem 25% do fluxo)",
          "implicacao": "O que isto significa para o negócio",
          "recomendacao": "Ação concreta para o gerente",
          "urgencia": "imediata",
          "confianca": 0.95
        }}
      ]
    }}
    """

def run_insights(input_path, output_path, strategy='few-shot'):
    print(f"A iniciar a geração de Insights:")
    print(f"Estratégia: {strategy}")

    if not os.path.exists(input_path):
        print(f"Erro: Ficheiro {input_path} não encontrado.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        metrics = json.load(f)

    prompt = get_prompt_zero_shot(metrics) if strategy == 'zero-shot' else get_prompt_few_shot(metrics)

    try:
        # chamada ao Ollama com Llama 3.1 8B (temperature=0)
        response = ollama.chat(
            model='llama3.1:8b', 
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0}
        )

        content = response['message']['content'].strip()

        # limpeza de markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        raw_data = json.loads(content)

        # verificar se o LLM enviou uma lista ou um dicionário
        if isinstance(raw_data, list):
            insights_data = {"insights": raw_data}
        else:
            insights_data = raw_data

        # guardar resultado
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(insights_data, f, indent=4, ensure_ascii=False)
        
        num_insights = len(insights_data.get('insights', []))
        print(f"Sucesso: {num_insights} insights gerados em {output_path}.")

    except json.JSONDecodeError:
        print("Erro: O LLM não devolveu um JSON válido.")
        print("Resposta bruta:", content[:200], "...")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--strategy", default="few-shot", choices=["zero-shot", "few-shot"])
    args = parser.parse_args()
    run_insights(args.input, args.output, args.strategy)