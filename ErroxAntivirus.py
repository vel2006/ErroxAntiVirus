ERROXVERSION = 1.2

import os
import winreg
import win32net
from datetime import datetime
import subprocess
import ast
import psutil
import time

#Getting the users inside of the C:\Users folder
def GetUsers(GetType):
    users = []
    match GetType:
        case "dir":
            startPath = os.getcwd()
            os.chdir("C:\\Users")
            for user in os.listdir():
                users.append(user)
            os.chdir(startPath)
        case "user":
            try:
                usersToFilter = win32net.NetUserEnum(None, 0)
                for user in usersToFilter[0]:
                    users.append(user['name'])
            except Exception as error:
                print(error)
        case "all":
            usersToAdd = win32net.NetUserEnum(None, 0)
            for user in usersToAdd[0]:
                users.append(user['name'])
            startPath = os.getcwd()
            os.chdir("C:\\Users")
            for user in os.listdir():
                if user not in users:
                    users.append(user)
                else:
                    pass
    return users

#Comparing the current user list inside of the C:\Users folder to the saved list
def GetNewUsers(userFileList):
    knownUsers = []
    newUsers = []
    #Getting known users
    with open(userFileList, "r") as file:
        for line in file:
            knownUsers.append(line.strip())
        file.close()
    #Getting the current users and comparing it to the past ones
    currentUsers = GetUsers("all")
    for user in currentUsers:
        if user in knownUsers:
            pass
        else:
            newUsers.append(user)
    if len(newUsers) == 0:
        return None
    else:
        return newUsers

#Getting the creation of a file and other data
def GetFileCreation(filePath):
    #Getting generic file data
    fileStats = os.stat(filePath)
    #Getting the spesific file data
    fileCreationTime = datetime.datetime.fromtimestamp(fileStats.st_ctime)
    fileAccessTime = datetime.datetime.fromtimestamp(fileStats.st_atime)
    fileModificationTime = datetime.datetime.fromtimestamp(fileStats.st_mtime)
    #Saving and returning the values as a tuple, its faster than an array
    returnValues = (fileCreationTime, fileAccessTime, fileModificationTime)
    return returnValues

#Getting all the contents of a directory
def AllInDirecory(targetDirectory):
    startingDirectory = os.getcwd()
    os.chdir(targetDirectory)
    allFilesInTarget = os.listdir()
    directorysInTarget = []
    filesInTarget = []
    for item in allFilesInTarget:
        if os.path.isfile(item):
            filesInTarget.append(item)
        else:
            directorysInTarget.append(item)
    os.chdir(startingDirectory)
    if len(filesInTarget) > 0:
        if len(directorysInTarget) > 0:
            return filesInTarget, directorysInTarget
        else:
            return filesInTarget, None
    else:
        if len(directorysInTarget) > 0:
            return None, directorysInTarget
        else:
            return None, None

#Deleting a directory and its sub files / direcories
def DeleteDirectory(targetDirectory):
    if os.path.exists(targetDirectory):
        files, directorys = AllInDirecory(targetDirectory)
        if len(files) != 0:
            for file in files:
                try:
                    os.remove(file)
                except Exception:
                    return f"Could not delete file {file}"
        if len(directorys) != 0:
            for directory in directorys:
                DeleteDirectory(directory)
                try:
                    os.removedirs(directory)
                except Exception:
                    return f"Could not delete directory {directory}"
        return "Removed target directory and its underlings"
    else:
        return "Passed directory does not exist"

