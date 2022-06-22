#this is the installer for any of the toine34 apps

import os
import sys
import tkinter as tk
from tkinter import Variable, ttk, filedialog

from requests import get
from tkhtmlview import HTMLLabel
from markdown import markdown

APP = "Blueprint-Manager" #Must be the name of the github repo


URL = "https://github.com/T0ine34/%s"                           #! Do not change this
RAWURL = "https://raw.githubusercontent.com/T0ine34/%s"         #! Do not change this
APIREPOURL = "https://api.github.com/repos/T0ine34/%s"          #! Do not change this
APIUSERURL = "https://api.github.com/users/T0ine34/repos"       #! Do not change this

def md2html(md):
    '''
    Convert markdown to html
    '''
    return markdown(md)

def load_rules(app):
    '''
    Load the rules from the rules.md file on github using github api
    '''
    rules = get((RAWURL %app )+"/main/rules.md").text
    if rules != "404: Not Found":
        print ("Loaded rules for %s" %app)
        return md2html(rules)
    else:
        print ("No rules found for %s" %app)
        return "Rules not found"

def get_releases(app):
    '''
    Load the list of releases from the github api
    '''
    print("Getting releases for %s :" %app)
    releases = []
    json = get((APIREPOURL %app )+"/releases").json()
    for i in range(len(json)):
        print('\t'+json[i]['tag_name'], end = '---')
        if json[i]['tag_name'].startswith('v'):
            print("loaded")
            releases.append(json[i]['tag_name'])
        else:
            print("skipped")
    return releases

def get_apps():
    '''
    Load the list of apps from the github api
    '''
    print("Getting apps :")
    apps = []
    json = get(APIUSERURL).json()
    for i in range(len(json)):
        print('\t'+json[i]['name'], end = '---')
        if not (json[i]['name'] in ('T0ine34', 'Installer') or json[i]['name'].startswith('_')):
            print("loaded")
            apps.append(json[i]['name'])
        else:
            print("skipped")
    return apps
    

class Listbox_Scrollable(tk.Frame):
    """
    Listbox with vertical scrollbar
    Usage is the same as the standard Tkinter listbox
    """
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent)
        self.listbox = tk.Listbox(self, *args, **kwargs)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        __doc__ = self.listbox.__doc__

    def __getattr__(self, attr):
        # Delegate attribute to listbox
        return getattr(self.listbox, attr)

    def bind(self, *args, **kwargs):
        # Delegate bind to listbox
        return self.listbox.bind(*args, **kwargs)


class Path_Input(tk.Frame):
    """
    Input field for path, with a button to open a file dialog
    Store the path in the variable var
    """
    def __init__(self, parent, var, *args, **kwargs):
        tk.Frame.__init__(self, parent)
        self.var = var
        self.entry = tk.Entry(self, textvariable=self.var, *args, **kwargs)
        self.entry.pack(side="left", fill="x", expand=True)
        self.button = tk.Button(self, text="Browse", command=self.browse)
        self.button.pack(side="right")

        __doc__ = self.entry.__doc__

    def browse(self):
        '''
        open a file dialog and set the path
        '''
        self.var = filedialog.askdirectory()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.var)



    def __getattr__(self, attr):
        # Delegate attribute to stringvar
        return getattr(self.var, attr)

    def is_valid(self, event=None):
        '''
        return if the path is valid
        '''
        return os.path.exists(self.var)







