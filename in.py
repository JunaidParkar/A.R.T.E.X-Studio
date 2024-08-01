import click, inquirer, os, json, shutil

@click.group()
def artex():
    pass

@click.command()
def init():
    with open(os.path.join(os.getcwd(), "config.json"), "r") as f:
        config = json.load(f)
        f.close()
    required_libraries = [lib for lib in config["requiredLibraries"]]
    lib_dir = os.path.join(os.getcwd(), "library")
    if not os.path.isdir(lib_dir):
        os.mkdir(lib_dir)
    else:
        print("Library folder already exist. Kindly delete that folder initialize again")


@click.command()
def pack():
    print("packing")

@click.command()
def build():
    print("building")

artex.add_command(init)
artex.add_command(pack)
artex.add_command(build)

artex()