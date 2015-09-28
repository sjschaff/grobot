
#include "DHT.h"

DHT dht_s[] = {
  DHT(42, DHT22),
  DHT(44, DHT22)
};

int cdht = sizeof(dht_s) / sizeof(DHT);

int relay_s[] = {
  9, 8, 7, 6, 5, 4, 3, 2
};

int crelay = sizeof(relay_s) / sizeof(int);

int water_s[] = {
  A2, A1, A0
};

int cwater = sizeof(water_s) / sizeof(int);

int light_s[] = {
  A7, A6, A3
};

int clight = sizeof(light_s) / sizeof(int);

void setup() {
  Serial.begin(57600);

  for (int i = 0; i < cdht; ++i)
    dht_s[i].begin();

pinMode(13, OUTPUT);
digitalWrite(13, LOW);

  for (int i = 0; i < crelay; ++i)
  {
    pinMode(relay_s[i], OUTPUT);
    digitalWrite(relay_s[i], HIGH);
  }
}

enum Cmd {
  Sync = 0,
  Power = 1,
  PWM = 2,
  ReadTH = 128,
  ReadWater = 129,
  ReadLight = 130,
};

byte checksumOut = 0;

void SendBytes(const byte* bytes, int cbyte)
{
  Serial.write(bytes, cbyte);

  for (int i = 0; i < cbyte; ++i)
    checksumOut ^= bytes[i];
}

void FinishMsg(byte checksumIn)
{
  Serial.write(&checksumIn, 1);
  Serial.write(&checksumOut, 1);
  checksumOut = 0;
}

void DoCmd(byte cmd, byte dev, byte val)
{
  byte checksumIn = cmd ^ dev ^ val;
  bool fSuccess = false;
  
  switch (cmd)
  {
    case Sync:
      SendBytes((byte*)"ACK", 3);
      fSuccess = true;
      break;

    case Power:
      if (dev < crelay)
      {
        digitalWrite(relay_s[dev], val == 0 ? HIGH : LOW);
        fSuccess = true;
      }
      
      break;
     
    case PWM:
    case ReadWater:
      if (dev < cwater)
      {
        float water = analogRead(water_s[dev]) / 1023.0;
        SendBytes((byte*)&water, 4);
        fSuccess = true;
      }

      break;

    case ReadLight:
      if (dev < clight)
      {
        float vlit = 5 * analogRead(light_s[dev]) / 1023.0;
        SendBytes((byte*)&vlit, 4);
        fSuccess = true; 
      }

      break;

    case ReadTH:
      if (dev < cdht)
      {
        DHT& dht = dht_s[dev];
        float humidity = dht.readHumidity();
        float temp = dht.readTemperature(true);
        float hif = dht.computeHeatIndex(temp, humidity);
        
        SendBytes((byte*)&temp, 4);
        SendBytes((byte*)&humidity, 4);
        SendBytes((byte*)&hif, 4);

        fSuccess = true;
      }
      
      break;
  }

  if (!fSuccess)
  {
      // Error, break checksum
      checksumIn = ~checksumIn;
  }

  FinishMsg(checksumIn);
}

// 0xFF 0xFF Cmd Dev Val
const int cmsg = 5;
byte message[cmsg] = { 0, 0, 0, 0, 0 };

void loop() {
  int read = Serial.read();
  
  if (read != -1)
  {
    for (int i = 1; i < cmsg; ++i)
      message[i - 1] = message[i];
     
    message[cmsg - 1] = read;
    
    if (message[0] == 0xFF && message[1] == 0xFF)
    {
      
      DoCmd(message[2], message[3], message[4]);
      
      //digitalWrite(13, HIGH);
      //delay(50);
      //digitalWrite(13, LOW);

      for (int i = 0; i < cmsg; ++i)
        message[i] = 0;
    }
  }
}

