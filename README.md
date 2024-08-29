# RPI and Pico

* Pico / Pico W
  * First version had a ML8511 UV Sensor - simply loops and logs timestring,uvLevelVoltage,uvIntensity,internalTempVoltage,internalTemp micropython/ports/rp2/modules/main.py
  * Second version extended to imclude a motion sensor, the combination of them both extended to including
    * pico_w for wifi connectivity
    * use of ntp time to set the machine.RTC
    * use of microdot for basic web interactions (in case serial was not available - can I use web with other periodic processes etc)
    * use of IRQ (motion pin)
    * use of timers (log and upload every 5 minutes)
    * use of mqtt to get the data off the device (hivemq)
      * tried requests but building HTTPS with JSON lead to memory issues every time
* Set-up
  * edit a config.py to include
  * create a umqtt folder and download source as per https://randomnerdtutorials.com/raspberry-pi-pico-w-mqtt-micropython/
  * download microdit.py from https://github.com/miguelgrinberg/microdot/blob/main/src/microdot/microdot.py
  * build - cp and monitor serial and check web address (remember it's port 5000 by default)
  
