# Webserver!

from aiohttp import web
import aiohttp_jinja2
import jinja2
from random import randint
import sqlite3
import requests

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

def get_location(ip_address):
    api_key = "fd0329babd7f4167ca8ff84646e1bfc2"
    result = requests.get("http://api.ipstack.com/%s?access_key=%s" % (ip_address, api_key))
    ip_address_info = result.json()
    #flag = ip_address_info['country_flag_emoji_unicode']
    city = ip_address_info["city"]
    region_code = ip_address_info["region_code"]
    country_name = ip_address_info["country_name"]
    return "%s, %s, %s" % (city, region_code, country_name)

async def add_tweet(request):
    data = await request.post()
    user_ip = request.remote
    #user_ip = "8.8.8.8"
    print("User is coming from %s" % user_ip)
    user_location = get_location(user_ip)
    print("You are at: %s" % user_location)
    content = data['content']
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tweets (content, likes, location) VALUES (?,0,?)", (content,user_location))
    #cursor.execute("UPDATE tweets SET location=?", (user_location,))
    conn.commit()
    print("The user tweeted %s" % data['content'])
    raise web.HTTPFound('/')

def like(request):
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()
    tweet_id = request.query['id']
    cursor.execute("SELECT likes FROM tweets WHERE id=?", (tweet_id,))
    like_count = cursor.fetchone()[0]
    cursor.execute("UPDATE tweets SET likes=? WHERE id=?", (like_count + 1, tweet_id))
    conn.commit()
    conn.close()
    raise web.HTTPFound('/')

async def like_json(request):
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()
    tweet_id = request.query['id']
    cursor.execute("SELECT likes FROM tweets WHERE id=?", (tweet_id,))
    like_count = cursor.fetchone()[0]
    cursor.execute("UPDATE tweets SET likes=? WHERE id=?", (like_count + 1, tweet_id))
    conn.commit()
    conn.close()
    return web.json_response(data={"like_count": like_count+1})

def main():


    app = web.Application()
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates'))
    app.add_routes([web.get('/',maria1),
                    web.get('/1.html', maria1),
                    web.get('/2.html', maria2),
                    web.get('/3.html', maria3),
                    web.get('/4.html', maria4),
                    web.post('/tweet',add_tweet),
                    web.get('/like', like),
                    web.get('/like.json',like_json),
                    web.static('/static','static')])
    print("Webserver 1.0")
    web.run_app(app, host="0.0.0.0", port=80)

if __name__=="__main__":
    main()