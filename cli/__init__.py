import logging
from cli.cli import cli

def run_cli():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s  %(message)s')
    cli()
