#!/usr/bin/env python3

import re
import subprocess

TARGET_X = 1800
TARGET_Y = 200


def get_screen_dimensions():
  dimension_re = re.compile(r'\s*dimensions:\s+(\d+)x(\d+) pixels.*')
  dpy_info = subprocess.check_output(['/usr/bin/xdpyinfo']).decode('utf-8')
  for line in dpy_info.split('\n'):
    m = dimension_re.match(line)
    if m:
      return int(m.group(1)), int(m.group(2))
  return None, None


def find_chrome_popup(screen_width, screen_height):
  # 0x46002e4 (has no name): ()  360x88+4670+2062  +4670+2062
  win_re = re.compile(
      r'\s*([0x0-9a-f]+) ([^:]*):\s*\(\)\s*(\d+)x(\d+)\+(\d+)\+(\d+)')
  windows = subprocess.check_output(
      ['/usr/bin/xwininfo', '-root', '-children']).decode('utf-8')
  for line in windows.split('\n'):
    if not '(has no name):' in line:
      continue
    m = win_re.match(line)
    if m:
      print(line)
      w_id = m.group(1)
      w_width = int(m.group(3))
      w_height = int(m.group(4))
      w_x = int(m.group(5))
      w_y = int(m.group(6))
      if (w_x + w_width == screen_width - 10):
        if w_y + w_height == screen_height - 10:
          print('%s %d x %d  @ %d,%d' % (w_id, w_width, w_height, w_x, w_y))
          # wmctrl does not want to move this.
          cmd = ['/usr/bin/wmctrl', '-i', '-r', w_id,
                 # '-b', 'add,modal',
                 '-e', '10,%d,%d,%d,%d' % (1000, 200, -1, -1)]
                 # '-e', '10,%d,%d,%d,%d' % (1000, 200, w_width, w_height)]
          cmd = ['/usr/bin/xdotool', 'windowmove', w_id, TARGET_X, TARGET_Y]
          print('doing', ' '.join(cmd))
          subprocess.check_call(cmd)


def main():
  screen_width, screen_height = get_screen_dimensions()
  if screen_width == None:
    raise Exception('Can not get screen dimensions')
  find_chrome_popup(screen_width, screen_height)


if __name__ == '__main__':
  main()


"""
xwininfo: Please select the window about which you
          would like information by clicking the
          mouse in that window.

xwininfo: Window id: 0x46002e4 (has no name)

  Absolute upper-left X:  4670
  Absolute upper-left Y:  2062
  Relative upper-left X:  4670
  Relative upper-left Y:  2062
  Width: 360
  Height: 88
  Depth: 24
  Visual: 0x21
  Visual Class: TrueColor
  Border width: 0
  Class: InputOutput
  Colormap: 0x20 (installed)
  Bit Gravity State: NorthWestGravity
  Window Gravity State: NorthWestGravity
  Backing Store State: NotUseful
  Save Under State: no
  Map State: IsViewable
  Override Redirect State: yes
  Corners:  +4670+2062  -10+2062  -10-10  +4670-10
  -geometry 360x88-10-10
"""
