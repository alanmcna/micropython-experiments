import time
import machine
import uos
import esp32
import camera
import network

save_path = '.'
image_file = 'image.jpg'
log_file = 'esp32cam.log'

# Network LED
led = machine.Pin(33, machine.Pin.OUT)

# Flash LED
use_flash = False
flash = machine.Pin(4, machine.Pin.OUT)

# Set-up motion detection
motion = False
pir = machine.Pin(3, machine.Pin.IN)  # Can't use serial IO
#pir = machine.Pin(13, machine.Pin.IN) # Can't use SD Card

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def log(s):
    global save_path, log_file
    f = open("{}/{}".format(save_path, log_file), "a")
    print("{}: {}".format(time.time(), s))
    f.write("{}: {}\n".format(time.time(), s))
    f.close()

def connect_to_wifi():
    global led

    if not wlan.isconnected():
        led.off() # reversed (so should show .. while we have no network connectivity)
        log('info: connecting to network...')
        wlan.connect('foo', 'bar')
    
        while not wlan.isconnected():
            pass

        log("info: connected, ip address is {}".format(wlan.ifconfig()[0]))
        led.on() # reversed so should now not show

def handle_interrupt(pin):
    global interrupt_pin, motion
    motion = True
    interrupt_pin = pin 

def mount_sd_card():
    global save_path

    try:
        uos.mount(machine.SDCard(), "/sd")
        save_path = '/sd'
        log('info: SD card mounted.')
    except OSError: 
        log('error: failed to mount SD card.')

    log("info: save path '{}', contains:".format(save_path))
    for fname in uos.listdir(save_path):
        log("  - {}".format(fname))

def take_photo():
    global save_path, image_file

    img = "{}/{}_{}".format(save_path, time.time(), image_file)
    try: 
        log("info: initialise camera")
        camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
        time.sleep(5)

        # wait for sensor to start and focus before capturing image
        log("info: camera capture")
        buf = camera.capture()

        imgFile = open(img, "wb")
        imgFile.write(buf)
        imgFile.close()
        log("info: created image file {}".format(img))

        log("info: de-initialise camera")
        camera.deinit()

    except OSError:
        log("error: failed to initialise camera")

### MAIN ###

# Register interrupt
#pir.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING, handler=handle_interrupt, wake=machine.SLEEP, priority=1)
#pir.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING, handler=handle_interrupt)

# Mount the SD card - save images and logs there if we can
mount_sd_card()

# Connect to wifi
connect_to_wifi()

pir_state = pir.value()

while True:
    motion = pir.value()
    if motion:
        led.on()
        log("debug: motion detected ({}).".format(motion))
        take_photo()
        led.off()
