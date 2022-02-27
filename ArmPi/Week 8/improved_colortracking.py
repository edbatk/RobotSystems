import sys
from perception import Perception
from move import Motion
import Camera
sys.path.append('/home/pi/School/RobotSystems/ArmPi/')

from rossros import Bus, ConsumerProducer, Producer, Consumer, Timer, Printer, runConcurrently

if __name__ == "__main__":
    camera = Camera.Camera()
    perception_bus = Bus((), 'perception_bus')
    
    percep = Perception(camera)
    move = Motion()
    
    percep_producer = Producer(percep, perception_bus, 0.01, 'producer')
    
    # move_consumer = Consumer(move.move_obj(pos1, pos2))
    


