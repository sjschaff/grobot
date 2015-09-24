from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn import wamp
from autobahn.wamp.types import CallResult
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.util import sleep
import traceback
import math
import time

FREQ = 30

class Avg:
  def __init__(self, mp):
    self.mp = mp
    self.count = 1
    self.time = time.time()

  def AddValues(self, mp):
    for e in mp.keys():
      self.mp[e] += mp[e]

    self.count += 1;

  def Ready(self):
    return (time.time() - self.time) >= 30

def ToSqlNum(value):
  if (math.isnan(value)):
    return "NULL"

  return str(value)

def GetOrNull(mp, key):
  if key in mp:
    return mp[key]
  else:
    return float('nan')

def onErr(err):
  print(str(err))

def IFE(dg):
  dg.addErrback(onErr)
  return dg

class DbCom(ApplicationSession):
  def __init__(self, config = None):
    ApplicationSession.__init__(self, config)
    self.debug_app = True
    self.traceback_app = True

  def WriteSensor(self, mp, table, columns):
    try:
      key = (table, mp["dev"]);
      values = dict((k, GetOrNull(mp, k)) for k in columns)

      if key in self.averages:
        avg = self.averages[key]
        avg.AddValues(values)
      else:
        avg = self.averages[key] = Avg(values)

      if (avg.Ready()):
        query = "INSERT INTO " + table + " (" + ", ".join(["dev"] + columns) + ") VALUES (" + ", ".join([str(key[1])] + list(ToSqlNum(avg.mp[x] / avg.count) for x in columns)) + ");"
        self.averages.pop(key)

        print query
        return IFE(self.pool.runOperation(query))

      return None
    except Exception as e:
      print("Exception! " + str(e))
      traceback.print_exc()

  @inlineCallbacks
  def onJoin(self, details):
    try:
      self.averages = dict();
      self.pool = adbapi.ConnectionPool(
          "psycopg2",
          host = '127.0.0.1',
          port = 5432,
          database = 'grobot',
          user = 'grobot',
          password = 'kittylick420')

      def onDht(dht):
        return self.WriteSensor(dht, "dht", ["temp", "humidity", "index"])

      def onWater(water):
        return self.WriteSensor(water, "water", ["value"])

      def onLight(light):
        return self.WriteSensor(light, "light", ["value"])

      yield self.register(self)
      yield self.subscribe(onDht, u"bot.sensor.dht")
      yield self.subscribe(onWater, u"bot.sensor.water")
      yield self.subscribe(onLight, u"bot.sensor.light")
      print("DB Com Connected.")

    except Exception as e:
      print(e)

  @inlineCallbacks
  @wamp.register(u'bot.db.dht')
  def ReadDHT(self, dev):
    result = yield self.pool.runQuery("SELECT CAST(EXTRACT(EPOCH FROM time) as INTEGER), temp, humidity FROM dht WHERE dev = " + str(dev) + " ORDER BY TIME")
    returnValue(result)

  @inlineCallbacks
  @wamp.register(u'bot.db.water')
  def ReadWater(self, dev):
    result = yield self.pool.runQuery("SELECT CAST(EXTRACT(EPOCH FROM time) as INTEGER), value FROM water WHERE dev = " + str(dev) + " ORDER BY TIME")
    returnValue(result)

  @inlineCallbacks
  @wamp.register(u'bot.db.light')
  def ReadLight(self, dev):
    result = yield self.pool.runQuery("SELECT CAST(EXTRACT(EPOCH FROM time) as INTEGER), value FROM light WHERE dev = " + str(dev) + " ORDER BY TIME")
    returnValue(result)


