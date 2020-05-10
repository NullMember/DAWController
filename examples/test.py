from DAWController import *
import time

def callback(name, data):
    return

if __name__ == "__main__":
    try:
        c = DAWController()
        c.connect("from", "to")
        c.addCallback(callback)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        print("Exit.")
        c.disconnect()