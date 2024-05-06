# Author: Alex Marquardt
# Desc: Update, print, edit, and remove from machines.json
# Date: 3/7/2024

import json

helpList = """
_help -> List of commands
_quit -> exit program
_show -> print all machines and their addresses
_add -> add a machine
_del -> remove a machine
_edit -> edit a machine
"""

selected = ""

def __add():#add a machine
    ans = input("machine or command? (m/c) - ")
    if(ans == "m"):
        new_name = input("Name: ")
        new_address = input("Ip: ")
        new_machine = {
            'name': new_name,
            'ip': new_address
        }
        write_dict["machines"].append(new_machine)

        return
    elif(ans == "c"):
        command = input("New command: ")
        write_dict["commands"].append(command)
        return
    else:
        print("ERR: INVALID CHOICE")
        __add()

def __del():#remove a machine
    ans = input("machine or command? (m/c) - ")
    if(ans == "m"):
        machine_name = input("Machine Name: ")
        new_dict = {
            'machines': []
        }
        for machine in write_dict["machines"]:
            if(machine['name'] != machine_name):
                new_dict["machines"].append(machine)
        write_dict["machines"] = new_dict["machines"]
        return
    elif(ans == "c"):
        del_command = input("Command to remove: ")
        new_command_list = []
        for command in write_dict["commands"]:
            if(command != del_command):
                new_command_list.append(command)
        return
    else:
        print("ERR: INVALID CHOICE")
        __del()

def __show():#print all machines
    print("""
    ********************
    *     Machines     *
    ********************
          """)
    for machine in write_dict['machines']:
        print(machine['name'], "-", machine['ip'])
    print("""
    ********************
    *     Commands     *
    ********************
          """)
    for command in write_dict["commands"]:
        print(command)
    return

def __edit():#edit a machine
    machine_name = input("Machine name: ")
    for machine in write_dict['machines']:
        if(machine['name'] == machine_name):
            machine['name'] = input("New machine name: ")
            machine['ip'] = input("New machine ip: ")

    return

def __runCom(command):#check what command we are running
    global selected

    if(command == "_help"):
        print(helpList)
    elif(command == "_add"):
        __add()
    elif(command == "_del"):
        __del()
    elif(command == "_show"):
        __show()
    elif(command=="_edit"):
        __edit()
    else:
        print("ERR: INVALID COMMAND")

if __name__ == "__main__":
    json_fp = open("../machines.json")
    json_file = json.load(json_fp)
    write_dict = {
        'machines': [],
        'commands': []
    }
    write_dict["machines"] = json_file['machines']
    write_dict["commands"] = json_file['commands']

    print("Welcome! Use _help for a list of commands!")
    __answer = input(">>> ")
    while(__answer != "_quit"):
        __runCom(__answer)
        __answer = input(">>> ")

    out_file = open("../machines.json", "w")  
    json.dump(write_dict, out_file, indent = 4)  
    out_file.close()
    json_fp.close()