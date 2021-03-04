import sqlite3

def main():
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC") #DESC or ASC
    results = cursor.fetchall()
    #print(results)
    #for x in results:
        #print(x[0])
    for x in results:
        print('TWEET: %s LIKES: %d' % (x[0], x[2]))


main()