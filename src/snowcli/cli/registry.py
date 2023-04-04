from __future__ import annotations

import typer
import json
import snowflake.connector
from rich import print
from snowcli import config
from snowcli.config import AppConfig
 

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})
EnvironmentOption = typer.Option("dev", help="Environment name")

@app.command("token")
def get_token(
    environment: str = EnvironmentOption,
):
    """
    Get token to authenticate with registry.
    """
    AppConfig().config.get(environment)
    if config.isAuth():
        config.connectToSnowflake()
        # inject the session parameters
        config.snowflake_connection.connection_config['session_parameters'] = {"PYTHON_CONNECTOR_QUERY_RESULT_FORMAT": "json"}
        config.snowflake_connection.ctx = snowflake.connector.connect(**config.snowflake_connection.connection_config)
        # disable session deletion
        config.snowflake_connection.ctx._all_async_queries_finished = lambda _: False 
        if config.snowflake_connection.ctx._rest is None:
            raise Exception("error in connection object")
        # obtain and create the token 
        token_data = config.snowflake_connection.ctx._rest._token_request('ISSUE')
        token = {'token': token_data['data']['sessionToken'],'expires_in': token_data['data']['validityInSecondsST']}
        tok = json.dumps(token)
        print("Session token for connection ", config.snowflake_connection.connection_name, " : \n", tok)