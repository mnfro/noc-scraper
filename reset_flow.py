import json
import time

def main():
   start_time = time.time()
   with open('./ignore_id.txt', 'w') as f:
    f.write(json.dumps([]))
   time_diff = time.time() - start_time
   print(f'Reset time: %.5f seconds.' % time_diff)

main()
