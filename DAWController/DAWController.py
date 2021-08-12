import rtmidi
import rtmidi.midiutil
from typing import Union
from .enums import *

class DAWController():
    def __init__(self):
        self._model = 0x00 # device model. 0x10 for Logic Control, 0x11 for Logic Control XT
        self._deviceID = 0x00
        self._header = [0x00, 0x00, 0x66, self._model] #, self.__deviceID] # ignore device id
        self._serial = 'serialn' # must 7 byte
        self._challenge = 'chln' # must 4 byte
        self._version = "0.0.1" # must 5 byte
        self._online = False
        self._midiInput = None
        self._midiOutput = None
        self._midiInputName = None
        self._midiOutputName = None
        self._connected = False
        self._button = [False] * 128
        self._led = [0] * 128
        self._fader = [0] * 9
        self._vpotRing = [0] * 8
        self._vpotCenter = [False] * 8
        self._vpotMode = [MCUVPot.SINGLE] * 8
        self._externalController = 0
        self._meter = [0] * 8
        self._lcdDisplay = [0] * 112
        self._modeDisplay = [0] * 2
        self._timeDisplay = [0] * 10
        self._callback = None
    
    def connect(self, midiInput: str, midiOutput: str) -> bool:
        try:
            self._midiInput, self._midiInputName = rtmidi.midiutil.open_midiinput(midiInput, use_virtual = True, interactive = False)
            self._midiOutput, self._midiOutputName = rtmidi.midiutil.open_midioutput(midiOutput, use_virtual = True, interactive = False)
        except:
            raise ConnectionError("Midi port not exist and virtual port already exist or cannot created")
        self._midiInput.ignore_types(sysex = False)
        self._midiInput.set_callback(self._midiInputCallback)
        self._connected = True
        return self._connected

    def disconnect(self) -> bool:
        if self._connected:
            self._midiInput.close_port()
            self._midiOutput.close_port()
            self._connected = False
        else:
            raise Exception("No midi device connected")
        return self._connected
    
    def setCallback(self, callback) -> None:
        self._callback = callback

    def fader(self, index: int, value: Union[int, None] = None) -> int:
        if value == None:
            return self._fader[index]
        else:
            value = min(16383, max(0, value))
            fader = 0xE0 | index
            lsb = value & 0x7F
            msb = (value >> 7) & 0x7F
            self._midiOutput.send_message([fader, lsb, msb])
    
    def press(self, button: Union[int, MCUButton]) -> None:
        if isinstance(button, int):
            self._midiOutput.send_message([0x90, button, 0x7F])
            self._button[button] = True
        elif isinstance(button, MCUButton):
            self._midiOutput.send_message([0x90, button.value, 0x7F])
            self._button[button.value] = True
        else:
            return
    
    def release(self, button: Union[int, MCUButton]) -> None:
        if isinstance(button, int):
            self._midiOutput.send_message([0x90, button, 0x00])
            self._button[button] = False
        elif isinstance(button, MCUButton):
            self._midiOutput.send_message([0x90, button.value, 0x00])
            self._button[button.value] = False
        else:
            return
    
    def tap(self, button: Union[int, MCUButton]) -> None:
        self.press(button)
        self.release(button)
    
    def switch(self, button: Union[int, MCUButton]) -> None:
        if isinstance(button, int):
            if self._button[button]:
                self.release(button)
            else:
                self.press(button)
        elif isinstance(button, MCUButton):
            if self._button[button.value]:
                self.release(button.value)
            else:
                self.press(button.value)
    
    def led(self, led: int) -> int:
        if isinstance(led, int):
            return self._led[led]
        elif isinstance(led, MCUButton):
            return self._led[led.value]
        else:
            return
    
    def vpot(self, index: int, delta: int) -> None:
        if delta < 0:
            direction = 1
            delta = min(63, max(0, abs(delta)))
            value = (direction << 6) | delta
        else:
            delta = min(63, max(0, delta))
            value = delta
        self._midiOutput.send_message([0xB0, 0x10 | index, value])

    def vpotMode(self, index: int) -> MCUVPot:
        return self._vpotMode[index]
    
    def vpotRing(self, index: int) -> int:
        return self._vpotRing[index]
    
    def vpotCenter(self, index: int) -> bool:
        return self._vpotCenter[index]

    def externalController(self, value: int) -> None:
        value = min(127, max(0, value))
        self._midiOutput.send_message([0xB0, 0x2E, value])
    
    def jogWheel(self, delta: int) -> None:
        if delta < 0:
            direction = 1
            delta = min(63, max(0, abs(delta)))
            value = (direction << 6) | delta
        else:
            delta = min(63, max(0, delta))
            value = delta
        self._midiOutput.send_message([0xB0, 0x3C, value])
    
    def meter(self, index: int) -> int:
        return self._meter[index]

    def lcd(self) -> list:
        return (self._lcdDisplay[:56], self._lcdDisplay[56:])
    
    def time(self) -> list:
        return self._timeDisplay
    
    def mode(self) -> list:
        return self._modeDisplay

    def _midiInputCallback(self, event, data = None):
        message, deltatime = event
        command = message[0] & 0xF0
        channel = message[0] & 0x0F
        # Note Off Event
        if command == 0x80:
            pass
        # Note On Event
        elif command == 0x90:
            # Set LED status
            if channel == 0x00:
                self._led[message[1]] = message[2]
                if self._callback != None:
                    self._callback("led", (MCUButton(message[1]), message[2]))
        # Polyphonic Key Pressure Event
        elif command == 0xA0:
            pass
        # Control Change Event
        elif command == 0xB0:
            # Set VPot leds
            if (message[1] & 0xF0) == 0x30:
                index = message[1] & 0x0F
                center = (message[2] & 0b01000000) >> 6
                mode = (message[2] & 0b00110000) >> 4
                ring = message[2] & 0b00001111
                if (message[2] & 0b01000000) == 0:
                    self._vpotCenter[index] == False
                else:
                    self._vpotCenter[index] == True
                self._vpotMode[index] = MCUVPot(mode)
                self._vpotRing[index] = ring
                if self._callback != None:
                    self._callback("vpot", (index, mode, ring, center))
            # Set 7-segment display
            if (message[1] & 0xF0) == 0x40:
                index = message[1] & 0x0F
                # Time display
                if index < 0x0A:
                    if message[2] < 0x20:
                        self._timeDisplay[9 - index] = chr(message[2] + 0x40)
                    elif message[2] < 0x40:
                        self._timeDisplay[9 - index] = chr(message[2])
                    elif message[2] < 0x60:
                        self._timeDisplay[9 - index] = chr(message[2]) + "."
                    elif message[2] < 0x80:
                        self._timeDisplay[9 - index] = chr(message[2] - 0x40) + "."
                    if self._callback != None:
                        self._callback("time", self._timeDisplay)
                # Mode display
                else:
                    if message[2] < 0x20:
                        self._modeDisplay[9 - index] = chr(message[2] + 0x40)
                    elif message[2] < 0x40:
                        self._modeDisplay[9 - index] = chr(message[2])
                    elif message[2] < 0x60:
                        self._modeDisplay[9 - index] = chr(message[2]) + "."
                    elif message[2] < 0x80:
                        self._modeDisplay[9 - index] = chr(message[2] - 0x40) + "."
                    if self._callback != None:
                        self._callback("mode", self._modeDisplay)
            # Send
        # Program Change Event
        elif command == 0xC0:
            pass
        # Channel Pressure Event
        elif command == 0xD0:
            # Metering
            if channel == 0x00:
                index = (message[1] & 0b01110000) >> 4
                level = message[1] & 0b00001111
                self._meter[index] = level
                if self._callback != None:
                    self._callback("meter", (index, level))
        # Pitch Bend Event
        elif command == 0xE0:
            # Fader movement
            value = (message[2] << 7) | message[1]
            if self._fader[channel] != value:
                self._fader[channel] = value
                if self._callback != None:
                    self._callback("fader", (channel, value))
        # System Common Event
        elif command == 0xF0:
            # Sysex Begin
            if channel == 0x00:
                # ignore model
                if message[1:4] == self._header[0:3]:
                    sysex = message[5:]
                    # Handshake begin (device query)
                    if sysex[0] == 0x00:
                        buffer = [0xF0] + self._header + [0x01] + [ord(c) for c in self._serial] + [ord(c) for c in self._challenge] + [0xF7]
                        # Send serial and challenge
                        self._midiOutput.send_message(buffer)
                    # Handshake reply (challenge response)
                    elif sysex[0] == 0x02:
                        buffer = [0xF0] + self._header + [0x03] + [ord(c) for c in self._serial] + [0xF7]
                        # Confirm connection (always)
                        self._midiOutput.send_message(buffer)
                        self._online = True
                        if self._callback != None:
                            self._callback("online", self._online)
                    # Transport Button Click Configuration
                    elif sysex[0] == 0x0A:
                        pass
                    # LCD Backlight Saver Configuration
                    elif sysex[0] == 0x0B:
                        pass
                    # Touchless Movable Faders Configuration
                    elif sysex[0] == 0x0C:
                        pass
                    # Fader Touch Sensitivity Configuration
                    elif sysex[0] == 0x0D:
                        pass
                    # Go offline message
                    elif sysex[0] == 0x0F:
                        self._online = False
                        if self._callback != None:
                            self._callback("offline", self._online)
                    # 7-Segment time display
                    elif sysex[0] == 0x10:
                        i = 1
                        while sysex[i] != 0xF7:
                            if i > 10:
                                break
                            if sysex[i] < 0x20:
                                self._timeDisplay[len(self._timeDisplay) - i] = chr(sysex[i] + 0x40)
                            elif sysex[i] < 0x40:
                                self._timeDisplay[len(self._timeDisplay) - i] = chr(sysex[i])
                            elif sysex[i] < 0x60:
                                self._timeDisplay[len(self._timeDisplay) - i] = chr(sysex[i]) + "."
                            elif sysex[i] < 0x80:
                                self._timeDisplay[len(self._timeDisplay) - i] = chr(sysex[i] - 0x40) + "."
                            i += 1
                        if self._callback != None:
                            self._callback("time", self._timeDisplay)
                    # 7-Segment mode display
                    elif sysex[0] == 0x11:
                        if sysex[1] < 0x20:
                            self._modeDisplay[1] = chr(sysex[1] + 0x40)
                        elif sysex[1] < 0x40:
                            self._modeDisplay[1] = chr(sysex[1])
                        elif sysex[1] < 0x60:
                            self._modeDisplay[1] = chr(sysex[1]) + "."
                        elif sysex[1] < 0x80:
                            self._modeDisplay[1] = chr(sysex[1] - 0x40) + "."
                        if sysex[2] < 0x20:
                            self._modeDisplay[0] = chr(sysex[2] + 0x40)
                        elif sysex[2] < 0x40:
                            self._modeDisplay[0] = chr(sysex[2])
                        elif sysex[2] < 0x60:
                            self._modeDisplay[0] = chr(sysex[2]) + "."
                        elif sysex[2] < 0x80:
                            self._modeDisplay[0] = chr(sysex[2] - 0x40) + "."
                        if self._callback != None:
                            self._callback("mode", self._modeDisplay)
                    # LCD data
                    elif sysex[0] == 0x12:
                        i = 0
                        pos = sysex[1]
                        # Parse LCD data
                        for i, value in enumerate(sysex[2:]):
                            if value == 0xF7:
                                break
                            if (pos + i) >= 112:
                                break
                            self._lcdDisplay[pos + i] = chr(value)
                        if self._callback != None:
                            self._callback("lcd", (self._lcdDisplay[:56], self._lcdDisplay[56:]))
                    # Firmware version request
                    elif sysex[0] == 0x13:
                        buffer = [0xF0] + self._header + [0x14] + [ord(c) for c in self._version] + [0xF7]
                        self._midiOutput.send_message(buffer)
                    # Faders to minimum
                    elif sysex[0] == 0x61:
                        for i in range(len(self._fader)):
                            self._fader[i] = 0
                            if self._callback != None:
                                self._callback("fader", (i, 0))
                    # Turn off all LEDs
                    elif sysex[0] == 0x62:
                        for i in range(len(self._led)):
                            self._led[i] = 0
                            if self._callback != None:
                                self._callback("led", (i, 0))
                    # Reset
                    elif sysex[0] == 0x63:
                        self.reset()
                        if self._callback != None:
                            self._callback("reset", 0)
                    
            pass