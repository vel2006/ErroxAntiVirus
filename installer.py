import os

#Used for creating the requierments.txt file and install the needed packages automatically
print("Checking for / Installing packages...")
try:
    with open("requirements.txt", "w") as file:
        file.write("requests==2.32.3\n")
        file.write("psutil==6.0.0\n")
        file.write("pywin32==306\n")
        file.close()
    os.system("python -m pip install -r requirements.txt")
except Exception as error:
    print(f"Error when creating requirements.txt or installing packages: {error}")
    exit()

import requests
#Used to extract the content between two strings
def GetInbetween(textIn, startingPoint, endingPoint):
    startIndex = textIn.find(startingPoint)
    endingIndex = textIn.find(endingPoint, startIndex + len(startingPoint))
    if startIndex != -1 and endingIndex != -1:
        return textIn[startIndex + len(startingPoint):endingIndex]
#Installs the needed directory and files within that directory
def InstallErroxAntivirus():
    print("Creating directory for Errox_Antivirus...")
    targetDirectory = f"C:\\Users\\{os.getlogin()}\\ErroxAntiVirus"
    os.mkdir(targetDirectory)
    print("Creating Antivirus file...")
    with open(f"{targetDirectory}\\ErroxAntivirus.py", "w") as file:
        responseFromMainPage = requests.get("https://vel2006.github.io/ErroxAntiVirus/installMainPageData.html")
        if responseFromMainPage.status_code == 200:
            for line in GetInbetween(responseFromMainPage.text, "<body>", "</body>").splitlines():
                if "<p>" in line:
                    file.write(str(GetInbetween(line, "<p>", "</p>")) + '\n')
        else:
            print("Fatial Error: Install page is down or doesnt exist!")
            exit()
        file.close()
    print("Creating user file...")
    with open(f"{targetDirectory}\\users.txt", "w") as file:
        pass
    print("Creating processes file...")
    with open(f"{targetDirectory}\\processes.txt", "w") as file:
        pass
    print(f"Errox Antivirus has been installed in {targetDirectory}!")

print("Checking for Errox Antivirus...")
if os.path.exists(f"C:\\Users\\{os.getlogin()}\\ErroxAntiVirus"):
    print("Directory of Errox Antivirus exists, checking for file...")
    if os.path.exists(f"C:\\Users\\{os.getlogin()}\\ErroxAntiVirus\\ErroxAntivirus.py"):
        print("Errox Antivirus exists, checking for \"users\", \"log\" and \"processes\" files...")
        if os.path.exists(f"C:\\Users\\{os.getlogin()}\\ErroxAntiVirus\\users.txt"):
            print("Users file exists.")
        else:
            print("Users file doesnt exist, creating...")
            with open(f"C:\\Users\\{os.getlogin()}\\ErroxAntiVirus\\users.txt", "w") as file:
                pass
        if os.path.exists(f"C:\\Users\\{os.getlogin()}\\ErroxAntiVirus\\processes.txt"):
            print("Processes file exists.")
        else:
            print("Processes file doesnt exist, creating...")
            with open(f"C:\\Users\\{os.getlogin()}\\ErroxAntiVirus\\processes.txt", "w") as file:
                pass
        if os.path.exists(f"C:\\Users{os.getlogin()}\\ErroxAntiVirus\\ErroxAutoRunSecurityLog.txt"):
            print("Log file exists.")
        else:
            print("Log file doesnt exist, creating...")
            with open(f"C:\\Users\\{os.getlogin()}\\ErroxAntiVirus\\ErroxAutoRunSecurityLog.txt", "w") as file:
                pass
    else:
        print("Errox Antivirus doesnt exist, creating...")
        InstallErroxAntivirus()
else:
    print("Errox Antivirus directory doesnt exist, creating all files...")
    InstallErroxAntivirus()
