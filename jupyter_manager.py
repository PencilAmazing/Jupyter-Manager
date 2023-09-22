#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk
import subprocess, pathlib

# from jupyter_server.serverapp import JupyterServerListApp
import jupyter_server.serverapp
from time import sleep
from enum import Enum
import webbrowser


def make_control_panel():
    assert False, "YOU LAZY BASTARD GET TO WORK"


cached_servers = []

root = Tk()
root.title("Jupyter Notebook manager")

notebooks_found = StringVar(value=["pid 1", "pid 2"])
processList = Listbox(root, listvariable=notebooks_found)
processList.grid(row=0, columnspan=3)

statusframe = ttk.Frame(root)
statusframe.grid(row=4, sticky="ew", columnspan=3)
statusframe["relief"] = "sunken"
statusframe["borderwidth"] = 2
statuslabel = ttk.Label(statusframe, text="Idle.")
statuslabel.grid()  # Label disappears without this. huh


# These dont work because single threaded lmao
# maybe do root.after(5, func)
class Status:
    IDLE = "Idle."
    SEARCH = "Searching..."
    KILL = "Killing... This will take a while."
    LAUNCH = "Launching new instance..."


def set_status_text(status):
    global statuslabel
    statuslabel["text"] = status


def find_active_notebooks():
    global cached_servers
    set_status_text(Status.SEARCH)
    cached_servers = list(jupyter_server.serverapp.list_running_servers())
    processList.delete(0, END)
    for server in cached_servers:
        pid = server["pid"]
        port = server["port"]
        print("Found server with pid", pid, "and port", port)
        processList.insert(END, str(pid) + "@" + str(port))
    set_status_text(Status.IDLE)


def kill_process(server_index):
    global cached_servers
    try:
        jupyter_server.serverapp.shutdown_server(cached_servers[server_index])
    except ConnectionRefusedError:
        print("Connection to server refused. Failed to shutdown server.")
        print("Perhaps outdated info? Try manual refresh again")


def shutdown_all_notebooks():
    for idx in range(len(cached_servers)):
        print(f"Killing server {idx}/{len(cached_servers)}")
        kill_process(idx)
    find_active_notebooks()


def shutdown_selected_notebook():
    set_status_text(Status.KILL)
    indices = processList.curselection()
    for idx in indices:
        print("Killing server index", str(idx), "/", len(cached_servers))
        kill_process(idx)
    find_active_notebooks()  # Refresh cache
    set_status_text(Status.IDLE)


def start_notebook():
    set_status_text(Status.LAUNCH)
    print("Attempt to start notebook")
    # This is to run in background
    subprocess.Popen(["jupyter", "lab"], cwd=pathlib.Path.home())
    # subprocess.run(["jupyter", "lab"])
    sleep(2)  # 2 seconds?
    find_active_notebooks()
    set_status_text(Status.IDLE)


def open_selected():
    for idx in processList.curselection():
        server = cached_servers[idx]
        url = "{}:{}".format(server["hostname"], server["port"])
        print("Opening notebook at url", url)
        webbrowser.open(url, new=0, autoraise=True)


root.option_add("*tearOff", FALSE)
# win = Toplevel(root)
menubar = Menu(root)
root["menu"] = menubar
menu_file = Menu(menubar)
menubar.add_cascade(menu=menu_file, label="File")
menu_file.add_command(label="Open selected...", command=open_selected)
menu_file.add_separator()
menu_file.add_command(label="Kill all notebooks...", command=shutdown_all_notebooks)
menu_file.add_command(label="Quit", command=root.destroy)

ttk.Button(root, text="Find Servers", command=find_active_notebooks).grid(
    row=1, column=1
)
ttk.Button(root, text="Start Server", command=start_notebook).grid(row=2, column=1)
ttk.Button(root, text="Kill Server", command=shutdown_selected_notebook).grid(
    row=3, column=1
)

find_active_notebooks()
root.mainloop()
