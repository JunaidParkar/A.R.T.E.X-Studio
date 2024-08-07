import click, inquirer, os, json, shutil
from rich import print
from inquirer import confirm, prompt
from Supplier import Studio

a = Studio(os.getcwd())

def copy(fromPath: str, toPath: str):
    print("\n")
    try:
        shutil.copy(src=fromPath, dst=toPath)
        print(f"[green italic]Building library at {os.path.normpath(toPath)}[/green italic]")
        return True
    except Exception as er:
        print("[red italic]An error occured while building libraries.[/red italic]")
        return False

def delete_all_contents(target_directory):
    print("\n")
    if os.path.exists(target_directory):
        shutil.rmtree(target_directory)
        print(f"[green italic]All contents of '{target_directory}' have been deleted.[/green italic]")
    else:
        print(f"[green italic]Directory '{target_directory}' does not exist.[/green italic]")


@click.group()
def artex():
    pass

@click.command()
def init():
    a.init()


@click.command()
def pack():
    print("packing")

@click.command()
def build():
    a.build()

artex.add_command(init)
artex.add_command(pack)
artex.add_command(build)

artex()