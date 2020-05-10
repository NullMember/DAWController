import rtmidi
import platform
from typing import Callable
from .enums import *

class DAWController():
    def __init__(self):
        self.__model = 0x00 # device model. 0x10 for Logic Control, 0x11 for Logic Control XT
        self.__deviceID = 0x00
        self.__header = [0x00, 0x00, 0x66, self.__model] #, self.__deviceID] # ignore device id
        self.__serial = 'serialn' # must 7 byte
        self.__challenge = 'chln' # must 4 byte
        self.__version = "0.0.1" # must 5 byte
        self.__online = False
        self.__midiInputName = None
        self.__midiOutputName = None
        self.__midiInputDevices = rtmidi.MidiIn().get_ports()
        self.__midiOutputDevices = rtmidi.MidiOut().get_ports()
        self.__midiInputID = -1
        self.__midiOutputID = -1
        self.__connected = False
        self.__button = [False] * 128
        self.__led = [0] * 128
        self.__fader = [0] * 9
        self.__vpotRing = [0] * 8
        self.__vpotCenter = [False] * 8
        self.__vpotMode = [MCUVPot.SINGLE] * 8
        self.__externalController = 0
        self.__meter = [0] * 8
        self.__lcdDisplay = [0] * 112
        self.__modeDisplay = [0] * 2
        self.__timeDisplay = [0] * 10
        self.__callback = None
    
    def connect(self, midiInput: str, midiOutput: str) -> bool:
        OS = platform.system()
        self.__midiInput = rtmidi.MidiIn()
        self.__midiOutput = rtmidi.MidiOut()
        self.__midiInputName = midiInput
        self.__midiOutputName = midiOutput
        try:
            self.__midiInput.open_virtual_port(self.__midiInputName)
        except NotImplementedError:
            for port in self.__midiInputDevices:
                if self.__midiInputName in port:
                    self.__midiInputID = self.__midiInputDevices.index(port)
                    break
            if self.__midiInputID != -1:
                try:
                    self.__midiInput.open_port(self.__midiInputID)
                    self.__midiInput.ignore_types(sysex = False)
                except rtmidi._rtmidi.InvalidPortError:
                    raise ConnectionError("Please check your input device is plugged in")
                self.__midiInput.set_callback(self.__midiInputCallback)
            else:
                raise NameError("{} is not found".format(self.__midiInputName))
        except:
            raise ConnectionError("Virtual input port exist or cannot created")
        try:
            self.__midiOutput.open_virtual_port(self.__midiOutputName)
        except NotImplementedError:
            for port in self.__midiOutputDevices:
                if self.__midiOutputName in port:
                    self.__midiOutputID = self.__midiOutputDevices.index(port)
                    break
            if self.__midiOutputID != -1:
                try:
                    self.__midiOutput.open_port(self.__midiOutputID)
                except:
                    raise ConnectionError("Please check your output device is plugged in")
            else:
                raise NameError("{} is not found".format(self.__midiOutputName))
        except:
            raise ConnectionError("Virtual output port exist or cannot created")
        self.__connected = True
        return self.__connected

    def disconnect(self) -> bool:
        if self.__connected:
            self.__midiInput.close_port()
            self.__midiOutput.close_port()
            self.__connected = False
        else:
            raise Exception("No midi device connected")
        return self.__connected
    
    def addCallback(self, callback) -> None:
        self.__callback = callback

    def fader(self, *args: int) -> int:
        if len(args) == 0:
            raise SyntaxError("at least 1 argument required")
        if len(args) == 1:
            try:
                return self.__fader[args[0]]
            except:
                raise IndexError("index out of range")
        if len(args) == 2:
            value = min(16383, max(0, args[1]))
            fader = 0xE0 | args[0]
            lsb = value & 0xFF
            msb = (value >> 8) & 0xFF
            self.__midiOutput.send_message([fader, lsb, msb])
            return
    
    def press(self, button: int) -> None:
        if isinstance(button, int):
            self.__midiOutput.send_message([0x90, button, 0x7F])
            self.__button[button] = True
        elif isinstance(button, MCUButton):
            self.__midiOutput.send_message([0x90, button.value, 0x7F])
            self.__button[button.value] = True
        else:
            return
    
    def release(self, button: int) -> None:
        if isinstance(button, int):
            self.__midiOutput.send_message([0x90, button, 0x00])
            self.__button[button] = False
        elif isinstance(button, MCUButton):
            self.__midiOutput.send_message([0x90, button.value, 0x00])
            self.__button[button.value] = False
        else:
            return
    
    def tap(self, button: int) -> None:
        self.press(button)
        self.release(button)
    
    def switch(self, button: int) -> None:
        if self.__button[button]:
            self.release(button)
        else:
            self.press(button)
    
    def led(self, led: int) -> int:
        if isinstance(led, int):
            return self.__led[led]
        elif isinstance(led, MCUButton):
            return self.__led[led.value]
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
        self.__midiOutput.send_message([0xB0, 0x10 | index, value])

    def vpotMode(self, index: int) -> MCUVPot:
        return self.__vpotMode[index]
    
    def vpotRing(self, index: int) -> int:
        return self.__vpotRing[index]
    
    def vpotCenter(self, index: int) -> bool:
        return self.__vpotCenter[index]

    def externalController(self, value: int) -> None:
        value = min(127, max(0, value))
        self.__midiOutput.send_message([0xB0, 0x2E, value])
    
    def jogWheel(self, delta: int) -> None:
        if delta < 0:
            direction = 1
            delta = min(63, max(0, abs(delta)))
            value = (direction << 6) | delta
        else:
            delta = min(63, max(0, delta))
            value = delta
        self.__midiOutput.send_message([0xB0, 0x3C, value])
    
    def meter(self, index: int) -> int:
        return self.__meter[index]

    def lcd(self) -> list:
        return (self.__lcdDisplay[:56], self.__lcdDisplay[56:])
    
    def time(self) -> list:
        return self.__timeDisplay
    
    def mode(self) -> list:
        return self.__modeDisplay

    def __midiInputCallback(self, event, data = None):
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
                self.__led[message[1]] = message[2]
                if self.__callback != None:
                    self.__callback("led", (MCUButton(message[1]), message[2]))
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
                    self.__vpotCenter[index] == False
                else:
                    self.__vpotCenter[index] == True
                self.__vpotMode[index] = MCUVPot(mode)
                self.__vpotRing[index] = ring
                if self.__callback != None:
                    self.__callback("vpot", (index, mode, ring, center))
            # Set 7-segment display
            if (message[1] & 0xF0) == 0x40:
                index = message[1] & 0x0F
                # Time display
                if index < 0x0A:
                    if message[2] < 0x20:
                        self.__timeDisplay[9 - index] = chr(message[2] + 0x40)
                    elif message[2] < 0x40:
                        self.__timeDisplay[9 - index] = chr(message[2])
                    elif message[2] < 0x60:
                        self.__timeDisplay[9 - index] = chr(message[2]) + "."
                    elif message[2] < 0x80:
                        self.__timeDisplay[9 - index] = chr(message[2] - 0x40) + "."
                    if self.__callback != None:
                        self.__callback("time", self.__timeDisplay)
                # Mode display
                else:
                    if message[2] < 0x20:
                        self.__modeDisplay[9 - index] = chr(message[2] + 0x40)
                    elif message[2] < 0x40:
                        self.__modeDisplay[9 - index] = chr(message[2])
                    elif message[2] < 0x60:
                        self.__modeDisplay[9 - index] = chr(message[2]) + "."
                    elif message[2] < 0x80:
                        self.__modeDisplay[9 - index] = chr(message[2] - 0x40) + "."
                    if self.__callback != None:
                        self.__callback("mode", self.__modeDisplay)
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
                self.__meter[index] = level
                if self.__callback != None:
                    self.__callback("meter", (index, level))
        # Pitch Bend Event
        elif command == 0xE0:
            # Fader movement
            value = (message[2] << 7) | message[1]
            self.__fader[channel] = value
            if self.__callback != None:
                self.__callback("fader", (channel, value))
        # System Common Event
        elif command == 0xF0:
            # Sysex Begin
            if channel == 0x00:
                # ignore model
                if message[1:4] == self.__header[0:3]:
                    sysex = message[5:]
                    # Handshake begin (device query)
                    if sysex[0] == 0x00:
                        buffer = [0xF0] + self.__header + [0x01] + [ord(c) for c in self.__serial] + [ord(c) for c in self.__challenge] + [0xF7]
                        # Send serial and challenge
                        self.__midiOutput.send_message(buffer)
                    # Handshake reply (challenge response)
                    elif sysex[0] == 0x02:
                        buffer = [0xF0] + self.__header + [0x03] + [ord(c) for c in self.__serial] + [0xF7]
                        # Confirm connection (always)
                        self.__midiOutput.send_message(buffer)
                        self.__online = True
                        if self.__callback != None:
                            self.__callback("online", self.__online)
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
                        self.__online = False
                        if self.__callback != None:
                            self.__callback("offline", self.__online)
                    # 7-Segment time display
                    elif sysex[0] == 0x10:
                        i = 1
                        while sysex[i] != 0xF7:
                            if i > 10:
                                break
                            if sysex[i] < 0x20:
                                self.__timeDisplay[len(self.__timeDisplay) - i] = chr(sysex[i] + 0x40)
                            elif sysex[i] < 0x40:
                                self.__timeDisplay[len(self.__timeDisplay) - i] = chr(sysex[i])
                            elif sysex[i] < 0x60:
                                self.__timeDisplay[len(self.__timeDisplay) - i] = chr(sysex[i]) + "."
                            elif sysex[i] < 0x80:
                                self.__timeDisplay[len(self.__timeDisplay) - i] = chr(sysex[i] - 0x40) + "."
                            i += 1
                        if self.__callback != None:
                            self.__callback("time", self.__timeDisplay)
                    # 7-Segment mode display
                    elif sysex[0] == 0x11:
                        if sysex[i] < 0x20:
                            if sysex[1] < 0x20:
                                self.__modeDisplay[1] = chr(sysex[1] + 0x40)
                            elif sysex[1] < 0x40:
                                self.__modeDisplay[1] = chr(sysex[1])
                            elif sysex[1] < 0x60:
                                self.__modeDisplay[1] = chr(sysex[1]) + "."
                            elif sysex[1] < 0x80:
                                self.__modeDisplay[1] = chr(sysex[1] - 0x40) + "."
                            if sysex[2] < 0x20:
                                self.__modeDisplay[0] = chr(sysex[2] + 0x40)
                            elif sysex[2] < 0x40:
                                self.__modeDisplay[0] = chr(sysex[2])
                            elif sysex[2] < 0x60:
                                self.__modeDisplay[0] = chr(sysex[2]) + "."
                            elif sysex[2] < 0x80:
                                self.__modeDisplay[0] = chr(sysex[2] - 0x40) + "."
                        if self.__callback != None:
                            self.__callback("mode", self.__modeDisplay)
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
                            self.__lcdDisplay[pos + i] = chr(value)
                        if self.__callback != None:
                            self.__callback("lcd", (self.__lcdDisplay[:56], self.__lcdDisplay[56:]))
                    # Firmware version request
                    elif sysex[0] == 0x13:
                        buffer = [0xF0] + self.__header + [0x14] + [ord(c) for c in self.__version] + [0xF7]
                        self.__midiOutput.send_message(buffer)
                    # Faders to minimum
                    elif sysex[0] == 0x61:
                        for i in range(len(self.__fader)):
                            self.__fader[i] = 0
                            if self.__callback != None:
                                self.__callback("fader", (i, 0))
                    # Turn off all LEDs
                    elif sysex[0] == 0x62:
                        for i in range(len(self.__led)):
                            self.__led[i] = 0
                            if self.__callback != None:
                                self.__callback("led", (i, 0))
                    # Reset
                    elif sysex[0] == 0x63:
                        self.reset()
                        if self.__callback != None:
                            self.__callback("reset", 0)
                    
            pass