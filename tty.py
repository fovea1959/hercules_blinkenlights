#!/usr/bin/python2

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import logging
import requests
import time
import re
import curses
import binascii

def byte_to_binary(n):
    return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))

def hex_to_binary(h):
    return ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))

def hex_to_led(h):
    bn = hex_to_binary(h)
    leds = re.sub("1", "*", bn)
    leds = re.sub("0", " ", leds)
    #scr.addstr(2, 1, bn)
    return leds

if __name__ == '__main__':
    scr = curses.initscr()
    scr.keypad(0)
    curses.noecho()

    try:
        while True:
            r = requests.get('http://localhost:8038/cgi-bin/registers/psw')
            m = re.search(r'PSW=(.*)', r.text)
            if m:
                hx = m.group(1).replace(" ", "")
                scr.addstr(1, 1, hx)
                scr.addstr(3, 1, hex_to_led(hx))
            r = requests.get('http://localhost:8038/cgi-bin/registers/general')
            grs = re.findall(r'GR(\d\d)=(\S+)', r.text)
            for gr in grs:
                r_num = int(gr[0])
                r_val = gr[1]
                scr.addstr(5 + r_num, 1, str(r_num).rjust(2))
                scr.addstr(5 + r_num, 50, r_val)
                scr.addstr(5 + r_num, 10, hex_to_led(r_val))

            scr.refresh()
            time.sleep(0.05)
    except Exception as e:
        print e
        raise e
    finally:
        curses.endwin()
        curses.echo()
