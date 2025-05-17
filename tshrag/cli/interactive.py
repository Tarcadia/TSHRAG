
# -*- coding: UTF-8 -*-


from typing import List

import click
from ..tshrag import Tshrag



def merge_cli(clis : List[click.Group]) -> click.Group:
    cli = click.Group()
    for _c in clis:
        for cmd_name, cmd in _c.commands.items():
            if cmd_name in cli.commands:
                raise ValueError(f"Command {cmd_name} already exists in CLI")
            cli.add_command(cmd)
    return cli



def InteractiveCLI(tshrag: Tshrag) -> click.Group:
    cli = click.Group()


    @cli.command()
    def exit():
        """Exit the CLI."""
        click.echo("Exiting...")
        raise click.Abort()


    return cli

