import leveldb
import random 

''' Populates the LevelDB in ./db with URLs and random frequencies for testing.
'''


db = leveldb.LevelDB("./db")

urls = ["example.com", "test.com/example", "dsg.cs.tcd.ie", "scss.tcd.ie", "tcd.ie"]

for url in urls:
    db.Put(url, str(random.randint(0, 32)))
