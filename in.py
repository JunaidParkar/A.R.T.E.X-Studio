import click, inquirer, os, json, shutil

def copy(fromPath: str, toPath: str):
    try:
        shutil.copy(src=fromPath, dst=toPath)
        print("copying")
        return True
    except Exception as er:
        print("error")
        return er

def delete_all_contents(target_directory):
    if os.path.exists(target_directory):
        shutil.rmtree(target_directory)
        print(f"All contents of '{target_directory}' have been deleted.")
    else:
        print(f"Directory '{target_directory}' does not exist.")


@click.group()
def artex():
    pass

@click.command()
def init():
    with open(os.path.join(os.getcwd(), "config.json"), "r") as f:
        config = json.load(f)
        f.close()
    required_libraries = [lib for lib in config["requiredLibraries"]]
    if os.path.isdir(os.path.join(os.getcwd(), "library")):
        print("Library folder already exist. Kindly delete that folder initialize again")
        delete_all_contents(os.path.join(os.getcwd(), "library"))
    os.mkdir(os.path.join(os.getcwd(), "library"))
    lib_path = []
    for lib in required_libraries:
        for root, dirs, files in os.walk(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Common")):
            for file in files:
                if os.path.join(root, file).endswith(lib):
                    lib_path.append(os.path.join(root, file))
    print(lib_path)
    for file in lib_path:
        copy(fromPath=file, toPath=os.path.join(os.getcwd(), "library"))
        pass


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