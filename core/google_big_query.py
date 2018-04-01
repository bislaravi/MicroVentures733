from google.cloud import bigquery
import pandas as pd


class GoogleBigQuery(object):

    def __init__(self):
        self.client = bigquery.Client.from_service_account_json('key.json')

    def execute_query_df(self, query):
        query_job = self.client.query(query)
        iterator = query_job.result(timeout=30)
        rows = list(iterator)
        return pd.DataFrame(
            data=[list(x.values()) for x in rows],
            columns=list(rows[0].keys()))

    def export_table_data_to_csv(self, data_set_id, table_id, destination):
        dataset_ref = self.client.dataset(data_set_id)
        table_ref = dataset_ref.table(table_id)
        job = self.client.extract_table(table_ref, destination)
        job.result()  # Waits for job to complete
        print('Exported {}:{} to {}'.format(
            data_set_id, table_id, destination))


big_query = GoogleBigQuery()
