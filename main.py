from login import login
from network import Network
from gamemanager import GameManager
import os
import logging
import time
from getpass import getpass


def setupLogging():
    logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(name)s %(levelname)s %(message)s",
            filename=os.path.join(os.path.dirname(os.path.realpath(__file__)),"farmbot.log"),
            filemode="w"
            )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logging.getLogger().addHandler(console)

def main():
    logger = logging.getLogger("main")
    
    print(
"""
 ______      _____  __  __ ______ _____            __  __          
|  ____/\   |  __ \|  \/  |  ____|  __ \     /\   |  \/  |   /\    
| |__ /  \  | |__) | \  / | |__  | |__) |   /  \  | \  / |  /  \   
|  __/ /\ \ |  _  /| |\/| |  __| |  _  /   / /\ \ | |\/| | / /\ \  
| | / ____ \| | \ \| |  | | |____| | \ \  / ____ \| |  | |/ ____ \ 
|_|/_/    \_\_|  \_\_|  |_|______|_|  \_\/_/    \_\_|  |_/_/    \_\ 
 ____   ____ _______ 
|  _ \ / __ \__   __|
| |_) | |  | | | |   
|  _ <| |  | | | |   
| |_) | |__| | | |   
|____/ \____/  |_|  made by: Hurutparittya
"""
    )
    username = input("username >")
    password = getpass("password >")
    print("\033\143")
    logger.info("launching bot")
    lastError = None
    errorCount = 0
    while True:
        try:
            session = login(username,password)
            network = Network(session)
            gm = GameManager(network)
            while True:
                gm.claimCalendar()
                gm.processFields()
                time.sleep(10)
        except Exception as e:
            logger.exception(str(e),exc_info=True)
            if lastError is not None and time.time() - lastError > 7200:
                errorCount = 0

            lastError = time.time()
            errorCount += 1
            if errorCount == 1:
                time.sleep(120)
            elif errorCount == 2:
                time.sleep(240)
            elif errorCount == 3:
                time.sleep(1800)
            elif errorCount > 3:
                logger.error("terminating loop because error count exceeded 3")
                break
            logger.warning(f"restarting main loop with error count of {errorCount}")

if __name__ == "__main__":
    setupLogging()
    main()
            



