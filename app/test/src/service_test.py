import unittest
from unittest.mock import patch, Mock, ANY
from google.cloud import bigquery
from app.src.main import delete_data, InitMessage  # Remplacez my_api par le nom de votre fichier Python


class TestDeleteData(unittest.TestCase):

    @patch('google.cloud.bigquery.Client')
    def test_delete_data(self, mock_bigquery_client):
        # Créer un message d'initialisation factice

        init_messag = InitMessage(raw_pattern="test",id_traitement="",ts_vac="2024-06-01",
                                  is_update=False,other_field="others")

        # Mock du client BigQuery et de ses méthodes
        mock_client_instance = mock_bigquery_client.return_value
        mock_client_instance.query.return_value.result.return_value = None

        # Appeler la fonction delete_data avec le client mocké et le message d'initialisation
        delete_data(mock_client_instance, init_messag)

        # Construire la requête SQL attendue
        table_id = f"sbx-mydataplatform.test.table_item"

        # Construire la requête SQL de suppression
        query = f""" DELETE FROM `{table_id}` WHERE ts_vac = @ts_vac_value """

        # Vérifier que la méthode query a été appelée
        mock_client_instance.query.assert_called_once()

        # Vérifier les arguments passés à la méthode query
        called_args, called_kwargs = mock_client_instance.query.call_args
        self.assertEqual(called_args[0].strip(), query.strip())

        # Vérifier le contenu du job_config
        job_config = called_kwargs['job_config']
        self.assertIsInstance(job_config, bigquery.QueryJobConfig)
        self.assertEqual(job_config.query_parameters[0].name, "ts_vac_value")
        self.assertEqual(job_config.query_parameters[0].type_, "STRING")
        self.assertEqual(job_config.query_parameters[0].value, "2024-06-01")

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("ts_vac_value", "STRING", init_messag.ts_vac)
            ]
        )


        # Vérifier que la méthode query a été appelée avec les bons paramètres
        mock_client_instance.query.assert_called_once_with(
            query,
            job_config=ANY  # Vérifie que job_config est passé, sans vérifier les détails
        )

        print("Test pour delete_data passé")



