from gpiozero import Button, LED

pir = []
pir.append(Button(16, pull_up=False))
pir.append(Button(20, pull_up=False))

led = []
led.append(LED(19))
led.append(LED(26))

relay = LED(21)
