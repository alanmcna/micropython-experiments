import time
import machine
import gc
from umqtt.simple import MQTTClient

motion = machine.Pin(28, machine.Pin.IN)
motion_data=[]

client = None

def boardid():
    b_id = ""
    s = machine.unique_id()
    for b in s:
        b_id = b_id + hex(b)[2:]
    return b_id

def mapfloat(x, in_min, in_max, out_min, out_max):
    gc.collect()
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;

def averageAnalogRead(adc):
    numberOfReadings = 8;
    runningValue = 0;

    for x in range(numberOfReadings):
        # Take an analog reading and return an integer in the range 0-65535
        reading = machine.ADC(adc).read_u16();
        runningValue += reading;
        time.sleep(0.1)

    runningValue /= numberOfReadings;
    gc.collect()
    return runningValue * (3.3 / 65535.0);

def log(s, nl=True):
    if nl:
        print(s)
    else:
        print(s, end="")
    gc.collect()

def connect_to_wifi():
    import network
    import config

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        log("info: connecting to {} wifi network".format(config.wifi_ssid))
        wlan.connect(config.wifi_ssid,config.wifi_password)
    
        while not wlan.isconnected():
            log(".", False)
            time.sleep(1)

        log("info: connected, ip address is {}".format(wlan.ifconfig()[0]))
    else:
        log('info: wifi connected')
    gc.collect()

def set_rtc():
    try:
        import ntptime
        print("Local time before synchronization：%s" %str(time.localtime()))
        ntptime.settime()
        print("Local time after synchronization：%s" %str(time.localtime()))
        log("set_rtc - free memory is {} Bytes".format(gc.mem_free()))
        return True
    except OSError:
        log("set_rtc - failed, moving on - consider setting manually")
    gc.collect()



def read_uv():
    timestamp=machine.RTC().datetime()
    timestring="%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] + timestamp[4:7])
    uvLevelVoltage = averageAnalogRead(machine.Pin(26));

    # No UV light starts at 1V with a maximum of 15mW/cm2 at around 2.8V
    uvIntensity = mapfloat(uvLevelVoltage, 0.99, 2.9, 0.0, 15.0);

    internalTempVoltage = averageAnalogRead(4);
    internalTemp = 27 - (internalTempVoltage - 0.706) / 0.001721
    gc.collect()

    return { 
                "DateTime" : timestring,
                "OutputVoltage": uvLevelVoltage,
                "UVIntensity": uvIntensity,
                "InternalTempVoltage": internalTempVoltage,
                "InternalTemp": internalTemp 
            }

def record_motion(pin):
    global motion_data
    timestamp=machine.RTC().datetime()
    timestring="%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] + timestamp[4:7])
    motion_data = motion_data + [{ "timestamp" : timestring, "value": pin.value(), "flags": pin.irq().flags() }]
    gc.collect()

def log_data():
    import json
    global motion_data

    uv_data = read_uv()

    data = { "uv" : uv_data, "motion": motion_data }
    log(json.dumps(data))

    # connect
    client = connect_mqtt()

    if client: 
        client.publish('pico_w/uv', json.dumps(uv_data))
        client.publish('pico_w/motion', json.dumps(motion_data))
        log('MQTT publishing done.')
    else:
        log('No client connection for MQTT - could not publish')

    motion_data = [] # reset after logging
    gc.collect()

def connect_mqtt():

    # MQTT Parameters
    MQTT_SERVER = config.mqtt_server
    MQTT_PORT = 8883 # for hivemq
    MQTT_USER = config.mqtt_username
    MQTT_PASSWORD = config.mqtt_password
    MQTT_CLIENT_ID = "{}".format(boardid()).encode('ascii')
    MQTT_KEEPALIVE = 7200
    MQTT_SSL = True   # set to False if using local Mosquitto MQTT broker
    MQTT_SSL_PARAMS = {'server_hostname': MQTT_SERVER}

    try:
        client = MQTTClient(client_id=MQTT_CLIENT_ID,
                            server=MQTT_SERVER,
                            port=MQTT_PORT,
                            user=MQTT_USER,
                            password=MQTT_PASSWORD,
                            keepalive=MQTT_KEEPALIVE,
                            ssl=MQTT_SSL,
                            ssl_params=MQTT_SSL_PARAMS)
        client.connect()
        return client
    except Exception as e:
        log('Error connecting to MQTT:', e)
        raise  # Re-raise the exception to see the full traceback
    gc.collect()

### MAIN ###
# Connect to wifi
log("initial - free memory is {} Bytes".format(gc.mem_free()))
gc.enable()

connect_to_wifi()
gc.collect()

set_rtc()
gc.collect()

motion.irq(lambda pin: record_motion(pin), machine.Pin.IRQ_RISING)

# log data every 300s (5m)
tim = machine.Timer(period=300000, mode=machine.Timer.PERIODIC, callback=lambda t:log_data())

from microdot import Microdot, Response, send_file, redirect
app = Microdot()
Response.default_content_type = 'text/html'

@app.route('/', methods=['GET', 'POST'])
async def index(req):
    timestamp=machine.RTC().datetime()
    timestring="%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] + timestamp[4:7])

    return """
<!doctype html>
<html>
  <head>
    <title>PICO_W Microdot</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <h1>PICO_W Microdot</h1>
    <p>Hello, World! The time is {}</p>
    <ul>
        <li><a href="/motion">Motion</a></li>
        <li><a href="/uv">UV</a></li>
    </ul>
  </body>
</html>
""".format(timestring)

@app.route('/motion', methods=['GET'])
async def getMotion(req):
    global motion_data
    return motion_data

@app.route('/uv', methods=['GET'])
async def getUv(req):
    return read_uv()

@app.route('/resettime', methods=['GET'])
async def resetRCTime(req):
    set_rtc()
    return redirect('/')

app.run()
