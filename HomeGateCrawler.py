"""Main module - used for starting the scraper"""

from hgc_modules.HGCtraverse import *
import sys

sys.setrecursionlimit(10000)
driver.get(main_page)


print("\nIf starting the scraper for the first time, please choose \'1.Check for new ads\' option\n")


try:
    while True:
        site_traversing()

except Exception as e:
    print(e)

except signal.signal(signal.SIGINT, Handler):
    pass

finally:
    time.sleep(1)
    sys.exit(0)







