import tornado.ioloop
import tornado.web
import datetime
import gpiozero
import time
import serial
import RPi.GPIO as GPIO
import os


robot = gpiozero.Robot(left=(11,25), right=(9,10))

leftend = gpiozero.DigitalInputDevice(17)
center = gpiozero.DigitalInputDevice(27)
rightend = gpiozero.DigitalInputDevice(22)
leftback = gpiozero.DigitalInputDevice(23)
rightback = gpiozero.DigitalInputDevice(19)

GPIO.setmode(GPIO.BCM)
GPIO.setup(6,GPIO.OUT) #temperature
GPIO.setup(5,GPIO.OUT) #pressure
GPIO.setup(26,GPIO.OUT) #spo2

GPIO.output(5,1)
GPIO.output(6,1)
GPIO.output(26,1)

rfid_dict = {'E235FC8B\r\n': 'A1', 'C0B4FD79\r\n': 'A4', '340B53B9\r\n': 'A3', '7DC476A9\r\n': 'A2'}
active_beds = ('A1','A2','A3','A4','A5','A6')                                        #fetch from main server
left_beds = ('A1','A3')

ser=serial.Serial("/dev/ttyACM0",9600)  #change ACM number as found from ls /dev/tty/ACM*
ser.baudrate = 9600

turn_left = False
line_follow_mode = False


def line_follow_config(fn):
    leftend.when_activated = fn
    rightend.when_activated = fn
    center.when_activated = fn
    leftback.when_activated = fn
    rightback.when_activated = fn


    leftend.when_deactivated = fn
    rightend.when_deactivated = fn
    center.when_deactivated = fn
    leftback.when_deactivated = fn
    rightback.when_deactivated = fn


def stop_line_follow():
    global line_follow_mode
    line_follow_mode = False


def rfid_read():
    global turn_left                                   #rfid taking and decisions
    print("RFID")
    read_ser=ser.readline()
    print(read_ser)
    bed = rfid_dict[read_ser]
    
    if (bed in active_beds):
        print("Active beds are detected")
        turn_left = bed in left_beds
        robot.stop()
        time.sleep(1)
        print("makin a turn for interaction")
        turn_robot()
    else:
        print("not in active beds list")
        print("not active_bed")
        # So that robot automatically moves on to next bed
        robot.forward()
        time.sleep(1)
        line_follow()

        
def turn_robot():
    if turn_left:                                  #interaction left turning
        print("turning_left")
        robot.left()
    else:
        print("turning_right")
        robot.right()
    time.sleep(0.7)
    print("turn is here")
    while True:
        if center.is_active:
            print("center_active")
            time.sleep(0.2)
            print("time_implemented")   #implement timne delay
            robot.stop()
            print("robot_stopped")
            break



def check():

    if not line_follow_mode:
        return

    print(center.is_active , leftend.is_active , rightend.is_active, leftback.is_active , rightback.is_active)


    if center.is_active and rightend.is_active and leftend.is_active:
        robot.forward()
        print("cross_near")
        #time.sleep(0.3)

    elif center.is_active and (not leftend.is_active) and (not rightend.is_active):
        print("forward")
        robot.forward()
    elif (not leftend.is_active) and rightend.is_active:
        robot.right()
        print("right")
    elif leftend.is_active and (not rightend.is_active):
        robot.left()
        print("left")


def line_follow():
    print("line_follow")

    global line_follow_mode
    line_follow_mode = True
    check()


line_follow_config(check)

def examine():
    global turn_left                                        #examination_finish and continue
    turn_left = not turn_left
    turn_robot()
    robot.forward()
    print("forward_after turn")
    time.sleep(0.4)
    print("line_follow_started")
    line_follow()


def stop_robot():
    robot.stop()
    stop_line_follow()


def take_pressure():                                      #pressure taking button
    GPIO.output(5,0)
    time.sleep(0.1)
    GPIO.output(5,1)

def take_temp():
    GPIO.output(6,0)
    time.sleep(0.4)
    GPIO.output(6,1)

def spox():
    GPIO.output(26,0)
    time.sleep(0.5)
    GPIO.output(26,1)
    

def fwd():
    robot.forward()

robo_actions = {
    "forward": fwd,
    "backward": robot.backward,
    "left": robot.left,
    "right": robot.right,
    "stop": stop_robot,
    "line": line_follow,
    "examine": examine,
    "take_pressure": take_pressure,
    "take_temp": take_temp,
    "spox":spox
}


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("main.html")

class CommandHandler(tornado.web.RequestHandler):
    def post(self):
        movement = self.get_body_argument("movement")
        robo_actions[movement]()
        self.write("You wrote " + movement)

settings = dict(
	template_path = os.path.join(os.path.dirname(__file__), "templates"),
	static_path = os.path.join(os.path.dirname(__file__), "static")
	)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/move", CommandHandler),
    ], **settings)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
