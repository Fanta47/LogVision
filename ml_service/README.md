# ml_service

Installation (Windows CMD)

```cmd
cd ml_service
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Pipeline ML

```cmd
python scripts\extract_events.py
python scripts\normalize_events.py
python scripts\build_sequences.py
python scripts\train_iforest.py
python scripts\train_kmeans.py
python scripts\train_logbert_embeddings.py
python scripts\compare_models.py
python scripts\write_scores_to_postgres.py
```

Anomalies prioritaires

Persistence / SQL
- explosion du nombre de requetes SQL
- requetes SQL tres longues
- sequences SQL inhabituelles
- trop de requetes sur le meme thread
- result_size anormal
- UPDATE/DELETE rares
- sql_query repetes sans result_size

SLA
- hausse anormale de NOT FOUND
- ratio NOT FOUND / found anormal
- meme caller_class en echec repete
- meme context_raw repete en boucle
- nouveau sla_class_name jamais vu
- burst d'evenements SLA
- meme thread qui genere trop d'evenements

Global
- frequence d'evenements anormale
- repetition excessive du meme template
- transition rare entre event_type
- silence anormal apres activite forte
- nouveau event_type rare

Tests rapides

```cmd
cd ml_service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python scripts\extract_events.py
python scripts\normalize_events.py
python scripts\build_sequences.py
python scripts\train_iforest.py
python scripts\train_kmeans.py
python scripts\train_logbert_embeddings.py
python scripts\compare_models.py

:: verifications fichiers
:: data/events.csv
:: data/events_normalized.csv
:: data/sequences.csv
:: outputs/iforest_scores.csv
:: outputs/kmeans_scores.csv
:: outputs/logbert_like_scores.csv
:: outputs/model_comparison.csv

:: verification docker
cd ..
docker compose up -d
docker compose logs -f logstash
docker compose logs -f postgres
docker compose logs -f elasticsearch
```
