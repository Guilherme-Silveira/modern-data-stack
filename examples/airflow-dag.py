from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator

with DAG(dag_id='dbt-delta',
          default_args={'owner': 'airflow'},
          schedule_interval='@weekly',
          start_date=days_ago(1)
    ) as dag:

    airbyte_sync_customers = AirbyteTriggerSyncOperator(
      task_id='airbyte-customers',
      airbyte_conn_id='airbyte',
      connection_id='0c5af1ab-e900-4fdb-9708-8c7bec4d459e',
      asynchronous=False,
      timeout=7200,
      wait_seconds=3
    )

    airbyte_sync_orders = AirbyteTriggerSyncOperator(
      task_id='airbyte-orders',
      airbyte_conn_id='airbyte',
      connection_id='7d7ea77c-ba2f-4b2b-9617-a43939e57e39',
      asynchronous=False,
      timeout=7200,
      wait_seconds=3
    )

    run_dbt_delta = KubernetesPodOperator(
      task_id='run-dbt-delta',
      name='run-dbt-delta',
      image='guisilveira/dbt-jaffle-shop-delta',
      namespace='mds',
      in_cluster=True
    )

    run_dbt_iceberg = KubernetesPodOperator(
      task_id='run-dbt-iceberg',
      name='run-dbt-iceberg',
      image='guisilveira/dbt-jaffle-shop-iceberg',
      namespace='mds',
      in_cluster=True
    )

    airbyte_sync_customers >> [run_dbt_delta, run_dbt_iceberg]
    airbyte_sync_orders >> [run_dbt_delta, run_dbt_iceberg]
