from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pymysql
from hdfs import InsecureClient
 
def transform_and_save_to_hadoop():
    # Conectar ao MySQL
    mysql_conn = pymysql.connect(
        host='mysql',
        user='root',
        password=fiapOn,
        database='dbfiapon'
    )
    
    # Conectar ao HDFS
    hdfs_client = InsecureClient('http://hadoop:9870', user='hadoop')
 
    with mysql_conn.cursor() as cursor:
        cursor.execute("SELECT * FROM tabela2")
        data = cursor.fetchall()
 
        # Exemplo de transformação (aqui você pode adicionar lógica)
        transformed_data = [f"{item[0]}, {item[1]}" for item in data]
 
        # Salvar no HDFS
        hdfs_path = '/user/hadoop/tabela2_output.txt'
        with hdfs_client.write(hdfs_path, encoding='utf-8') as writer:
            for line in transformed_data:
                writer.write(line + '\n')
 
    mysql_conn.close()
 
with DAG(dag_id='dag2', start_date=datetime(2023, 1, 1), schedule_interval='@daily') as dag:
    task1 = PythonOperator(task_id='transform_and_save_to_hadoop', python_callable=transform_and_save_to_hadoop)
 
task1