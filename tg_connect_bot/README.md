### Installation 
pip install -r requirements.txt
fill .env_clear and rename it to .env
### Usage 
###### Debian/Ubuntu
- add code below to ~/.bashrc
```bash
alias killautoresp='pkill -f -9 autoresp.py'
alias killbot='pkill -f -9 bot.py'
alias rnautoresp='killautoresp;sleep 5; python -u /home/user/tg_connect_bot/autoresp.py >> /home/user/tg_connect_bot/logs/autoresp.log 2>&1 &'
alias rnbot='killbot;sleep 5; python -u /home/user/tg_connect_bot/bot.py >> /home/user/tg_connect_bot/logs/bot.log 2>&1 &'
```
- perform in terminal
```bash
source ~/.bashrc
rnbot
rnautoresp
``` 
