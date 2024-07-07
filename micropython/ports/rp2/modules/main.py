from machine import Pin, ADC, RTC
from utime import sleep

def mapfloat(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;

def averageAnalogRead(adc):
    numberOfReadings = 8;
    runningValue = 0;

    for x in range(numberOfReadings):
        # Take an analog reading and return an integer in the range 0-65535
        reading = ADC(adc).read_u16(); 

        #print("DEBUG: {}".format(reading));
        runningValue += reading;
        sleep(0.1)

    runningValue /= numberOfReadings;
    #print("DEBUG: {}".format(reading));

    return runningValue * (3.3 / 65535.0);

def loop():

    timestamp=RTC().datetime()
    timestring="%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] +
                                                timestamp[4:7])
    uvLevelVoltage = averageAnalogRead(Pin(26));

    # No UV light starts at 1V with a maximum of 15mW/cm2 at around 2.8V
    uvIntensity = mapfloat(uvLevelVoltage, 0.99, 2.9, 0.0, 15.0);

    internalTempVoltage =  averageAnalogRead(4);
    internalTemp = 27 - (internalTempVoltage - 0.706) / 0.001721

    print("{},{},{},{},{}".format(timestring,uvLevelVoltage,uvIntensity,internalTempVoltage,internalTemp));
    sleep(5 * 60);


sleep(5); # Just to make sure we see the header
print("DateTime,OutputVoltage,UV Intensity (mW/cm^2),InternalTempVoltage,InternalTemp");
while True:
    loop()
