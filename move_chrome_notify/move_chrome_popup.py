#!/usr/bin/env python3
"""Find chrome notification popups and move them to a new location."""

import argparse
import os
import re
import subprocess

DEFAULT_MOVETO_XY='2000,200'


def get_screen_dimensions(display):
  dimension_re = re.compile(r'\s*dimensions:\s+(\d+)x(\d+) pixels.*')
  dpy_info = subprocess.check_output(
      ['/usr/bin/xdpyinfo', '-display', display]).decode('utf-8')
  for line in dpy_info.split('\n'):
    m = dimension_re.match(line)
    if m:
      return int(m.group(1)), int(m.group(2))
  return None, None


def find_and_move_chrome_popup(screen_width, screen_height, options):
  """Find the chrome notification popup and move it to a new location.

  Finds all top level windows looking for ones that are place -10,-10
  from the bottom corner of the screen. Move those to another place.

  Args:
    screen_width: width of screen
    screen_height: height of screen
    options: global options
  """
  to_x, to_y = (int(x) for x in options.move_to.split(','))
  # 0x46002e4 (has no name): ()  360x88+4670+2062  +4670+2062
  win_re = re.compile(
      r'\s*([0x0-9a-f]+) ([^:]*):\s*\(\)\s*(\d+)x(\d+)\+(\d+)\+(\d+)')
  windows = subprocess.check_output(
      ['/usr/bin/xwininfo',
       '-display', options.display,
       '-root', '-children']).decode('utf-8')
  for line in windows.split('\n'):
    if '(has no name):' not in line:
      continue
    m = win_re.match(line)
    if m:
      w_id = m.group(1)
      w_width = int(m.group(3))
      w_height = int(m.group(4))
      w_x = int(m.group(5))
      w_y = int(m.group(6))
      if w_x + w_width == screen_width - 10:
        if w_y + w_height == screen_height - 10:
          # print('%s %d x %d  @ %d,%d' % (w_id, w_width, w_height, w_x, w_y))
          # wmctrl does not work for the popup, but it does for others
          cmd = ['/usr/bin/wmctrl', '-i', '-r', w_id,
                 '-e', '10,%d,%d,%d,%d' % (to_x, to_y, -1, -1)]
          cmd = ['/usr/bin/xdotool', 'windowmove', w_id, str(to_x), str(to_y)]
          print('doing:', ' '.join(cmd))
          if not options.dry_run:
            subprocess.check_call(cmd)


def main():
  parser = argparse.ArgumentParser(
      description='Move the chrome notification popup to a place I can see it.')
  parser.add_argument('--display', default=':0', help='xdisplay')
  parser.add_argument(
      '--dry_run', '-n', action='store_true',
      help='Just print effect, do not do it')
  parser.add_argument(
      '--move_to', default=DEFAULT_MOVETO_XY,
      help='x,y coordinate to move window to')
  options = parser.parse_args()
  # Note: xdotool requires display via then environment
  os.environ['DISPLAY'] = options.display

  screen_width, screen_height = get_screen_dimensions(options.display)
  if screen_width is None:
    raise Exception('Can not get screen dimensions')
  find_and_move_chrome_popup(screen_width, screen_height, options)


if __name__ == '__main__':
  main()
