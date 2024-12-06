# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)

import re
import time
import digitalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
import board
from board import *
import pwmio
import asyncio
import usb_hid
from adafruit_hid.keyboard import Keyboard

# Imports commit mouse
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# comment out these lines for non_US keyboards
#from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
#from adafruit_hid.keycode import Keycode

# uncomment these lines for non_US keyboards
# replace LANG with appropriate language
from keyboard_layout_win_es import KeyboardLayout
from keycode_win_es import Keycode

duckyCommands = {
    'WINDOWS': Keycode.WINDOWS, 'GUI': Keycode.GUI,
    'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 'SHIFT': Keycode.SHIFT,
    'ALT': Keycode.ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL,
    'DOWNARROW': Keycode.DOWN_ARROW, 'DOWN': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW,
    'LEFT': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 'RIGHT': Keycode.RIGHT_ARROW,
    'UPARROW': Keycode.UP_ARROW, 'UP': Keycode.UP_ARROW, 'BREAK': Keycode.PAUSE,
    'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE,
    'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'ESCAPE': Keycode.ESCAPE, 'HOME': Keycode.HOME,
    'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK, 'PAGEUP': Keycode.PAGE_UP,
    'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
    'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB,
    'BACKSPACE': Keycode.BACKSPACE,
    'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
    'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
    'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
    'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
    'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
    'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3,
    'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7,
    'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11,
    'F12': Keycode.F12,
}

# Variables globales

variables = {}
functions = {}
defaultDelay = 0

# Cargar payloads

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

mouse = Mouse(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

#init button
button1_pin = DigitalInOut(GP22) # defaults to input
button1_pin.pull = Pull.UP      # turn on internal pull-up resistor
button1 =  Debouncer(button1_pin)

#init payload selection switch
payload1Pin = digitalio.DigitalInOut(GP4)
payload1Pin.switch_to_input(pull=digitalio.Pull.UP)
payload2Pin = digitalio.DigitalInOut(GP5)
payload2Pin.switch_to_input(pull=digitalio.Pull.UP)
payload3Pin = digitalio.DigitalInOut(GP10)
payload3Pin.switch_to_input(pull=digitalio.Pull.UP)
payload4Pin = digitalio.DigitalInOut(GP11)
payload4Pin.switch_to_input(pull=digitalio.Pull.UP)

def convertLine(line):
    newline = []
    # print(line)
    # loop on each key - the filter removes empty values
    for key in filter(None, line.split(" ")):
        key = key.upper()
        # find the keycode for the command in the list
        command_keycode = duckyCommands.get(key, None)
        if command_keycode is not None:
            # if it exists in the list, use it
            newline.append(command_keycode)
        elif hasattr(Keycode, key):
            # if it's in the Keycode module, use it (allows any valid keycode)
            newline.append(getattr(Keycode, key))
        else:
            # if it's not a known key name, show the error for diagnosis
            print(f"Unknown key: <{key}>")
    # print(newline)
    return newline

def runScriptLine(line):
    if isinstance(line, str):
        line = convertLine(line)
    for k in line:
        kbd.press(k)
    kbd.release_all()

def sendString(line):
    layout.write(line)

def parseMouseCommand(line):
    if line.startswith('CLICK'):
        if line[6:] == 'LEFT':
            mouse.click(Mouse.LEFT_BUTTON)
        elif line[6:] == 'RIGHT':
            mouse.click(Mouse.RIGHT_BUTTON)
        elif hasattr(Mouse, line[6:]):
            mouse.click(getattr(Mouse, line[6:]))

    elif line.startswith('MOVE'):
        x, y = line[5:].split(',')
        x, y = int(x), int(y)

        mouse.move(x, y)
    elif line.startswith('WHEEL'):
        wheel = int(line[5:])
        mouse.move(wheel=wheel)

    elif line.startswith('PRESS'):
        if line[6:] == 'LEFT':
            mouse.press(Mouse.LEFT_BUTTON)
        elif line[6:] == 'RIGHT':
            mouse.press(Mouse.RIGHT_BUTTON)
        elif hasattr(Mouse, line[6:]):
            mouse.press(getattr(Mouse, line[6:]))

    elif line.startswith('RELEASE'):
        if line[8:] == 'LEFT':
            mouse.release(Mouse.LEFT_BUTTON)
        elif line[8:] == 'RIGHT':
            mouse.release(Mouse.RIGHT_BUTTON)
        elif hasattr(Mouse, line[8:]):
            mouse.release(getattr(Mouse, line[8:]))

def parseLine(line, script_lines):
    global defaultDelay, variables, functions
    line = line.strip()
    if(line[0:3] == "REM"):
        # ignore ducky script comments
        pass
    elif(line[0:5] == "DELAY"):
        time.sleep(float(line[6:])/1000)
    elif(line[0:6] == "STRING"):
        sendString(line[7:])
    elif line.startswith("MOUSE"):
        parseMouseCommand(line[6:])
    elif line.startswith("CC"):
        CC_KEY = line[3:]
        if hasattr(ConsumerControlCode, CC_KEY):
            cc.send(getattr(ConsumerControlCode, CC_KEY))
    elif(line[0:5] == "PRINT"):
        print("[SCRIPT]: " + line[6:])
    elif(line[0:6] == "IMPORT"):
        runScript(line[7:])
    elif(line[0:13] == "DEFAULT_DELAY"):
        defaultDelay = int(line[14:]) * 10
    elif(line[0:12] == "DEFAULTDELAY"):
        defaultDelay = int(line[13:]) * 10
    elif(line[0:21] == "WAIT_FOR_BUTTON_PRESS"):
        button_pressed = False
        # NOTE: we don't use assincio in this case because we want to block code execution
        while not button_pressed:
            button1.update()

            button1Pushed = button1.fell
            button1Released = button1.rose
            button1Held = not button1.value

            if(button1Pushed):
                print("Button 1 pushed")
                button_pressed = True
    elif line.startswith("VAR"):
        _, var, _, value = line.split()
        variables[var] = int(value)
    elif line.startswith("FUNCTION"):
        func_name = line.split()[1]
        functions[func_name] = []
        line = next(script_lines).strip()
        while line != "END_FUNCTION":
            functions[func_name].append(line)
            line = next(script_lines).strip()
    elif line.startswith("WHILE"):
        condition = re.search(r'\((.*?)\)', line).group(1)
        var_name, _, condition_value = condition.split()
        condition_value = int(condition_value)
        loop_code = []
        line = next(script_lines).strip()
        while line != "END_WHILE":
            if not (line.startswith("WHILE")):
                loop_code.append(line)
            line = next(script_lines).strip()
        while variables[var_name] > condition_value:
            for loop_line in loop_code:
                parseLine(loop_line, {})
            variables[var_name] -= 1
    elif line in functions:
        updated_lines = []
        inside_while_block = False
        for func_line in functions[line]:
            if func_line.startswith("WHILE"):
                inside_while_block = True  # Start skipping lines
                updated_lines.append(func_line)
            elif func_line.startswith("END_WHILE"):
                inside_while_block = False  # Stop skipping lines
                updated_lines.append(func_line)
                parseLine(updated_lines[0], iter(updated_lines))
                updated_lines = []  # Clear updated_lines after parsing
            elif inside_while_block:
                updated_lines.append(func_line)
            elif not (func_line.startswith("END_WHILE") or func_line.startswith("WHILE")):
                parseLine(func_line, iter(functions[line]))
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)

