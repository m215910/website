# Webserver!

from aiohttp import web
import aiohttp_jinja2
import jinja2
from random import randint
import sqlite3
import requests
import secrets
import hashlib

    #    with open("templates/hello_world.html.jinja2", "r") as file:
        #contents = file.read()
    # equivalent:
    #     file = open("hello_world.html.jinja2", "r")
    #     contents = file.read()
    #     file.close()

#@aiohttp_jinja2.template('SatreSite1.html.jinja2')
async def maria1(request):

    #is the user logged in?
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()
    user_loggedin=0
    if "logged_in" in request.cookies:
        cursor.execute("SELECT COUNT(*) FROM users WHERE cookie=?", (request.cookies['logged_in'],))

        result = cursor.fetchone()
        if result[0] == 1:
            user_loggedin = 1

    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")  # DESC or ASC
    results = cursor.fetchall()
    #conn.close()
    context = {"user_loggedin": user_loggedin, "tweets": results, "hobbies": ["Reading", "Swimming and Running", "Drawing",
                                               "Watching Tv (although less so since covid)",
                                               "Spending time with my friends"]}
    response = aiohttp_jinja2.render_template('SatreSite1.html.jinja2', request, context)
    #response.set_cookie('logged_in','yes')
    return response

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

@aiohttp_jinja2.template('login_page.html.jinja2')
async def show_login(request):
    return {}

async def logout(request):
    response = aiohttp_jinja2.render_template('login_page.html.jinja2', request, {})
    response.cookies['logged_in'] = ''
    return response

async def login(request):
    data = await request.post()
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()

    cursor.execute("SELECT salt FROM users WHERE username=?", (data['username'],))
    result = cursor.fetchone()
    if result is None:
        raise web.HTTPFound('/login.html')

    salt = result[0]
    salted_password = data['password'] + salt
    hashed_password = hashlib.md5(salted_password.encode('ascii')).hexdigest()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username=? AND password=?",
                   (data['username'], hashed_password))
    query_result = cursor.fetchone()

    user_exists = query_result[0]
    if user_exists == 0:
        user_loggedin = 0
        raise web.HTTPFound('/login.html')
    else:
        response = web.Response(text="congrats!", status=302, headers={'Location': '/1.html'})
        # generate a random cookie
        user_loggedin = 1
        logged_in_secret = secrets.token_hex(8)
        response.cookies['logged_in'] = logged_in_secret
        #store cookie
        cursor.execute("UPDATE users SET cookie=? WHERE username=?", (logged_in_secret, data['username']))
        conn.commit()

        conn.close()
        #context = { "user_loggedin": user_loggedin}
        return response

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

async def delete(request):
    if 'logged_in' not in request.cookies:
        raise web.HTTPForbidden()

    cookie = request.cookies['logged_in']
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()
    tweet_id = request.query['id']

    #data = cursor.execute("SELECT * FROM users")
    cursor.execute("SELECT COUNT(*) FROM users WHERE cookie=?",
                   (cookie,))
    query_result = cursor.fetchone()

    user_loggedin = query_result[0]
    if user_loggedin == 0:
        raise web.HTTPFound('/login.html')

    #response = web.Response(text="congrats!", status=302, headers={'Location': '/1.html'})
    cursor.execute("DELETE FROM tweets WHERE id=?", (tweet_id,))
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
                    web.get('/login.html', show_login),
                    web.post('/login', login),
                    web.get('/logout', logout),
                    web.post('/tweet',add_tweet),
                    web.get('/like', like),
                    web.get('/delete', delete),
                    web.get('/like.json',like_json),
                    web.static('/static','static')])
    print("Webserver 1.0")
    web.run_app(app, host="0.0.0.0", port=80)

if __name__=="__main__":
    main()