#Getting startup processes
def GetStartupProcesses(returnType):
    startupPrograms = []
    #Checking directories using keys
    keyPaths = ["SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run",
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce", "SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\runOnce"]
    for currentKeyPath in keyPaths:
        try:
            registerKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, currentKeyPath, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, value, _, = winreg.EnumValue(registerKey, i)
                    match returnType:
                        case "full":
                            startupPrograms.append((name, value))
                        case "name":
                            startupPrograms.append(name)
                        case "info":
                            startupPrograms.append(value)
                    i += 1
                except OSError as error:
                    break
            winreg.CloseKey(registerKey)
        except Exception as error:
            print(f"Failed to read registery: {error}")
    #Checking task scheduler
    try:
        resultOfSearch = subprocess.run(["schtasks", "/Query", "/FO", "LIST", "/V"], capture_output=True, text=True)
        if resultOfSearch.returncode != 0:
            print("Query of tasks returned with an error.")
            pass
        else:
            tasks = resultOfSearch.stdout.splitlines()
            lineData = []
            for line in tasks:
                match returnType:
                    case "full":
                        if line.startswith("TaskName:"):
                            lineData.append(line.split(':', 1)[1].strip())
                        if line.startswith("Task To Run:"):
                            lineData.append(line.split(':', 1)[1].strip())
                            startupPrograms.append(tuple(lineData))
                            lineData = []
                    case "name":
                        if line.startswith("TaskName:"):
                            startupPrograms.append(line.split(':', 1)[1].strip())
                    case "info":
                        if line.startswith("Task To Run:"):
                            startupPrograms.append(line.split(':', 1)[1].strip())
    except Exception as error:
        print(f"An error occured: {error}")
        pass
    #Checking direcories
    directoriesToScan = ("C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup", "C:\\Users\\<user>\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    usersToScan = GetUsers("dir")
    try:
        usersToScan.remove("Public")
        usersToScan.remove("Default User")
        usersToScan.remove("All Users")
        usersToScan.remove("desktop.ini")
    except Exception as error:
        print(f"Error: {error}")
    for directory in directoriesToScan:
        if directory == directoriesToScan[1]:
            for user in usersToScan:
                if user != "Default":
                    targetDirectory = directory.replace("<user>", user)
                    files, directorys = AllInDirecory(targetDirectory)
                    try:
                        files.remove("desktop.ini")
                    except Exception as error:
                        print(f"Error: {error}")
                    for file in files:
                        startupPrograms.append(directory + file)
                else:
                    defaultDirectories = ("C:\\Users\\Default\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs",
                                          "C:\\Users\\Default\\AppData\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Accessibility",
                                          "C:\\Users\\Default\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Accessories",
                                          "C:\\Users\\Default\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Maintenance",
                                          "C:\\Users\\Default\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Windows PowerShell",
                                          "C:\\Users\\Default\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\System Tools")
                    for dir in defaultDirectories:
                        files, directorys = AllInDirecory(dir)
                        if files is not None:
                            for file in files:
                                startupPrograms.append(dir + file)
        else:
            files, directorys = AllInDirecory(directory)
            try:
                files.remove("desktop.ini")
            except Exception as error:
                print(f"Error: {error}")
            for file in files:
                startupPrograms.append(directory + file)
    return tuple(startupPrograms)

#Comparing the current startup tasks to the saved ones inside of the tasks file
def GetNewStartupProcesses(startupProcessesFile):
    knownProcesses = []
    newProcesses = []
    #Getting known processes
    with open(startupProcessesFile, "r") as file:
        for line in file:
            content = ast.literal_eval(line)
            knownProcesses.append(content[0])
    #Getting new processes and comparing it to the known ones
    processesNames = GetStartupProcesses("names")
    for process in processesNames:
        if process in knownProcesses:
            pass
        else:
            newProcesses.append(process)
    if len(newProcesses) == 0:
        return None
    else:
        return newProcesses

#Well, getting the currently running processes...Its in the name...
def GetRunningProcesses(returnType):
    processes = []
    match returnType:
        case 0:
            for process in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
                try:
                    if process.info['name'] in processes or process.info['pid'] in processes:
                        pass
                    else:
                        processes.append(tuple(process.info))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as error:
                    print(f"Error: {error}")
            return processes
        case 1:
            for process in psutil.process_iter(['name']):
                try:
                    if process.info['name'] in processes:
                        print("Not adding:{process}")
                    else:
                        processes.append(process.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as error:
                    print(f"Error: {error}")
            return processes
        case 2:
            for process in psutil.process_iter(['username', 'pid']):
                try:
                    if process.info['pid'] in processes:
                        pass
                    else:
                        processes.append(process.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as error:
                    print(f"Error: {error}")
            return processes
        case 3:
            for process in psutil.process_iter(['username', 'name', 'pid']):
                try:
                    if process.info['name'] in processes or process.info['pid'] in processes:
                        pass
                    else:
                        processes.append(process.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as error:
                    print(f"Error: {error}")
            return processes
        case 4:
            for process in psutil.process_iter(['name', 'pid']):
                try:
                    if process.info['name'] in processes or process.info['pid'] in processes:
                        pass
                    else:
                        processes.append(process.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as error:
                    print(f"Error: {error}")
            return processes
        case 5:
            for process in psutil.process_iter(['pid']):
                try:
                    if process.info['pid'] in processes:
                        pass
                    else:
                        processes.append(process.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as error:
                    print(f"Error: {error}")
            return processes

#Kills a process
def KillProcess(targetProcessPid):
    try:
        os.system(f"taskkill /F /PID {targetProcessPid} > NUL 2>&1")
        return f"Proccess PID: {targetProcessPid} killed."
    except Exception as error:
        return f"Error: {error}"

#Checking to see if the current running processes are allowed.
def GetNewRunningProcesses(allowedProcessesFile, threatMode):
    knownProcesses = []
    unknownProcess = []
    with open(allowedProcessesFile, "r") as file:
        for line in file:
            knownProcesses.append(line.strip())
        file.close()
    runningProcesses = GetRunningProcesses(4)
    for process in runningProcesses:
        if process['name'] not in knownProcesses and process != '':
            unknownProcess.append(process)
        else:
            pass
    if threatMode == 1:
        for process in unknownProcess:
            print(f"Name: {process['name']}, PID: {process['pid']}")
            KillProcess(process['pid'])
    else:
        return unknownProcess

#Kills a user account
def KillUser(username):
    print("Work in progress")
    if username in GetUsers("dir"):
        result = DeleteDirectory(f"C:\\Users\\{username}")
        match result:
            case "Removed target directory and its underlings":
                pass
            case "Passed directory does not exist":
                return "Passed directory does not exist"
            case _ if "Could not delete file" in result:
                return result
            case _ if "Could not delete directory" in result:
                return result
    else:
        print("User directory doesnt exist, continuing with killing user.")
    if username in GetUsers("user"):
        try:
            win32net.NetUserDel(None, username) 
            return f"Killed User: {username}"
        except Exception as error:
            return f"Error: {error}"
    else:
        print("Username does not exist")

#Will handle all of the logic of the script, will run everything but adding users / processes
def AutomatedRun(allowedProcessesFile, allowedUsersFile, threatMode):
    print("Work in progress")
    users = []
    processes = []
    with open(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\ErroxAutoRunSecurityLog.txt", "w") as logFile:
        #Get users
        with open(allowedUsersFile, "r") as file:
            for line in file:
                users.append(line.split())
        #Get processes
        with open(allowedProcessesFile, "r") as file:
            for line in file:
                processes.append(line)
        #If in danger mode
        if threatMode == 1:
            logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Attempting to start automated run with threat mode enabled.")
            try:
                while True:
                    #Kill new users with no prompt
                    collectedUsers = GetUsers("all")
                    for user in collectedUsers:
                        if user not in users:
                            if "Killed User:" in KillUser(user):
                                logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Removed user: {user} with no prompt")
                            else:
                                logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Failed to removed user: {user} with no prompt, inspect by hand")
                    #Kill new processes with no prompt
                    collectedProcesses = GetNewRunningProcesses(allowedProcessesFile, 0)
                    for process in collectedProcesses:
                        if process not in processes:
                            response = KillProcess(process['pid'])
                            if "Error:" not in response:
                                logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Killed process: {process} with no prompt")
                            else:
                                logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Failed to kill process: {process} with no prompt, inspect by hand")
                    #Remove unknown startup proccesses
                    #Work in progress...
            except Exception as error:
                logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Encountered error with fully automated run: {error}")
        else:
            logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Attempting to start automated run with threat mode disabled.")
            try:
                while True:
                    #Kill new users with no prompt
                    collectedUsers = GetUsers("all")
                    for user in collectedUsers:
                        if user not in users:
                            killUser = input(f"Do you wish to kill user: {user} (1/0)\n>")
                            if killUser == 1:
                                if "Killed User:" in KillUser(user):
                                    logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Removed user: {user} with prompt")
                                else:
                                    logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Failed to removed user: {user} with prompt, inspect by hand")
                            else:
                                logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Remove user: {user} denied by user")
                    #Kill new processes with no prompt
                    collectedProcesses = GetNewRunningProcesses(allowedProcessesFile, 0)
                    for process in collectedProcesses:
                        if process not in processes:
                            killProcess = input(f"Do you wish to kill process: {process} (1/0)\n>")
                            if killProcess == 1:
                                response = KillProcess(process['pid'])
                                if "Error:" not in response:
                                    logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Killed process: {process} with prompt")
                                else:
                                    logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Failed to kill process: {process} with prompt, inspect by hand")
                            else:
                                logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Kill process: {process} denied by user")
                    #Remove unknown startup proccesses
                    #Work in progress...
            except Exception as error:
                logFile.write(f"{datetime.now().date()}/{datetime.now().time()} | Encountered error with fully automated run: {error}")
            logFile.close()

#Script's user end logic
def MainRun():
    while True:
        print("Input your command choice:")
        choice = input(">")
        match choice:
            case "Help":
                print("Help page:\nCommand  | What it does / Output")
                print("Scan     | Scans for all running processes and prints the ones that are running\nStart    | Scans for all processes that run on startup")
                print("Purge    | Kills ANY process not in the process white list (only use if you know what your doing)\nHelp     | How would you not know what this does?")
                print("User     | Looks for any new users outside of whitelist\nAddP     | Adds all running processes to whitelist\nAddU     | Adds all user\'s to whitelist")
                print("Kill     | Removes user's directory and account from system\nKILL     | Removes ANY UNKNOWN USER's directory and account from system (ONLY USE IF YOU KNOW WHAT YOUR DOING)")
                print("Auto     | Automates all commands. Will purge unknown processes, scan for new users and kill new users (only for setup and leave devices)")
                print("End      | Stops this script.")
            case "Scan":
                print("Starting process scan...")
                time.sleep(0.5)
                processes = GetRunningProcesses(4)
                print("Scan complete!")
                for process in processes:
                    print(f"Process name: {process['name']}, Process PID: {process['pid']}")
            case "Start":
                print("Starting startup process scan...")
                time.sleep(0.5)
                processes = GetStartupProcesses("name")
                print("Scan complete!")
                for process in processes:
                    print(f"Process name: {process}")
            case "Purge":
                print("Starting process purge...")
                time.sleep(0.5)
                while True:
                    print("Do you wish to have the script keep puring until it\'s closed? (1/0)")
                    foreverRun = input(">")
                    if foreverRun == "1" or foreverRun == "0":
                        break
                if foreverRun == 1:
                    print ("Starting forever loop of purge.")
                    while True:
                        processes = GetNewRunningProcesses(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\processes.txt", 1)
                else:
                    processes = GetNewRunningProcesses(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\processes.txt", 1)
                    print("Purge complete!")
            case "User":
                print("Starting user scan...")
                time.sleep(0.5)
                users = GetNewUsers(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\users.txt")
                print("User scan complete!")
                for user in users:
                    print(f"User: {user}")
            case "Kill":
                print("Starting killing of user...")
                time.sleep(0.5)
                choices = GetUsers("all")
                while True:
                    print(f"Which user do you wish to kill:\n{choices}")
                    userToKill = input(">")
                    if userToKill in choices:
                        KillUser(userToKill)
                        print(f"Killing of user: {userToKill} done!")
                        break
                    else:
                        print("Error: unknown user.")
            case "KILL":
                print("Starting KILLING of all unknown users...")
                time.sleep(0.5)
                unknownUsers = GetNewUsers(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\users.txt")
                for user in unknownUsers:
                    print(f"Killing user: {user}")
                    KillUser(user)
                print(f"KILLing of users: {unknownUsers} done!")
            case "Auto":
                while True:
                    print("Do you want a prompt during auto run? (Yes / No)")
                    runType = input(">")
                    if runType != "Yes" and runType != "No":
                        print("Error: unknown input run type. Options are \"Yes\" and \"No\"")
                    else:
                        if runType == "No":
                            AutomatedRun(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\processes.txt", f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\users.txt", 1)
                        else:
                            AutomatedRun(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\processes.txt", f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\users.txt", 0)
            case "AddP":
                print("Collecting running processes...")
                time.sleep(0.5)
                processes = GetRunningProcesses(1)
                print("Collection complete!")
                time.sleep(0.5)
                print("Adding processes to whitelist...")
                time.sleep(0.5)
                with open(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\processes.txt", "r+") as file:
                    file.truncate(0)
                with open(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\processes.txt", "w") as file:
                    for process in processes:
                        file.write(f"{process['name']}\n")
                    file.close()
                print("Adding processes to whitelist complete!")
            case "AddU":
                print("Collecting users...")
                time.sleep(0.5)
                users = GetUsers("all")
                print("Collection complete!")
                time.sleep(0.5)
                print("Adding users to whitelist...")
                time.sleep(0.5)
                with open(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\users.txt", "r+") as file:
                    file.truncate(0)
                with open(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\users.txt", "w") as file:
                    for user in users:
                        file.write(f"{user}\n")
                    file.close()
                print("Adding users to whitelist complete!")
            case "End":
                print("Ending script...")
                time.sleep(0.5)
                break
            case _:
                print("Error: Invalid selection, input \"Help\" for allowed inputs.")

print("ERROX ANTIVIRUS\nVersion: 1.0\nProgramed by: That1EthicalHacker")
print("Hello user, this is Errox Antivirus! The worst (and best) proof of concept antivirus you will never use!")
print("This is not ment to be use in a real enviorment and only should be used for studdying")
print("For the help page type \"Help\"")
print(f"Thanks for using Errox Antivirus Version {ERROXVERSION}!")
MainRun()
