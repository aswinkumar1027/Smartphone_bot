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

#rfid_dict = {'75C8CE20\r\n': 'A1', '8538E320\r\n': 'A4', '86221222\r\n': 'A3', '7DC476A9\r\n': 'A2'}
rfid_dict = {'75859320\r\n': 'A13', '963B4422\r\n': 'A33', '9618BB22\r\n': 'A70', '75F4B220\r\n': 'A41', '8630D222\r\n': 'A93', '864FD722\r\n': 'A94', '7564B620\r\n': 'A63', '7557FC20\r\n': 'A48', '75BBAD20\r\n': 'A31', '8656E322\r\n': 'A74', '759B1E20\r\n': 'A29', '8555B320\r\n': 'A15', '75E02E20\r\n': 'A36', '86270022\r\n': 'A53', '8592D520\r\n': 'A26', '853B1220\r\n': 'A60', '86931A22\r\n': 'A54', '857B2220\r\n': 'A27', '756D6020\r\n': 'A28', '76ADC822\r\n': 'A97', '7519CC20\r\n': 'A3', '8534F920\r\n': 'A37', '85679120\r\n': 'A16', '759F2120\r\n': 'A80', '8574BF20\r\n': 'A61', '86D64022\r\n': 'A57', '75988620\r\n': 'A21', '850ECC20\r\n': 'A71', '7573DC20\r\n': 'A51', '86D15522\r\n': 'A55', '86E66822\r\n': 'A2', '7589BB20\r\n': 'A91', '850D3920\r\n': 'A89', '96578622\r\n': 'A17', '9650EF22\r\n': 'A52', '8685C422\r\n': 'A34', '855CA420\r\n': 'A59', '85130220\r\n': 'A79', '7569E620\r\n': 'A22', '854D6420\r\n': 'A25', '75933D20\r\n': 'A20', '86E76922\r\n': 'A66', '86CCA622\r\n': 'A49', '75E17920\r\n': 'A47', '75A1DC20\r\n': 'A18', '7578DC20\r\n': 'A32', '86323822\r\n': 'A92', '75F9A620\r\n': 'A62', '85E8A420\r\n': 'A50', '701B8A2B\r\n': 'A98', '759DD720\r\n': 'A58', '9629E522\r\n': 'A6', '75719620\r\n': 'A69', '756F1120\r\n': 'A38', '7599A020\r\n': 'A95', '76D7A222\r\n': 'A87', '85B2E620\r\n': 'A5', '757B0520\r\n': 'A83', '757ED820\r\n': 'A45', '85221A20\r\n': 'A88', '7576BC20\r\n': 'A4', '859E1420\r\n': 'A78', '8658B822\r\n': 'A64', '86EF6522\r\n': 'A23', '86F25022\r\n': 'A73', '757BA820\r\n': 'A40', '86068A22\r\n': 'A7', '859A6D20\r\n': 'A30', '96026C22\r\n': 'A56', '8501A820\r\n': 'A81', '85307E20\r\n': 'A85', '850AEA20\r\n': 'A84', '86081E22\r\n': 'A35', '86375D22\r\n': 'A86', '86E9D022\r\n': 'A42', '852AB720\r\n': 'A14', 'A5D5C622\r\n': 'A100', '755D5620\r\n': 'A96', '7581F020\r\n': 'A39', '75123620\r\n': 'A44', '8676A522\r\n': 'A24', '96127C22\r\n': 'A10', '96335822\r\n': 'A65', '860CCA22\r\n': 'A82', '7594B820\r\n': 'A9', '851E8320\r\n': 'A77', '755AAC20\r\n': 'A67', '76D17522\r\n': 'A46', '76B23C22\r\n': 'A76', '96054322\r\n': 'A72', '96191F22\r\n': 'A12', '8637DE22\r\n': 'A8', '606F782B\r\n': 'A99', '86B79622\r\n': 'A1', '86EEA922\r\n': 'A19', '963D8522\r\n': 'A11', '5AAC20\r\n': 'A68', '8577BF20\r\n': 'A75', '75CC2720\r\n': 'A43', '86A72B22\r\n': 'A90'}
active_beds = ('A1','A2','A3','A4','A5','A6','A10','A11')                                        #fetch from main server
left_beds = ('A1','A2','A3','A4','A5','A6','A7','A10','A11')


ser=serial.Serial("/dev/ttyACM0",19200,timeout=2)  #change ACM number as found from ls /dev/tty/ACM*
ser.baudrate = 19200


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
    print("RFID_READ")
    bed = rfid_dict[rfid_cpy]
    
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
    robot.forward()
    time.sleep(0.3)
    if turn_left:                                  #interaction left turning
        print("turning_left")
        robot.left()
    else:
        print("turning_right")
        robot.right()
    time.sleep(1.4)
    robot.stop()
    robot.forward()
    time.sleep(0.3)
    robot.stop()
    print("turn is here")
    #while True:
     #   if center.is_active:
      #      print("center_active")
       #     time.sleep(0.2)
        #    print("time_implemented")   #implement timne delay
         #   robot.stop()
          #  print("robot_stopped")
           # break


def mod_turn_robot():
    robot.forward()
    time.sleep(0.3)
    if turn_left:                                  #interaction left turning
        print("turning_left")
        robot.left()
    else:
        print("turning_right")
        robot.right()
    print("turn is here")
    time.sleep(1.5)
    while True:
        if center.is_active:
           print("center_active")
           time.sleep(0.2)
           print("time_implemented")   #implement timne delay
           robot.stop()
           print("robot_stopped")
           break



def rfid():
    global rfid_cpy
    ser.flushInput() # flushing out old data
    read_ser=ser.readline()
    print (read_ser)
    rfid_cpy = read_ser
    if read_ser in rfid_dict:
        stop_robot()
        print("detected and stopping robot")
        rfid_read()
    else:
        line_follow()


def check():
    

    if not line_follow_mode:
        return

    print(center.is_active , leftend.is_active , rightend.is_active, leftback.is_active , rightback.is_active)
    

    if center.is_active and rightend.is_active and leftend.is_active:
        print("cross_near")
        robot.forward()
        rfid()
        return

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
    mod_turn_robot()
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
