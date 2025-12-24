from machine import Pin
import utime
trigger = Pin(14, Pin.OUT)
echo = Pin(15, Pin.IN)
def ping():
   trigger.low()
   utime.sleep_us(2)
   trigger.high()
   utime.sleep_us(5)
   trigger.low()
   
   # Wait for the ping to bounce back
   while echo.value() == 0:
       signaloff = utime.ticks_us()
   
   # Wait to the end of the ping
   while echo.value() == 1:
       signalon = utime.ticks_us()
       
   # Calculate how long the ping took
   timepassed = signalon - signaloff
   
   # Convert the time of the ping into meters
   distance = (timepassed * 0.0343) / 2
   
   print("The distance from object is ",distance,"cm")
while True:
   ping()
   utime.sleep(1)
