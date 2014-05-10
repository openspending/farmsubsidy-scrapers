import sys
from transparenzdatenbank import Listing

year=sys.argv[1]
filename=sys.argv[2]

l=Listing(year=year)
l.save_csv(filename)
