
# Stack Docker: Airflow + MySQL + Hadoop (HDFS)

> **Status do pacote**: README gerado automaticamente em 2025-09-24 a partir do ZIP enviado. Foram detectados alguns pontos a ajustar (veja **Checklist de correções**).

## 🎯 Objetivo
Provisionar um ambiente local com:
- **MySQL** (banco de dados)
- **Hadoop HDFS** (armazenamento distribuído)
- **Airflow** (orquestração de DAGs)
- DAGs Python que lêem do MySQL, transformam e salvam saídas no HDFS.

## 📦 Estrutura detectada
```
├─ dag1.py
├─ dag2.py
├─ dag3.py
├─ data.sql
├─ docker-compose.yml
├─ requiriments.txt
├─ shells.md
```

## 🔎 Observações sobre o `docker-compose.yml`
O arquivo contém o seguinte início (trecho relevante):

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:latest
    environment:
      MYSQL_ROOT_PASSWORD: fiapOn
      MYSQL_DATABASE: dbfiapon
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  hadoop:
    image: bde2020/hadoop-python:latest
    ports:
      - "9870:9870"
    volumes:
      - hadoop_data:/hadoop/dfs

  airflow:
    image: apache/airflow:2.5.0
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: mysql+pymysql://root:fiapOn@mysql/dbfiapon
      AIRFLOW__WEBSERVER__RBAC: "true"
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/usr/local/airflow/dags
      - ./requirements.txt:/requirements.txt
    depends_on:
      - mysql
    command: >
      bash -c "pip install -r /requirements.txt &&
               airflow db init &&
               airflow scheduler & airflow webserver"

volumes:
  mysql_data:
  hadoop_data:
```

> ⚠️ Notamos que há `...` no meio do arquivo — indicando trechos faltando. Abaixo há um **compose de referência** funcional para você comparar e completar.

## ✅ Checklist de correções recomendadas
- [ ] Arquivo `requiriments.txt` encontrado; o compose referencia `requirements.txt`. Renomear e corrigir conteúdo.
- [ ] Pasta `dags/` não existe, mas o compose monta `./dags` no contêiner do Airflow.
- [ ] `dag1.py` usa senha MySQL sem aspas (`password=fiapOn`). Corrigir para `password='fiapOn'` ou usar variável de ambiente.
- [ ] `dag2.py` usa senha MySQL sem aspas (`password=fiapOn`). Corrigir para `password='fiapOn'` ou usar variável de ambiente.
- [ ] `dag3.py` usa senha MySQL sem aspas (`password=fiapOn`). Corrigir para `password='fiapOn'` ou usar variável de ambiente.
- [ ] `shells.md` está vazio (opcional remover ou preencher).


### Itens específicos
1. **Criar a pasta `dags/`** e **mover** `dag1.py`, `dag2.py`, `dag3.py` para dentro dela.
2. **Renomear** `requiriments.txt` → `requirements.txt` e garantir conteúdo mínimo:
   ```txt
   apache-airflow==2.10.*
   pymysql
   hdfs
   ```
3. **Corrigir credenciais** em DAGs:
   ```python
   pymysql.connect(
       host='mysql',
       user='root',
       password='fiapOn',  # ou variável de ambiente
       database='dbfiapon',
   )
   ```
4. **Popular MySQL automaticamente (opcional):** coloque `data.sql` em `./mysql-init/` e monte em `/docker-entrypoint-initdb.d/` no serviço MySQL.

## 🧩 Compose de referência (exemplo funcional)
Use-o para **comparar** com o seu. **Ajuste portas/versões conforme necessidade**.

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-fiapOn}
      MYSQL_DATABASE: ${MYSQL_DATABASE:-dbfiapon}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql-init:/docker-entrypoint-initdb.d:ro

  hadoop:
    image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
    container_name: hadoop
    environment:
      CLUSTER_NAME: local-hadoop
    ports:
      - "9870:9870"   # Web UI NameNode
      - "9000:9000"   # RPC NameNode
    volumes:
      - hadoop_data:/hadoop/dfs/name

  airflow:
    image: apache/airflow:2.10.2
    container_name: airflow
    environment:
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
      AIRFLOW__WEBSERVER__SECRET_KEY: 'change-me'
      _PIP_ADDITIONAL_REQUIREMENTS: ""
    user: "0:0"
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./requirements.txt:/requirements.txt:ro
      - airflow_logs:/opt/airflow/logs
    depends_on:
      - mysql
    command: >
      bash -c "pip install -r /requirements.txt &&
               airflow db init &&
               airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin &&
               airflow scheduler & exec airflow webserver"

volumes:
  mysql_data:
  hadoop_data:
  airflow_logs:
```

> **Dica:** se preferir um único contêiner Hadoop all-in-one (para testes), você pode usar `bde2020/hadoop:latest` e expor `9870`.

## 🐍 Exemplo mínimo de DAG (corrigido)
Coloque em `dags/dag1.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pymysql
from hdfs import InsecureClient

def transform_and_save_to_hadoop():
    conn = pymysql.connect(
        host='mysql',
        user='root',
        password='fiapOn',
        database='dbfiapon',
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome FROM tabela1")
            data = cur.fetchall()
        transformed = [f"{row[0]}, {row[1]}" for row in data]

        hdfs = InsecureClient('http://hadoop:9870', user='hadoop')
        with hdfs.write('/user/hadoop/tabela1_output.txt', encoding='utf-8') as w:
            for line in transformed:
                w.write(line + "\\n")
    finally:
        conn.close()

with DAG(
    dag_id='dag1',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False,
) as dag:
    task = PythonOperator(
        task_id='transform_and_save_to_hadoop',
        python_callable=transform_and_save_to_hadoop,
    )
```

## 🚀 Como subir o ambiente
1. **Pré-requisitos:** Docker e Docker Compose v2.
2. (Opcional) Crie um `.env` na raiz:
   ```env
   MYSQL_ROOT_PASSWORD=fiapOn
   MYSQL_DATABASE=dbfiapon
   ```
3. Suba os serviços:
   ```bash
   docker compose up -d
   ```
4. Acesse:
   - Airflow: http://localhost:8080 (usuário/senha conforme criado no comando)
   - MySQL: `localhost:3306` (root / `fiapOn` por padrão)
   - HDFS NameNode UI: http://localhost:9870

## 🧪 Testes rápidos
- Verifique Airflow **DAGs** aparecendo na UI.
- No MySQL, crie `tabela1` e insira registros (ou use `data.sql` via `mysql-init/`).
- Rode a DAG e confirme `tabela1_output.txt` no HDFS.

## 🔐 Boas práticas
- Nunca commitar senhas reais. Use `.env` ou `secrets`.
- Fixar versões das imagens para reprodutibilidade.
- Parametrizar conexões no Airflow (Connections/Variables) ao invés de strings fixas no código.

## 🛠️ Troubleshooting
- **Airflow não sobe / dá erro no `requirements.txt`:** confira nome correto, conteúdo e permissões de montagem.
- **DAG não aparece:** verifique se está em `dags/` e se não há erros de sintaxe (veja logs do scheduler).
- **HDFS write falha:** valide se a porta `9870` está exposta e o path `/user/hadoop/` existe.
- **MySQL init não rodou:** confirme a pasta `./mysql-init/` e logs do contêiner MySQL.

---

Feito com 💚 para acelerar seu ambiente de dados.
