# Change working directory to current script
import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

import json
from pathlib import Path
import datetime
from datetime import timedelta
from itertools import cycle
from settings import margins, exposures, rois
import camera

try:
    SharpCap
except NameError:
    SharpCap = None

camera.init_sharpcap(SharpCap)

UTC = datetime.timezone.utc
IMAGEPATH = r'~/Desktop/SharpCap Captures/'

partial_interval = 3
image_counter = 0

def nextfilename(exposure_time):
    global image_counter
    image_counter += 1
    t = datetime.datetime.strftime(now(), '%Y%m%d-%H%M%S')
    return os.path.expanduser(f'{IMAGEPATH}/{t}-{image_counter:04d}-{exposure_time:.1f}ms.fits')

def now(no_offset=False):
    if no_offset:
        return datetime.datetime.now(UTC)
    return datetime.datetime.now(UTC) + now_offset

def parse(input):
    format = '%Y-%m-%dT%H:%M:%S.%fZ'
    return datetime.datetime.strptime(input, format).replace(tzinfo=UTC)

simulate_time = True

path = Path(r'times.json')
with path.open() as fp:
    settings = json.load(fp)
    time_strings = settings['times']
    times = {k: parse(v) for k, v in time_strings.items() if not k == 'MAX'}

breaks = [
    # before start
    times['C1'] - timedelta(seconds=margins['outside_eclipse']),
    # partial
    times['C2'] - timedelta(seconds=margins['outside_total']),
    # around C2
    times['C2'] + timedelta(seconds=margins['inside_total']),
    # middle
    times['C3'] - timedelta(seconds=margins['inside_total']),
    # around C3
    times['C3'] + timedelta(seconds=margins['outside_total']),
    # partial
    times['C4'] + timedelta(seconds=margins['outside_eclipse']),
    # after end
    datetime.datetime.max.replace(tzinfo=UTC)
]

blocks = ['wait',
          'partial',
          'contacts',
          'middle',
          'contacts',
          'partial',
          'stop']

C_names = ['C1', 'C2', 'C3', 'C4']  # need these to guarantee sorting in py3.4


def block_number_at(t):
    for i, break_time in enumerate(breaks):
        if t < break_time:
            return i
    return len(breaks) - 1  # "stop"


def prev_next_contacts(t):
    next = None
    for i, contact_name in enumerate(C_names):
        contact_time = times[contact_name]
        if t < contact_time:
            next = i
            break

    if next == 0:
        return None, next
    if next == None:
        return 3, None
    return next - 1, next


if simulate_time:
    #simulated_time = times['C1'] - timedelta(seconds=10)
    simulated_time = times['C2'] - timedelta(seconds=35)
    #simulated_time = times['C2'] + timedelta(seconds=20)
    # simulated_time = times['C3'] - timedelta(seconds=30)
    # simulated_time = times['C3'] + timedelta(seconds=25)
    #simulated_time = times['C4'] + timedelta(seconds=-5)
    now_offset = simulated_time - now(no_offset=True)
else:
    now_offset = datetime.timedelta(0)

import time


def tf(t):
    global diff_timedelta_next, diff_timedelta_prev
    prev_c, next_c = prev_next_contacts(t)
    time_string = now().isoformat()[11:21] + ', '
    if prev_c is not None:
        prev_name = C_names[prev_c]
        prev_time = times[prev_name]
        diff_timedelta_prev = prev_time - now()
        diff = (-diff_timedelta_prev).seconds
        time_string += f'{prev_name}+{diff}s, '
    if next_c is not None:
        next_name = C_names[next_c]
        next_time = times[next_name]
        diff_timedelta_next = next_time - now()
        diff = (diff_timedelta_next).seconds
        time_string += f'{next_name}-{diff}s,'
    return time_string


def print_prevnext():
    p = prev_next_contacts(now())
    print(p)
    try:
        print(C_names[p[0]], '..', C_names[p[1]])
    except TypeError:
        # pass
        try:
            print(C_names[p[0]], '...')
        except:
            pass
        try:
            print('...', C_names[p[1]])
        except:
            pass

prev_partial = datetime.datetime.min.replace(tzinfo=UTC)

set_roi = None

while True: # while number 1
    bn = block_number_at(now())
    current_block = blocks[bn]
    next_break = breaks[bn]

    if current_block == 'stop':
        # print_prevnext()
        print(tf(now()), f'C4+{margins["outside_eclipse"]}s, stopping')
        break # number 1

    if current_block == 'wait':
        while now() < next_break:
            # print_prevnext()
            print(tf(now()), f'waiting for C1-{margins["outside_eclipse"]}s ...')
            time.sleep(1)
        continue # number 1

    # current block is now partial, contacts or middle

    # restart loop (while number 1) rapidly until next frame is due (prevent sleeping into next phase)
    if current_block == 'partial':
        diff = now() - prev_partial
        if diff < timedelta(seconds=partial_interval):
            time.sleep(0.1)
            continue # number 1

    bracketing = len(exposures[current_block]) > 1

    bracket_values = cycle(exposures[current_block])

    current_roi = rois[current_block]
    if not set_roi or not (set_roi == current_roi):
        camera.set_roi(current_roi)
        set_roi = current_roi

    if bracketing:
        print(tf(now()), f'{current_block}: start bracketing {exposures[current_block]}')
    else: # set exposure only once at start of block
        exposure = exposures[current_block][0]
        # set exposure
        print(tf(now()), f'{current_block}: start exposures {exposures[current_block]}, set exposure to {exposure:.3f} ms')

    if current_block == 'contacts':
        # first iteration of while number 1 since changing to contacts block
        camera.start_video_capture(exposure)
        print(tf(now()), f'{current_block}: prepared and started video')

        while now() < next_break: # while number 2
            seconds_left = (next_break - now()).total_seconds()
            print(tf(now()), f'{current_block}: waiting for {seconds_left:.0f} s until {next_break.strftime("%H:%M:%S")} for video to finish..')
            time.sleep(1)

        camera.stop_video_capture()
        print(tf(now()), f'{current_block}: stopped video')
        continue # number 1


    else: # partial and middle blocks
        while now() < next_break: # while number 3
            if bracketing:
                exposure = next(bracket_values)
            print(tf(now()), f'{current_block}: capture image, exposure {exposure:.1f} ms')
            camera.capture_single_frame_to(nextfilename(exposure), exposure)

            if current_block == 'partial':
                # in partial block, while number 3 only runs once and image is  taken during first iteration
                prev_partial = now()
                print(tf(now()), f'{current_block}: waiting for {partial_interval}s')
                break # number 3
            time.sleep(.1)
