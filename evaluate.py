import pandas as pd
import json
import argparse
import os

def evaluate_pipeline(data_path, output_path):
    print(f"A iniciar Harness de Avaliação:")
    
    # carregar dados
    events_df = pd.read_csv(data_path)
    # assumimos que o output/journeys.csv já foi gerado pelo stitcher
    journeys_path = "output/journeys.csv"
    if not os.path.exists(journeys_path):
        print("Erro: output/journeys.csv não encontrado. Corre o stitcher primeiro.")
        return
    
    journeys_df = pd.read_csv(journeys_path)
    journeys_df['entry_time'] = pd.to_datetime(journeys_df['entry_time'])
    journeys_df['exit_time'] = pd.to_datetime(journeys_df['exit_time'])

    results = {}

    # mmétrica: consistência 
    # verificar se alguma pessoa tem sobreposição de horários em zonas diferentes
    consistency_errors = 0
    for p_id, group in journeys_df.groupby('person_id'):
        group = group.sort_values('entry_time')
        # compara o fim de uma zona com o início da próxima
        overlap = (group['exit_time'].shift(1) > group['entry_time']).any()
        if overlap:
            consistency_errors += 1
    
    total_p = journeys_df['person_id'].nunique()
    results['consistency'] = ((total_p - consistency_errors) / total_p) * 100

    # métrica: cobertura 
    # aproximação: eventos no journeys vs eventos no original (cada linha no journeys ~ 3 eventos)
    # o stitcher descarta eventos que não formam trios ou não ligam bem
    total_events = len(events_df)
    assigned_events = len(journeys_df) * 3 # entry, linger, exit
    results['coverage'] = min((assigned_events / total_events) * 100, 100.0)

    # métrica: completude 
    # trajetórias que começam em ZE e terminam em ZE ou ZCK
    complete_journeys = 0
    for p_id, group in journeys_df.groupby('person_id'):
        group = group.sort_values('entry_time')
        start_zone = str(group.iloc[0]['zone_id'])
        end_zone = str(group.iloc[-1]['zone_id'])
        
        if start_zone.startswith('Z_E') and (end_zone.startswith('Z_E') or 'Z_CK' in end_zone or 'Z_C' in end_zone):
            complete_journeys += 1
            
    results['completeness'] = (complete_journeys / total_p) * 100 if total_p > 0 else 0

    # guardar resultados
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    
    print(f"Avaliação concluída:")
    print(f"Consistência: {results['consistency']:.2f}% (Esperado: 100%)")
    print(f"Cobertura: {results['coverage']:.2f}%")
    print(f"Completude: {results['completeness']:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="events_validation.csv")
    parser.add_argument("--output", required=True, help="evaluation_report.json")
    args = parser.parse_args()
    evaluate_pipeline(args.data, args.output)