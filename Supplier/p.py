import os
import shutil
import json
from rich import print
from bs4 import BeautifulSoup
from inquirer import confirm, text
from .choice import get_choice, get_choices_with_checkboxes

class Packer:
    def __init__(self, cwd) -> None:
        self.__cwd = cwd
        self.__basic_config_cleared = True
        self.__available_libraries = []
        self.__html_lists = []
        for root, dirs, files in os.walk(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../Common")):
            for file in files:
                if os.path.join(root, file).endswith(".js"):
                    self.__available_libraries.append(file)

    def __check_basic_configurations(self):
        print("checking")
        if not os.path.isfile(os.path.join(self.__cwd, "config.json")):
            print("[red italic]Error: config.json is not available in your project. Kindly Re-Initialize the project carefully")
            self.__basic_config_cleared = False
            return
        
        if not os.path.isfile(os.path.join(self.__cwd, "icon.png")):
            self.__basic_config_cleared = False
            print("[red italic]Error: icon.png is not found in main directory.[red italic]")
            return
        
        if not os.path.isfile(os.path.join(self.__cwd, "index.html")):
            self.__basic_config_cleared = False
            print("[red italic]Error: Entry point index.html is not found.")

        with open(os.path.join(self.__cwd, "config.json"), 'r') as j:
            cfg = json.load(j)
            j.close()
        
        try:
            for f in cfg["includeDir"]:
                cl = True if os.path.isdir(os.path.join(self.__cwd, f)) else False
                if not cl:
                    print(f"[red italic]Error: {os.path.normpath(os.path.join(self.__cwd, f))} is unavailable or is invalid directory")
                    self.__basic_config_cleared = False
                    return
        except:
            self.__basic_config_cleared = False
            print("[red italic]Error: config.json is corrupted.")

        for l in cfg["requiredLibraries"]:
            if not l in self.__available_libraries:
                self.__basic_config_cleared = False
                print(f"[red italic]Error: Unknown library {l} is added in config.json")
                return
            
        if not cfg["name"]:
            self.__basic_config_cleared = False
            print("[red italic]Error: App name is not defined in config.json[/red italic]")
            return
        
        if not cfg["packageName"]:
            self.__basic_config_cleared = False
            print("[red italic]Error: App package name is not defined in config.json[/red italic]")
            return
        
        if not cfg["version"]:
            self.__basic_config_cleared = False
            print("[red italic]Error: App version is not defined in config.json[/red italic]")
            return
        
        if cfg["packageName"] != f"artex.{cfg['name'].lower()}":
            self.__basic_config_cleared = False
            print(f"[red italic]Error: App package name should be artex.{cfg['name'].lower()}.[/red italic]")
            return
            
    def __list_htmls(self):
        with open(os.path.join(self.__cwd, "config.json"), 'r') as j:
            cfg = json.load(j)
            j.close()
        
        self.__html_lists.append(os.path.join(self.__cwd, "index.html"))

        for p in cfg["includeDir"]:
            if p:
                for root, dirs, files in os.walk(os.path.join(self.__cwd, p)):
                    for file in files:
                        if file.endswith(".html"):
                            self.__html_lists.append(os.path.join(root, file))

    def __update_html_script_src(self):
        for file_path in self.__html_lists:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                script_tags = soup.find_all('script')
                for script_tag in script_tags:
                    src = script_tag.get('src', '')
                    if any(src.endswith(service) for service in self.__available_libraries):
                        script_tag["src"] = os.path.normpath(os.path.join(os.path.relpath(self.__cwd, os.path.dirname(file_path)), f"../../Common/{src.split(os.path.dirname(src))[1]}"))

                with open(file_path, 'w', encoding='utf-8') as m_file:
                    m_file.write(str(soup))
                print(f"Updated script src in {file_path}")

            except Exception as e:
                print(f"Error updating {file_path}: {e}")

    def builder(self):
        self.__check_basic_configurations()
        if not self.__basic_config_cleared:
            return
        self.__list_htmls()
        self.__update_html_script_src()
