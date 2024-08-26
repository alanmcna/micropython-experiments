from microdot import Microdot, send_file, redirect

app = Microdot()

def fahrenheit_to_celcius(fahrenheit):
    celcius = (fahrenheit - 32) * 5 / 9
    return round(celcius,3)

@app.route('/sleep')
async def sleep(request):
    machine.sleep(10000)
    log('Going to sleep for 10s...')
    return redirect('/')

@app.route('/log')
async def showlog(request):
    global save_path, log_file
    return send_file("{}/{}".format(save_path, log_file), max_age=0, content_type='text/plain')

@app.route('/remount')
async def remount(request):
    global save_path
    mount_sd_card()
    return redirect('/')

@app.route('/reconnect')
async def reconnect(request):
    connect_to_wifi()
    return redirect('/')

@app.route('/resetlog')
async def resetlog(request):
    global save_path, log_file
    f = open("{}/{}".format(save_path, log_file), "w")
    f.write("")
    f.close()
    return redirect('/')

@app.route('/image')
async def image(request):
    global last_photo
    return send_file(last_photo, max_age=0)

@app.route('/')
async def index(request):
    global motion

    header = """
<html>
  <head>
    <title>ES32-CAM Image Capture</title>
  </head>
  <body>
    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/image">Image</a></li>
        <li><a href="/log">Log</a></li>
        <li><a href="/remount">Remount SD</a></li>
        <li><a href="/reconnect">Network Reconnect</a></li>
        <li><a href="/resetlog">Clear/Reset Log</a></li>
        <li><a href="/sleep">Sleep (10s)</a></li>
    </ul>
    <p>"""
    
    body = ""
    for fname in uos.listdir(save_path):
        body = "{}</br>  - {}".format(body, fname)
    body = "{}<br/><br/>Motion = {} ({}), Temp = {}".format(body, motion, pir.value(), fahrenheit_to_celcius(esp32.raw_temperature()))

    footer = """
    </p>
  </body>
</html>
"""
    return "{}{}{}".format(header, body, footer), 200, {'Content-Type': 'text/html'}

app.run()
