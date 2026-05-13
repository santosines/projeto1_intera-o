import pandas as pd
import argparse
import os
from tqdm import tqdm

def run_stitcher(input_path, output_path):
    print(f"A carregar eventos de: {input_path}...")
    df = pd.read_csv(input_path)
    df.columns = [c.strip() for c in df.columns]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # ordenação lógica: entry -> linger -> exit
    prio = {'entry': 1, 'linger': 2, 'exit': 3}
    df['prio'] = df['event_type'].str.lower().map(prio).fillna(4)
    df = df.sort_values(by=['timestamp', 'prio']).reset_index(drop=True)

    # estado: guardamos as pessoas que estão "dentro" da loja
    # p_id -> {last_ts, current_zone, gender, age}
    active_people = {}
    current_zone_visits = {} 
    journeys = []
    person_counter = 1
    MAX_GAP_SECONDS = 600 

    print("A reconstruir trajetórias (Modo Multi-Perfil):")
    
    for _, row in tqdm(df.iterrows(), total=len(df)):
        event_type = str(row['event_type']).lower()
        zone_id = str(row['zone_id'])
        ts = row['timestamp']
        gender = str(row['gender'])
        age = str(row['age_range']) if 'age_range' in row else str(row.get('age', 'adult'))
        
        assigned_p_id = None

        # tentar associação inteligente
        if event_type == 'entry':
            # procura alguém do mesmo perfil que esteja FORA de qualquer zona e tenha sido visto há pouco tempo
            for p_id, data in active_people.items():
                if data['gender'] == gender and data['age'] == age:
                    if data['current_zone'] is None:
                        if (ts - data['last_ts']).total_seconds() < MAX_GAP_SECONDS:
                            assigned_p_id = p_id
                            break
        else:
            # Linger ou Exit: procura alguém do mesmo perfil que ESTEJA especificamente nesta zona
            for p_id, data in active_people.items():
                if data['gender'] == gender and data['age'] == age:
                    if data['current_zone'] == zone_id:
                        assigned_p_id = p_id
                        break

        # se nao encontrar, cria novo
        if assigned_p_id is None:
            assigned_p_id = f"P_{person_counter:05d}"
            person_counter += 1
            active_people[assigned_p_id] = {
                'last_ts': ts, 'current_zone': None, 
                'gender': gender, 'age': age
            }

        # maquina de estados
        if event_type == 'entry':
            if assigned_p_id in current_zone_visits:
                v = current_zone_visits.pop(assigned_p_id)
                v['exit_time'] = ts
                journeys.append(v)

            current_zone_visits[assigned_p_id] = {
                'person_id': assigned_p_id, 'zone_id': zone_id,
                'entry_time': ts, 'exit_time': ts, 'dwell_s': 0,
                'gender': gender, 'age_range': age,
                'visit_date': ts.date().isoformat(), 'hour_of_day': ts.hour
            }
            active_people[assigned_p_id]['current_zone'] = zone_id
        
        elif event_type == 'linger':
            if assigned_p_id in current_zone_visits:
                try:
                    current_zone_visits[assigned_p_id]['dwell_s'] = int(float(row['duration_s']))
                except: pass
        
        elif event_type == 'exit':
            if assigned_p_id in current_zone_visits:
                visit = current_zone_visits.pop(assigned_p_id)
                visit['exit_time'] = ts
                journeys.append(visit)
                active_people[assigned_p_id]['current_zone'] = None
        
        active_people[assigned_p_id]['last_ts'] = ts

    if journeys:
        output_df = pd.DataFrame(journeys)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        output_df.to_csv(output_path, index=False)
        print(f"\nSucesso: {len(output_df)} visitas registadas.")
        print(f"Visitantes únicos: {person_counter - 1}")
    else:
        print("\nErro crítico: Nenhuma visita processada.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    run_stitcher(args.input, args.output)