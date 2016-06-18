Thermoctrl - Automatic Thermostat
===================================================

![Controls](/docs/screenshots/controls.png?raw=true)

This project is the source code to a raspberry pi project I started summer 2014.

Before this, our A/C had a really bad problem in the summer: It would freeze and stop cooling the house.
Unfortunately, the old mechanical thermostat couldn't detect this state and resolve it automatically, so I
started working on a solution myself.

I knew that if I put the A/C under software control, I could write something that would detect that it was frozen
and take care of it. So, I did just that.

## Hardware

![Raspberry Pi](/docs/screenshots/raspberrypi.jpg?raw=true)
![Relay Board](/docs/screenshots/relayboard.jpg?raw=true)

All in all, the hardware was pretty cheap (I imagine this can go as low as $15 if I optimized this for cost).

I wired the pi's GPIO pins into the relay board to switch the 24VAC wires coming from the A/C's relays.

## Layout

* control/ - Houses all the logic used for actual control of the A/C.
 * control/management/commands/docontrol.py - This is the core logic for A/C functionality.
* templog/ - Just a bit of fun - displays a temperature log of the house for the past few hours.
* thermoctrl / - Main page/index