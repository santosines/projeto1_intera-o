import pandas as pd
import json
import argparse
import os
import sys

def run_analytics(input_path, output_path):
    print(f"A iniciar Analytics:")
    
    try:
        if not os.path.exists(input_path):
            print(f"ERRO: O ficheiro {input_path} não existe!")
            return

        df = pd.read_csv(input_path)
        print(f"Sucesso: {len(df)} linhas lidas do CSV.")

        # conversão de tipos para garantir cálculos precisos 
        df['entry_time'] = pd.to_datetime(df['entry_time'])
        df['exit_time'] = pd.to_datetime(df['exit_time'])
        df['visit_date'] = pd.to_datetime(df['visit_date']).dt.date
        
        metrics = {}


        # tráfego geral 
        metrics['traffic_general'] = {
            'total_unique_visitors': int(df['person_id'].nunique()),
            'avg_visit_duration_seconds': float(df.groupby('person_id')['dwell_s'].sum().mean()),
            'visitors_per_day': df.groupby('visit_date')['person_id'].nunique().astype(int).rename(index=str).to_dict()
        }
        print("Métricas de tráfego calculadas.")


        # métricas por zona 
        zone_metrics = {}
        for zone in df['zone_id'].unique():
            zone_df = df[df['zone_id'] == zone]
            visitors_in_zone = zone_df['person_id'].nunique()
            stop_count = zone_df[zone_df['dwell_s'] > 0]['person_id'].nunique()
            
            zone_metrics[zone] = {
                'total_traffic': int(visitors_in_zone),
                'avg_dwell_time': float(zone_df['dwell_s'].mean()),
                'stop_rate': float(stop_count / visitors_in_zone) if visitors_in_zone > 0 else 0
            }
        metrics['zones'] = zone_metrics
        print("Métricas por zona calculadas.")


        # funil de cliente 
        total_v = metrics['traffic_general']['total_unique_visitors']
        # considera conversão quem passou pelas caixas (Z_C) ou Checkout (Z_CK) 
        converted_visitors = df[df['zone_id'].str.contains('Z_C', na=False)]['person_id'].unique()
        num_converted = len(converted_visitors)
        
        metrics['funnel'] = {
            'total_entrants': int(total_v),
            'converted_to_checkout': int(num_converted),
            'conversion_rate': float(num_converted / total_v) if total_v > 0 else 0
        }
        print("Funil de cliente calculado.")


# bloco de anomalias
        counts_df = df.groupby(['zone_id', 'hour_of_day', 'visit_date'])['person_id'].nunique().reset_index(name='count')
        
        anomalies = []
        for index, row in counts_df.iterrows():
            zone, hour, date, count = row['zone_id'], row['hour_of_day'], row['visit_date'], row['count']
            
            historical_data = counts_df[(counts_df['zone_id'] == zone) & 
                                        (counts_df['hour_of_day'] == hour) & 
                                        (counts_df['visit_date'] != date)]
            
            if not historical_data.empty:
                avg = historical_data['count'].mean()
                
                # SÓ CONSIDERA ANOMALIA SE:
                # o desvio for > 20%
                # a média for superior a 5 pessoas (evita ruído em zonas vazias)
                if avg > 0: 
                    deviation = abs(count - avg) / avg
                    if deviation > 0.20:
                        anomalies.append({
                            'zone': zone,
                            'hour': int(hour),
                            'observed': int(count),
                            'expected': float(avg),
                            'deviation': float((count - avg) / avg)
                        })
        
        # ordenar as anomalias por gravidade (maior desvio primeiro)
        anomalies = sorted(anomalies, key=lambda x: abs(x['deviation']), reverse=True)
        
        # guardar apenas as 50 mais críticas para o LLM não ficar confuso
        metrics['anomalies'] = anomalies[:50] 
        print(f"Deteção de anomalias concluída ({len(anomalies)} encontradas, 50 filtradas).")


        # top 10 sequências de zonas
        sequences = df.sort_values(['person_id', 'entry_time']).groupby('person_id')['zone_id'].apply(tuple)
        top_sequences = sequences.value_counts().head(10).to_dict()
        metrics['top_sequences'] = { " -> ".join(k): int(v) for k, v in top_sequences.items() }


        # gravação final
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=4, ensure_ascii=False)
        
        print(f"Ficheiro {output_path} gerado.")

    except Exception as e:
        print(f"Erro durante a execução.")
        print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    run_analytics(args.input, args.output)