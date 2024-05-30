import time
import random
epoch = time.time()
while True:
    ct = time.time() - epoch
    # print(f"ct: {ct}")
    # print(f"test: {str(int(ct*1000)%1000).zfill(3)}")
    print(f"[{str(int(ct/60)).zfill(3)}:{str(int(ct%60)).zfill(2)}.{str(int(ct*1000)%1000).zfill(3)}]: Hello, World!")
    time.sleep((random.random() * 400 + 800)/1000)