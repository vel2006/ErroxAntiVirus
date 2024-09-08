# ErroxAntiVirus

## Basic Description:

Errox Antivirus is a proof of consept AntiVirus that works differently than other options on the market.

## Features:

* Windows compatable

* Open Source

* Free

* Allows only listed processes to run

* Allows only listed users to exist

* Support for (at least) one month

* Planned updates

## Creator:

That1EthicalHacker

## How it works:

As stated above, this solution is different than other commercial options. As other AntiViruses and EDR products is that they will allow any script / file to run, even if it has a known exploit or is well known malware. A good example of this to display how they work against unknown ransomware is a video by "The PC Security Channel" on Youtube, which can be found here: "https://youtu.be/2R033fex8D8?si=gfF9w1KXzCb4ScUQ". To combat this, Errox AntiVirus takes a different approach to defending a computer / device against threats. While it isnt the most secure or useable for every day usage, it is one of the best solutions I have found for protecting against file ceration, encryption, reading, and more for servers. As a testament of this I have been using it on my own home servers for roughly a week without any problems! The way it is able to check for any kind of new process or user is using python packages for windows and simply end / remove any unknown or allowed processes and users.

## How to use Errox AntiVirus:

Before you can use Errox AntiVirus you have to run the installer.py file with admin access, it will automatically install or update any needed packages along will pulling the code for the AntiVirus from the page "https://vel2006.github.io/ErroxAntiVirus/installMainPageData.html", that page can be found under the site branch. Once the install it done, it will add a folder to your base user directory which can be found at "C:\Users\<your username>\ErroxAntiVirus". It will create the antivirus file (ErroxAntivirus.py), the users file (users.txt), processes file (processes.txt) and log file (ErroxAutoRunSecurityLog.txt). To use the AntiVirus, simply run "ErroxAntivirus.py" as an administrator.

### Commands in AntiVirus:

* help    | displays help page

* AddU    | adds current users to users.txt file

* AddP    | adds currently running processes to processes.txt file

* Purge   | kills any process not in the processes.txt file

* Kill    | removes passed user

* KILL    | removes all users not in users.txt file

* Scan    | scans for all running processes

* Start   | scans for all startup processes (removal added in next update)

* User    | scans for all unknown users

* Auto    | runs "Purge" and "KILL" in a forever loop that will either prompt the user before acting based on run type