def getProgrammingStatus():
    # check GP0 for setup mode
    # see setup mode for instructions
    progStatusPin = digitalio.DigitalInOut(GP0)
    progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
    progStatus = not progStatusPin.value
    return(progStatus)

def runScript(file):
    global defaultDelay

    duckyScriptPath = file
    try:
        with open(duckyScriptPath, "r", encoding='utf-8') as f:
            script_lines = iter(f.readlines())
            previousLine = ""
            for line in script_lines:
                print(f"runScript: {line}")
                
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine, script_lines)
                        time.sleep(float(defaultDelay) / 1000)
                else:
                    parseLine(line, script_lines)
                    previousLine = line
                time.sleep(float(defaultDelay) / 1000)
    except OSError as e:
        print("Unable to open file", file)
        
def selectPayload():
    global payload1Pin, payload2Pin, payload3Pin, payload4Pin
    payload = "payload.dd"
    # check switch status
    # payload1 = GPIO4 to GND
    # payload2 = GPIO5 to GND
    # payload3 = GPIO10 to GND
    # payload4 = GPIO11 to GND
    payload1State = not payload1Pin.value
    payload2State = not payload2Pin.value
    payload3State = not payload3Pin.value
    payload4State = not payload4Pin.value

    if payload1State:
        payload = "payload.dd"

    elif payload2State:
        payload = "payload2.dd"

    elif payload3State:
        payload = "payload3.dd"

    elif payload4State:
        payload = "payload4.dd"

    else:
        # if all pins are high, then no switch is present
        # default to payload1
        payload = "payload.dd"

    return payload

async def blink_led(led):
    print("Blink")
    if(board.board_id == 'raspberry_pi_pico'):
        blink_pico_led(led)
    elif(board.board_id == 'raspberry_pi_pico_w'):
        blink_pico_w_led(led)

async def blink_pico_led(led):
    print("starting blink_pico_led")
    led_state = False
    while True:
        if led_state:
            #led_pwm_up(led)
            #print("led up")
            for i in range(100):
                # PWM LED up and down
                if i < 50:
                    led.duty_cycle = int(i * 2 * 65535 / 100)  # Up
                await asyncio.sleep(0.01)
            led_state = False
        else:
            #led_pwm_down(led)
            #print("led down")
            for i in range(100):
                # PWM LED up and down
                if i >= 50:
                    led.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)  # Down
                await asyncio.sleep(0.01)
            led_state = True
        await asyncio.sleep(0)

async def blink_pico_w_led(led):
    print("starting blink_pico_w_led")
    led_state = False
    while True:
        if led_state:
            #print("led on")
            led.value = 1
            await asyncio.sleep(0.5)
            led_state = False
        else:
            #print("led off")
            led.value = 0
            await asyncio.sleep(0.5)
            led_state = True
        await asyncio.sleep(0.5)

async def monitor_buttons(button1):
    global inBlinkeyMode, inMenu, enableRandomBeep, enableSirenMode,pixel
    print("starting monitor_buttons")
    button1Down = False
    while True:
        button1.update()

        button1Pushed = button1.fell
        button1Released = button1.rose
        button1Held = not button1.value

        if(button1Pushed):
            print("Button 1 pushed")
            button1Down = True
        if(button1Released):
            print("Button 1 released")
            if(button1Down):
                print("push and released")

        if(button1Released):
            if(button1Down):
                # Run selected payload
                payload = selectPayload()
                print("Running ", payload)
                runScript(payload)
                print("Done")
            button1Down = False

        await asyncio.sleep(0)