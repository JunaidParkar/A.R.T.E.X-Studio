import os, shutil, json
from rich import print
from inquirer import confirm, text
from choice import get_choice, get_choices_with_checkboxes

class studio:
    def __init__(self, cwd) -> None:
        self.__cwd = cwd

    def __copy(self, f, t):
        print("\n")
        try:
            shutil.copy(src=f, dst=t)
            print(f"[green italic]Building libraries at {t}[/green italic]")
            return True
        except Exception as er:
            print("[green italic]An error occured while building libraries")
            return False
        
    def __delete_all_contents(self, t):
        print("\n")
        if os.path.exists(t):
            shutil.rmtree(t)
            print(f"[green italic]All contents of '{t}' have been deleted.[/green italic]")
        else:
            print(f"[green italic]Directory '{t}' does not exist.[/green italic]")

    def init(self):
        print("\n")
        app_name = text(message="Enter the name for your application.")
        app_version = text(message="Enter version for your app.")
        app_libraries = get_choices_with_checkboxes(["cursor.js", "dkit.js", "CREngine.js", "anime.js", "chart.js", "gsap.js"])
        app_publisher = text(message="Enter publisher name.")
        data = {
            "name": app_name,
            "version": app_version,
            "packageName": f"artex.{app_name}",
            "requiredLibraries": app_libraries,
            "publisher": app_publisher,
            "includeDir": []
        }
        with open(os.path.join(self.__cwd, "config.json"), 'w') as file:
            json.dump(data, file, indent=4)
        print("\n")
        print("[green italic]Creating a folder library[/green italic]")
        os.mkdir(os.path.join(self.__cwd, "library"))
        lib_path = []
        for lib in app_libraries:
            for root, dirs, files in os.walk(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Common")):
                for file in files:
                    if os.path.join(root, file).endswith(lib):
                        lib_path.append(os.path.join(root, file))
        for file in lib_path:
            self.__copy(f=file, t=os.path.join(self.__cwd, "library"))
        print("\n")
        print("[green italic]Creating an assets folder.[/green italic]")
        os.mkdir(os.path.join(self.__cwd, "assets"))
        print("[green italic]Creating an src folder.[/green italic]")
        os.mkdir(os.path.join(self.__cwd, "src"))
        print("\n")
        print("[green italic]Creating index.html.[/green italic]")
        html_data = f"""<!DOCTYPE html>\n<html lang="en">\n\n<head>\n\t<meta charset="UTF-8">\n\t<meta name="viewport" content="width=device-width, initial-scale=1.0">\n\t<title>{app_name}</title>\n</head>\n\n<body>\n\n"""
        for libr in app_libraries:
            html_data += f"\n<script src='library/{libr}' ></script>"
        html_data += """\n</body>\n\n</html>"""
        with open(os.path.join(self.__cwd, "index.html"), "w") as h:
            h.write(html_data)
        print("\n")
        print("[green italic]Your project have been initialized. If you want to add any library later then you can use command `artex addLibrary` in your current working directory.[/green italic]")
        print("[red bold]Note: config.json must not be deleted.[/red bold]")
        print("[red bold]Note: index.html in root directory is your entry point.[/red bold]")
        print("[red bold]Note: All of the files you create manually like html, css or js everything should be done inside 'src' folder.[/red bold]")
        print("[red bold]Note: If you create any other folder manually in the root directory then you need to add name of that folder while build process when it will be asked.[/red bold]")
        print("[red bold]Note: All the assets of your application must be inside assets folder excluding your app icon.[/red bold]")
        print("[red bold]Note: Apps icon name should be icon.jpg.[/red bold]")
        print("[red bold]Note: Apps icon should be in root directory of project.[/red bold]")

    def addLibrary(self):
        pass

    def build(self):
        with open(os.path.join(self.__cwd, "config.json"), "r") as f:
            config = json.load(f)
            f.close()