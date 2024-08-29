# RPI and Pico

* Pico / Pico W
  * Initial test version had a ML8511 UV Sensor - simply loops and logs to serial
     * timestring
     * uvLevelVoltage
     * uvIntensity
     * internalTempVoltage
     * internalTemp
  * Second version extended to include an additinoal (motion) sensor, the combination of them both extended to including
    * moved to a pico w for wifi connectivity
      * used the startard documented connect_to_wifi style of method to bring up the link
      * could extend to check on the log_data periodic run (to ensure we have connectivity prior to publishing to mqtt) 
    * use of ntp time to set the machine.RTC
      * no TZ support as yet - we use UTC heavily so that's fine for now
    * use of microdot for basic web interactions
      * this should help us drop the need for a serial connection to truely move to the edge
      * also test we can use web with other periodic (irq and timer based) processes
      * also so we can run a current meter while we know it's functioning (can it run off grid - via solar)
    * use of IRQ (motion pin)
    * use of timers (log / upload every 5 minutes)
    * use of mqtt to get the data off the device (hivemq)
      * tried requests but building HTTPS with JSON lead to memory issues every time
    * added garbage colection (gc) to see what the memory footprint looked like
* Set-up
  * edit config.py 
  * create a umqtt folder and download source as per https://randomnerdtutorials.com/raspberry-pi-pico-w-mqtt-micropython/
  * download microdot.py from https://github.com/miguelgrinberg/microdot/blob/main/src/microdot/microdot.py
  * build - cp and monitor serial and check web address (remember it's port 5000 by default)
