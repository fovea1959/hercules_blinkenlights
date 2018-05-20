#!/usr/bin/env python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import logging, argparse
import requests
import time
import re
import curses
import binascii
import locale

def byte_to_binary(n):
    return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))

def hex_to_binary(h):
    return ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))

def leds(scr, y, x, bn, psw=False):
    for i, c in enumerate(bn):
        c2 = curses.ACS_BULLET if c == '1' else ' '
        if i == 0:
            scr.addch(y,x,c2)
        else:
            if psw and i == 14:
                scr.addch(c2, curses.color_pair(1))
            else:
                scr.addch(c2)

def hex_to_led(h):
    bn = hex_to_binary(h)
    leds = re.sub("1", "*".encode('utf-8'), bn)
    leds = re.sub("0", " ", leds)
    #scr.addstr(2, 1, bn)
    return leds

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--hercules", default='localhost:8038')
    parser.add_argument("--verbose", action='count')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARN)

    scr = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    scr.keypad(0)
    curses.noecho()

    #locale.setlocale(locale.LC_ALL, '')
    #code = locale.getpreferredencoding()
    #scr.addch(1, 40, curses.ACS_BULLET)

    try:
        while True:
            r = requests.get('http://%s/cgi-bin/registers/psw' % (args.hercules))
            m = re.search(r'PSW=(.*)', r.text)
            if m:
                hx = m.group(1).replace(" ", "")
                scr.addstr(1, 1, hx)

                bn = hex_to_binary(hx)
                leds(scr, 2, 1, bn, psw=True)

                wait = bn[14:15]
                scr.addstr(4, 1, 'wait: ')
                scr.addstr(4, 7, wait)
                leds(scr, 4, 10, wait)

                problem_supervisor = bn[15:16]
                scr.addstr(4, 21, 's/p: ')
                scr.addstr(4, 27, problem_supervisor)
                leds(scr, 4, 30, problem_supervisor)

            r = requests.get('http://%s/cgi-bin/registers/general' % (args.hercules))
            grs = re.findall(r'GR(\d\d)=(\S+)', r.text)
            for gr in grs:
                r_num = int(gr[0])
                r_val = gr[1]
                bn = hex_to_binary(r_val)
                scr.addstr(6 + r_num, 1, str(r_num).rjust(2))
                scr.addstr(6 + r_num, 50, r_val)
                leds(scr, 6 + r_num, 10, bn)

            scr.move(3, 1)
            scr.clrtoeol()
            scr.move(3, 1)

            r = requests.get('http://%s/cgi-bin/blinkenlights/devices' % (args.hercules))

            channels = set()
            for line in r.text.split("\n"):
    
                busy = re.search(r'busy', line)
                if busy:
                    dev = line.split(',')[1]
                    channel = dev[1:2]
                    channels.add(channel)

            #scr.addstr(str(channels))
            for channel in xrange(0, 16):
                c_channel = format(channel, 'X')
                if c_channel in channels:
                    scr.addstr(c_channel)
                else:
                    scr.addstr(' ')

            #scr.addstr(line.split(',')[1])
            #scr.addstr(' ')

            scr.refresh()
            time.sleep(0.05)
    except Exception as e:
        print e
        raise
    finally:
        curses.endwin()
        curses.echo()
