import requests
import os
from Log import logger

class ChorusAPI:
    def __init__(self, session_id, chorus_address="http://localhost:8080"):
        self.session_id = session_id
        self.chorus_address = chorus_address
        self.uri = self.chorus_address.rstrip("/") + "/%s" + "?session_id=" + self.session_id
        self.cert = False

    def set_ssl_verify(self, cert_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../certfile")):
        self.cert = cert_path if os.path.exists(cert_path) else False

    def hdfs_ls(self, datasource_name, path, **kwargs):
        uri = self.uri % ("hdfs_files_by_path/list")
        kwargs["hdfs_data_source_name"] = datasource_name
        kwargs["path"] = path
        logger.debug("get " + uri)
        logger.debug("params:" + str(kwargs))

        response = requests.get(uri, params=kwargs, verify=kwargs.get("verify", self.cert))
        return response

    def get_data_from_hdfs_datasource(self, datasource_name, path, **kwargs):
        uri = self.uri % ("hdfs_files_by_path/contents")
        kwargs["hdfs_data_source_name"] = datasource_name
        kwargs["path"] = path
        logger.debug("get " + uri)
        logger.debug("params:" + str(kwargs))
        response = requests.get(uri, params=kwargs, verify=kwargs.get("verify", self.cert))
        return response

    def import_data_to_hdfs_datasource(self, datasource_name, data, path, **kwargs):
        uri = self.uri % ("hdfs_files_by_path/import")
        kwargs["hdfs_data_source_name"] = datasource_name
        kwargs["path"] = path
        logger.debug("get " + uri)
        logger.debug("params:" + str(kwargs))
        files = {'file': ('upload.csv', data)}
        response = requests.post(uri, params=kwargs, files=files, verify=kwargs.get("verify", self.cert))
        return response

    def sql_execute(self, data_source_name, sql, schema_name=None, database_name="public", **kwargs):
        assert (database_name is not None)

        uri = self.uri % ("db_execute/sql")
        kwargs["data_source_name"] = data_source_name
        kwargs["database"] = database_name

        if schema_name is not None:
            kwargs["schema"] = schema_name

        files = {'file': ("upload.sql", sql)}
        logger.debug("post " + uri)
        logger.debug("params:" + str(kwargs))
        logger.debug("sql:" + str(sql))

        response = requests.post(uri, params=kwargs, files=files,  verify=kwargs.get("verify", self.cert))
        return response


if __name__ == "__main__":
    capi = ChorusAPI("7e0d8d046a3a059dccc2a8e30c7f7552575977ca", chorus_address="http://localhost:8080")
    response = capi.get_data_from_hdfs_datasource("CDH5_HA", "/automation_test_data/csv/apple_customers.csv")
    print response.json()

    response = capi.get_data_from_hdfs_datasource("CDH5_HA", "/automation_test_data/csv", first_row_is_header="true",max="5")
    print response.json()

    response = capi.get_data_from_db_datasource("HAWQ1.3_PHD3.0", "miner_demo.demo.account")
    print response.json()
    response = capi.sql_execute("HAWQ1.3_PHD3.0", "demo", "select * from \"account\"")
    print response.json()

    # Hao, some examples:
    # r = capi.sql_execute(data_source_name='local-greenplum',
    #                  data_source_schema='test_schema',
    #                  sql='select * from "master_table1"')
    # chorus_query_to_df(r.json())

    # create_sql = '''
    # CREATE TABLE films (
    # code        char(5) CONSTRAINT firstkey PRIMARY KEY,
    # title       varchar(40) NOT NULL,
    # did         integer NOT NULL,
    # date_prod   date,
    # kind        varchar(10),
    # len         interval hour to minute
    # )
    # '''
    # r = capi.sql_execute(data_source_name='local-greenplum',
    #                  data_source_schema='test_schema',
    #                  sql=create_sql)
    # print r.json()
    #
    # insert_sql = '''
    # INSERT INTO films (code, title, did, date_prod, kind) VALUES
    #     ('B6717', 'Tampopo', 110, '1985-02-10', 'Comedy'),
    #     ('HG120', 'The Dinner Game', 140, DEFAULT, 'Comedy')
    # '''
    # r = capi.sql_execute(data_source_name='local-greenplum',
    #                  data_source_schema='test_schema',
    #                  sql=insert_sql)
    # print r.json()
    #
    # r = capi.sql_execute(data_source_name='local-greenplum',
    #                  data_source_schema='test_schema',
    #                  sql='select * from "films"')
    #
    # df = chorus_query_to_df(r.json())
    # print df
