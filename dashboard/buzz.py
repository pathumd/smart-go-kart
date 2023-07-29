import Adafruit_DHT as dht
h,t = dht.read_retry(dht.DHT22, 12)
print(str(h))
