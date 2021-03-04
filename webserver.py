# Webserver!

from aiohttp import web
import aiohttp_jinja2
import jinja2
from random import randint
import sqlite3

    #    with open("templates/hello_world.html.jinja2", "r") as file:
        #contents = file.read()
    # equivalent:
    #     file = open("hello_world.html.jinja2", "r")
    #     contents = file.read()
    #     file.close()

@aiohttp_jinja2.template('SatreSite1.html.jinja2')
async def maria1(request):
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")  # DESC or ASC
    results = cursor.fetchall()
    conn.close()
    return { "tweets": results,
        "hobbies": ["Reading", "Swimming and Running", "Drawing", "Watching Tv (although less so since covid)", "Spending time with my friends"]
    }

@aiohttp_jinja2.template('SatreSite2.html.jinja2')
async def maria2(request):
    return {
        "titles": ["Maria's TV shows!","My favorite shows on Netflix:"]
    }

@aiohttp_jinja2.template('SatreSite3.html.jinja2')
async def maria3(request):
    return {"favBook": randint(0,2)}

@aiohttp_jinja2.template('SatreSite4.html.jinja2')
async def maria4(request):
    return {
        "cars": ["Honda CRV","Porsche 911","Mazda Miata"]
            }

def main():


    app = web.Application()
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates'))
    app.add_routes([web.get('/',maria1),
                    web.get('/1.html', maria1),
                    web.get('/2.html', maria2),
                    web.get('/3.html', maria3),
                    web.get('/4.html', maria4),
                    web.static('/static','static')])
    print("Webserver 1.0")
    web.run_app(app, host="127.0.0.1", port=3000)

if __name__=="__main__":
    main()