import RPi.GPIO as GPIO
import time
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
app = Flask(__name__)

GPIO.setmode(GPIO.BCM)

# Create a dictionary called pins to store the pin number, name, and pin state:
#GPIO.setup(15, GPIO.OUT)
pins = { }

# Set each pin as an output and make it low:

client = MongoClient('localhost',27017)
db = client.database
pins_from_db = db.pins.find()

for pin in pins_from_db:
    GPIO.setup(pin['pinNum'], GPIO.OUT)
    pinData = { 'name'   : pin['name'],
                'state'  : pin['state'],
                'pinNum' : pin['pinNum'],
                'pwm'    : GPIO.PWM(int(pin['pinNum']), 50),
                'pinType': pin['pinType']}
    pins[pin['pinNum']] = pinData
    #pins[pin['pinNum']]['pwm'].start(7.5)

@app.route("/", methods=['GET', 'POST'])
def main():
    #for pin in pins:
        #GPIO.setup(pin, GPIO.OUT)
        #p = GPIO.PWM(pin, 50)
        #GPIO.output(pin, GPIO.LOW)
    if request.method == 'POST':
        if 'addActuator' in request.form:
            name = str(request.form.get("actuatorName", False))
            pin  = int(request.form.get("actuatorPin", False))
            type = str(request.form.get("actuatorType", False))
            
            GPIO.setup(pin, GPIO.OUT)
            pinInfo = { 'name'   : name,
                        'state'  : False,
                        #'pwm'    : GPIO.PWM(pin, 50),
                        'pinNum' : pin,
                        'pinType': type}
                  
            #print(pins)
            db.pins.insert(pinInfo)
            pinInfo["pwm"] = GPIO.PWM(pin, 50)
            pins[pin] = pinInfo
            #pins[pin]['pwm'].start(7.5)
            
        if 'deleteActuator' in request.form:
            pin = int(request.form.get("deleteActuator", False))
            db.pins.delete_one({"pinNum" : pin})
            pins.pop(pin)
            
    templateData = {
      'pins' : pins
      }
   # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
def action(changePin, action):
   # Convert the pin from the URL into an integer:
    changePin = int(changePin)
   # Get the device name for the pin being changed:
    deviceName = pins[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   
    if pins[changePin]['pinType'] == "switch":
          
        if action == "on":
            pins[changePin]['state'] = True
         
            pins[changePin]['pwm'].start(7.5) #start at 90 degrees
            
            pins[changePin]['pwm'].ChangeDutyCycle(12.5)  # turn towards 0 degree
            
            time.sleep(1)
            
            pins[changePin]['pwm'].ChangeDutyCycle(7.5)

            message = "Turned " + deviceName + " on."
            
        if action == "off":
            pins[changePin]['state'] = False
            
            pins[changePin]['pwm'].ChangeDutyCycle(2.5) #turn towards 180 degree
            time.sleep(1)
            
            pins[changePin]['pwm'].ChangeDutyCycle(7.5)
            
            message = "Turned " + deviceName + " off."
        
        if action == "press": 
            pins[changePin]['pwm'].start(2.5)
            
            pins[changePin]['pwm'].ChangeDutyCycle(7.5)  # turn towards 90 degree

            time.sleep(1) # sleep 1 second
            
            pins[changePin]['pwm'].ChangeDutyCycle(2.5)
            
            message = "Toggled " + deviceName

   # For each pin, read the pin state and store it in the pins dictionary:
    #for pin in pins:
        #pins[pin]['state'] = GPIO.input(pin)

   # Along with the pin dictionary, put the message into the template data dictionary:
    templateData = {
      'pins' : pins,
      'message': message
    }

    return redirect(url_for("main"))
    #return render_template('main.html', **templateData)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)


