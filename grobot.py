import serial
import struct

from datetime import datetime
from enum import Enum
import time
import math

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue

from autobahn import wamp
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError

def LocDHT(device):
  if (device == 0):
    return "left"

  if (device == 1):
    return "right"

  return None

def LocWater(device):
  if (device == 0):
    return "la"

  if (device == 1):
    return "lb"

  if (device == 2):
    return "ra"

def LocLight(device):
  return LocWater(device)

class Cmd(Enum):
  Sync = 0
  Power = 1
  PWM = 2

  ReadDHT = 128
  ReadWater = 129
  ReadWater = 130

class ReplySuccess:
  pass

class ReplyDHT:
  def __init__(self, device, temp, humidity, index):
    self.device = device
    self.temp = temp
    self.humidity = humidity
    self.index = index
    self.valid = (not math.isnan(temp)) and (not math.isnan(humidity)) and (not math.isnan(index))
    self.json = {
      "dev": device,
      "location": LocDHT(device),
      "humidity": humidity,
      "temp": temp,
      "index": index
    }

class ReplyWater:
  def __init__(self, device, value):
    self.device = device
    self.value = value
    self.valid = not math.isnan(value)
    self.json = {
      "dev": device,
      "location": LocWater(device),
      "value": value
    }

class ReplyLight:
  def __init__(self, device, value):
    self.device = device
    self.value = value
    self.json = {
      "dev": device,
      "location": LocLight(device),
      "value": value
    }

class ReplyError:
  def __init__(self, log):
    self.log = log
    self.json = log

def LengthReply(cmd):
  if (cmd is Cmd.Sync):
    return 3

  elif (cmd.value < 128):
    return 0

  elif (cmd is Cmd.ReadDHT):
    return 12

  elif (cmd is Cmd.ReadWater):
    return 4

  elif (cmd is Cmd.ReadLight):
    return 4

  return 0

def ReadFloat(byte_s):
  return struct.unpack("f", ''.join(map(chr, byte_s)))[0]

def CreateReply(cmd, device, reply):
  if (cmd is Cmd.Sync):
    if (''.join(map(chr, reply)) == "ACK"):
      return ReplySuccess()
    else:
      return ReplyError("Bad ACK")

  elif (cmd is Cmd.ReadDHT):
    return ReplyDHT(
      device,
      ReadFloat(reply[0:4]),
      ReadFloat(reply[4:8]),
      ReadFloat(reply[8:12]))

  elif (cmd is Cmd.ReadWater):
    return ReplyWater(device, ReadFloat(reply))

  elif (cmd is Cmd.ReadLight):
    return ReplyLight(device, ReadFloat(reply))

  assert len(reply) == 0
  return ReplySuccess()





class ArduinoCom(ApplicationSession):

  def SendCmd(self, cmd, dev, val):
    # Write
    #self.ser.flushOutput()
    #self.ser.flushInput()
    time.sleep(.1)

    sent = [0xFF, 0xFF, cmd.value, dev, val]
    self.ser.write(''.join(map(chr, sent)))
    self.ser.flush()

    # Read
    cbyte = 2 + LengthReply(Cmd(cmd));
    reply = self.ser.read(cbyte);
    reply = map(ord, reply)

    #error
    if (len(reply) < cbyte):
      return ReplyError("Reply Time Out [" + str(len(reply)) + "/" + str(cbyte) + "]")

    print("Sent: [" + ", ".join(map(str, sent)) + "]")
    print("Rec: [" + ", ".join(map(str, reply)) + "]")

    # parse response
    head = reply[-2:]
    reply = reply[0:-2]

    # calc checksum
    checksumOut = sent[2] ^ sent[3] ^ sent[4]
    checksumIn = 0
    for b in reply:
      checksumIn = checksumIn ^ b

    # verify checksum
    if (head[1] != checksumIn):
      return ReplyError("Error Reading From Arduino")

    if (head[0] != checksumOut):
      return ReplyError("Error Writing To Arduino")

    # Success
    return CreateReply(cmd, dev, reply)

  def BotDo(self, cmd, dev, val):
    return self.SendCmd(cmd, dev, val)

  def TryConnect(self, name):
    self.ser = serial.Serial("/dev/tty" + name, 57600, timeout=.1)
    print("Connected To Arduino On " + name)

  @inlineCallbacks
  def onJoin(self, details):
    try:
      self.TryConnect("ACM0")
    except:
      self.TryConnect("ACM1")

    ack = None
    trys = 0

    while isinstance(ack, ReplySuccess) == False:
      trys = trys + 1
      if trys > 150:
        raise IOError("Failed to Connect to Arduino")

      time.sleep(.1)
      ack = self.SendCmd(Cmd.Sync, 0, 0)

    self.ser.timeout = 2
    print("Connected To Arduino After " + str(trys) + " Trys.")
    reg = yield self.register(self.BotDo, u'bot.do')
    print("Arduino Com Registered.")



sensors = []

for i in range(0, 2):
  sensors.append(
    { "cmd": Cmd.ReadDHT, "reply": ReplyDHT, "channel": "bot.sensor.dht", "dev": i })

for i in range(0, 3):
  sensors.append(
    { "cmd": Cmd.ReadWater, "reply": ReplyWater, "channel": "bot.sensor.water", "dev": i })

for i in range(0, 3):
  sensors.append(
    {"cmd": Cmd.ReadLight, "reply": ReplyLight, "channel": "bot.sensor.light", "dev": i })


class GroBot(ApplicationSession):

  def Publish(self, channel, msg):
    #print("(" + channel + "): " + str(msg))
    return self.publish(channel, msg)

  def InternalError(self, msg):
    print("[ALERT]: " + msg)
    return self.Publish(u'bot.alert', {
      "severity": "moderate",
      "message": msg,
    })

  @inlineCallbacks
  def DoCmd(self, cmd, typ, channel, lmbda, dev = 0, val = 0):
    reply = yield self.call(u'bot.do', cmd, dev, val)

    if isinstance(reply, typ):
      if (lmbda != None):
        lmbda(typ)

      if (channel != None):
        if (reply.valid):
          yield self.Publish(channel, reply.json)
        else:
          yield self.InternalError(channel.rpartition(u".")[2].capitalize() + u" " + str(dev) + u": Not Connected")

    elif isinstance(reply, ReplyError):
      yield self.InternalError(reply.log)

    else:
      yield self.InternalError("Invalid Response From Cmd: " + str(reply))

  @inlineCallbacks
  def InitSensors(self):
    for sensor in sensors:
      yield self.Publish(sensor["channel"], {"dev": sensor["dev"]})

  @inlineCallbacks
  def ReadSensors(self):
    for sensor in sensors:
        yield self.DoCmd(sensor["cmd"], sensor["reply"], sensor["channel"], None, sensor["dev"])

  @inlineCallbacks
  def ReadDHT(self):
    for i in range(0, 2):
      yield self.DoCmd(Cmd.ReadDHT, ReplyDHT, u"bot.sensor.dht", None, i)

  @inlineCallbacks
  def ReadWater(self):
    for i in range(0, 3):
      yield self.DoCmd(Cmd.ReadWater, ReplyWater, u"bot.sensor.water", None, i)

  @inlineCallbacks
  def onJoin(self, details):
    yield self.InitSensors()
    yield sleep(1)

    t = 0
    while True:
      yield self.ReadSensors()
      #yield self.ReadDHT()
      #yield self.ReadWater()
      yield sleep(3)