class Installer(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Blueprint Manager Installer")
        #set size of window
        self.geometry("600x500")
        self.resizable(False, False)

        self.content = tk.Frame(self, background="white", height=400, width=600)
        self.content.pack(fill="both", expand=True)

        self.current_step = 0 #0 = welcome, 1 = accept conditions, 2 = choose version,3 = choice of paths, 4 = download & install, 5 = finish

        self.next_button = tk.Button(self, text="Next", command=self.next)
        self.previous_button = tk.Button(self, text="Previous", command=self.previous, state="disabled")

        self.list_apps = get_apps()
        self.list_releases = []
        self.rules = ""
        self.path = ""
        self.app = {}
        self.version = ""
        self.__init_steps__()

        self.update_step()

        
        self.next_button.pack(side="right")

        self.previous_button.pack(side="right")

    def get_app_info(self, app):
        """get the info (releases & rules) of the app"""
        self.list_releases = get_releases(app)
        self.rules = load_rules(app)

    def previous(self):
        self.current_step -= 1
        self.update_step()
        if self.current_step == 0:
            self.previous_button.config(state="disabled")
        elif self.current_step == 6:
            self.next_button.config(text="Install")
        elif self.current_step < 6:
            self.next_button.config(text="Next")
        self.next_button.config(state="normal")
    


    def next(self):
        self.current_step += 1
        self.update_step()
        if self.current_step == 5:
            self.next_button.config(text="Install")
        elif self.current_step == 6:
            self.next_button.config(text="Please wait...")
            self.next_button.config(state="disabled")
        elif self.current_step == 7:
            self.next_button.config(text="Close", command=self.close)

        if self.current_step > 0:
            self.previous_button.config(state="normal")
        else:
            self.previous_button.config(state="disabled")

    def close(self):
        self.destroy()

    def __init_steps__(self):
        self.choose_app()
        self.welcome()
        self.accept_conditions()
        self.choose_version()
        self.choose_paths()
        self.confirm()
        self.download_install()
        self.finish()

    def update_step(self):
        self.f_welcome.pack_forget()
        self.f_choose_app.pack_forget()
        self.f_accept_conditions.pack_forget()
        self.f_choose_version.pack_forget()
        self.f_choose_paths.pack_forget()
        self.f_confirm.pack_forget()
        self.f_download_install.pack_forget()
        self.f_finish.pack_forget()
        if self.current_step == 0:
            self.f_welcome.pack(fill="both", expand=True)
        elif self.current_step == 1:
            self.f_choose_app.pack(fill="both", expand=True)
            self.next_button.bind("<Button-1>", self.choose_app_event)
            self.next_button.config(state="disabled")
        elif self.current_step == 2:
            self.next_button.config(state="disabled")
            self.f_accept_conditions.pack(fill="both", expand=True)
        elif self.current_step == 3:
            self.next_button.config(state="disabled")
            self.f_choose_version.pack(fill="both", expand=True)
        elif self.current_step == 4:
            self.next_button.config(state="disabled")
            self.f_choose_paths.pack(fill="both", expand=True)
        elif self.current_step == 5:
            self.confirm()
            self.f_confirm.pack(fill="both", expand=True)
        elif self.current_step == 6:
            self.f_download_install.pack(fill="both", expand=True)
        elif self.current_step == 7:
            self.f_finish.pack(fill="both", expand=True)

    #create differents frames for each step. Each frame will be grid in the main window, and start invisible.


    def welcome(self):
        self.f_welcome = tk.Frame(self.content, background="white")
        
        tk.Label(self.f_welcome, text="Welcome to the Toine34 app installer", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)
        tk.Label(self.f_welcome, text="This program will guide you through the installation of a Toine34 app.",
            font="Helvetica 10", background="white").pack(fill="both", expand=True)


    def choose_app(self):
        """allow the user to choose the app to install and allow him to continue only if he chose an app"""
        self.f_choose_app = tk.Frame(self.content, background="white")
        tk.Label(self.f_choose_app, text="Choose the app you want to install", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)
        self.listbox = Listbox_Scrollable(self.f_choose_app, background="white", height=10, width=30)
        for app in self.list_apps:
            self.listbox.insert("end", app)
        self.listbox.bind("<<ListboxSelect>>", self.listbox_choosed)
        self.listbox.pack(fill="both", expand=True)

    def listbox_choosed(self, event):
        self.app = self.list_apps[self.listbox.curselection()[0]]
        self.next_button.config(state="normal")
    
    def choose_app_event(self, event):
        """when the user choose an app, get the info of the app (releases & rules)"""
        self.get_app_info(self.listbox.get(self.listbox.curselection()))
        self.accept_conditions()
        self.choose_version()
        self.next_button.unbind("<Button-1>")

        
        
    def accept_conditions(self):
        self.f_accept_conditions = tk.Frame(self.content, background="white")
        tk.Label(self.f_accept_conditions, text="Accept the following conditions", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True) 
        HTMLLabel(self.f_accept_conditions, html=self.rules, font="Helvetica 10", background="white").pack(fill="both", expand=True)
        self.accept_conditions_var = tk.IntVar()
        self.accept_conditions_var.set(0)
        tk.Checkbutton(self.f_accept_conditions, text="I accept the terms and conditions", variable=self.accept_conditions_var,
            background="white").pack(fill="both", expand=True)
        self.accept_conditions_var.trace("w", self.accept_conditions_changed)


    def accept_conditions_changed(self, *args):
        if self.accept_conditions_var.get() == 1:
            self.next_button.config(state="normal")
        else:
            self.next_button.config(state="disabled")

    def choose_version(self):
        self.f_choose_version = tk.Frame(self.content, background="white")
        tk.Label(self.f_choose_version, text="Choose the version of the Blueprint Manager", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)
        #create a scrollable list of releases
        self.list_releases_var = tk.StringVar()
        if len(self.list_releases) > 0:
            self.list_releases_var.set(self.list_releases[0])
        
        self.version_menu = Listbox_Scrollable(self.f_choose_version, width = 20, height = 20, listvariable = self.list_releases_var)

        for release in self.list_releases[1:]:
            self.version_menu.insert(tk.END, release)
        self.version_menu.pack()
        self.version_menu.bind("<<ListboxSelect>>", self.choose_version_changed)

    def choose_version_changed(self, *args):
        self.version = self.list_releases[self.version_menu.curselection()[0]]
        self.next_button.config(state="normal")




    def choose_paths(self):
        """create a 1 line height input for the user to choose the path of the app"""
        self.f_choose_paths = tk.Frame(self.content, background="white")
        tk.Label(self.f_choose_paths, text="Choose the installation path", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)
        self.path_strvar = tk.StringVar()
        self.path_input = Path_Input(self.f_choose_paths, self.path_strvar, background="white")
        #verify if the path is valid at each update of the path_input. if it is, enable the next button.
        self.path_input.trace_add("write", self.path_input_changed)
        self.path_input.pack(fill="both", expand=True)

    def path_input_changed(self, *args):
        if self.path_input.is_valid():
            self.path = self.path_strvar.get()
            self.next_button.config(state="normal")
        else:
            self.next_button.config(state="disabled")

    def confirm(self):
        self.f_confirm = tk.Frame(self.content, background="white")
        tk.Label(self.f_confirm, text="Confirm the installation", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)

        if self.path != "":
            tk.Label(self.f_confirm, text="The following app will be installed in the following path:",
                font="Helvetica 10", background="white").pack(fill="both", expand=True)
            tk.Label(self.f_confirm, text=self.path, font="Helvetica 10", background="white").pack(fill="both", expand=True)

        if self.app != {}:
            tk.Label(self.f_confirm, text="The following application will be installed:",
                font="Helvetica 10", background="white").pack(fill="both", expand=True)
            tk.Label(self.f_confirm, text=self.app, font="Helvetica 10", background="white").pack(fill="both", expand=True)

        if self.version != "":
            tk.Label(self.f_confirm, text="The following version will be installed:",
                font="Helvetica 10", background="white").pack(fill="both", expand=True)
            tk.Label(self.f_confirm, text=self.version,  font="Helvetica 10", background="white").pack(fill="both", expand=True)
        


    def download_install(self):
        """download the app and install it in the folder "path"."""
        self.f_download_install = tk.Frame(self.content, background="white")
        tk.Label(self.f_download_install, text="Download and install the Blueprint Manager", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)

    def installation_complete(self):
        self.next()


    def finish(self):
        self.f_finish = tk.Frame(self.content, background="white")
        tk.Label(self.f_finish, text="Finish", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)





Installer().mainloop()

