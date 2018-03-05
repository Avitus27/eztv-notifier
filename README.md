# eztv-notifier
A Python based email notifier for eztv
## Parameters
You can use parameters to override the .env file or for verbose output. Detailed description of all parameters in the `--help` output
## Set-Up
``` $ date +%s > last_torrent $ cp .env.example .env $ vim .env $ chmod +x Main.py $ ./Main.py ``` The program will email you a list of any torrents found since the last time it was run
## Contributions
I try to keep the master branch as stable and don't tend to allow direct commits. Just create a new branch and pull request and I'll manually review. All I ask is you run the following command first: 
`autopep8 -p 5 -a -i Main.py`
