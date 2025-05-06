#!/usr/bin/python3

import time, os, random, logging, signal, sys
from dotenv import dotenv_values

secrets = dotenv_values(".env")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(secrets["LOG_LEVEL"].upper()) # set log level from .env file


stop = False  

sensors0 = secrets['SENSORS0'].split(",") # if sys.argv[1] == "0" else secrets['SENSORS1'].split(",") 
sensors1 = secrets['SENSORS1'].split(",") # if sys.argv[1] == "0" else secrets['SENSORS1'].split(",") 

dt = 10    # time interval between measurement points
points = 10 # smoothing decay time in points

outfile_cage0 = os.path.expanduser("/var/tmp/drivetemp-cage-0.txt")
outfile_cage1 = os.path.expanduser("/var/tmp/drivetemp-cage-1.txt")

if __name__ == "__main__":
    logging.info("Starting...")

    def sighandler(signum, frame):
        global stop
        stop = True
        
    signal.signal(signal.SIGINT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)
    is_posix = os.name == 'posix'
    if is_posix:
        signal.signal(signal.SIGQUIT, sighandler)
 
               
    while not stop:    
        time.sleep(dt)
        
           
        if not os.path.exists(outfile_cage0):
            open(outfile_cage0, "w").close()
        temp = int(open(sensors0[0]).read())
        k = 1. / points
        K = 1 - k
        k = k / len(sensors0)
        t = 0
        for s in sensors0:
            t += int(open(s).read())
        temp = round(temp * K + t * k)
        logging.info("Temperature0: %s", temp)
        myfile = open(outfile_cage0,'r+')
        myfile.seek(0)
        myfile.write(str(int(temp)) + "\n\n")
        myfile.truncate()
            
        if not os.path.exists(outfile_cage1):
            open(outfile_cage1, "w").close()
        temp = int(open(sensors1[0]).read())
        k = 1. / points
        K = 1 - k
        k = k / len(sensors1)
        t = 0
        for s in sensors1:
            t += int(open(s).read())
        temp = round(temp * K + t * k)
        logging.info("Temperature1: %s", temp)
        myfile = open(outfile_cage1,'r+')
        myfile.seek(0)
        myfile.write(str(int(temp)) + "\n\n")
        myfile.truncate()            


    logging.info("Stopping...")
    
    myfile = open(outfile_cage0,'r+')
    myfile.seek(0)
    myfile.write(str(int(99999)) + "\n\n")
    myfile.truncate()  
    
    myfile = open(outfile_cage1,nano'r+')
    myfile.seek(0)
    myfile.write(str(int(99999)) + "\n\n")
    myfile.truncate()  