import click
import MetaTrader5 as mt5
from manipulation import manipulation
import logging

logger = logging.getLogger("Tradepal")
logger.root


@click.group(help="A command-line tool for getting convenient trading stats based on the MetaTrader 5")
@click.option("--path", help="Path to the MetaTrader5 terminal EXE file.", default=None, required=False)
@click.option("-u", "--username", help="Username of a MetaTrader5 account", default=None, required=False)
@click.option("-p", "--password", help="Password of a MetaTrader5 account", default=None, required=False)
@click.option("-s", "--server", help="The MetaTrader5 server address", default=None, required=False)
@click.option("-l", "--log_level", help="Sets the level of the logger (info, warn, error, debug)", default="info", required=False, show_default=True)
def tradepal(path, username, password, server, log_level: str):
    log_level = log_level.lower()
    if log_level == "info":
        log_level = logging.INFO
    elif log_level == "warn":
        log_level = logging.WARN
    elif log_level == "error":
        log_level = logging.ERROR
    elif log_level == "debug":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)
    if not mt5.initialize():
        logger.critical("Could not connect ot the MetaTrader5")


tradepal.add_command(manipulation)


if __name__ == '__main__':
    tradepal()
