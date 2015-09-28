from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn import wamp
from autobahn.wamp.types import CallResult
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.util import sleep
import traceback
import math
import picamera

class CamCom(ApplicationSession):
  def __init__(self, config = None):
    ApplicationSession.__init__(self, config)
    self.debug_app = True
    self.traceback_app = True

  @inlineCallbacks
  def onJoin(self, details):
    cam = picamera.PiCamera()
    cam.contrast = 15
    cam.saturation = 15
    cam.awb_mode = "fluorescent"
    cam.exposure_mode = "sports"
    cam.exposure_compensation = 6
    cam.resolution = (1296, 730)
    yield sleep(2)

    while (True):
      cam.capture("cam/cam.png")
      yield sleep(60)


