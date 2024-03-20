import json
from pathlib import Path
import datetime
from datetime import timedelta
from itertools import cycle

UTC = datetime.timezone.utc

margins = {
    "outside_eclipse": 5,
    "outside_total": 30,
    "inside_total": 25
}

exposures = {
    "partial": [0.800],
    "contacts": [0.032],
    "middle": [1.0, 50.0, 300.0]
}


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
    # simulated_time = times['C1'] - timedelta(seconds=10)
    simulated_time = times['C2'] - timedelta(seconds=35)
    # simulated_time = times['C2'] + timedelta(seconds=20)
    # simulated_time = times['C3'] - timedelta(seconds=30)
    # simulated_time = times['C3'] + timedelta(seconds=25)
    # simulated_time = times['C4'] + timedelta(seconds=-5)
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


while True:
    bn = block_number_at(now())
    current_block = blocks[bn]
    next_break = breaks[bn]

    if current_block == 'stop':
        # print_prevnext()
        print(tf(now()), f'C4+{margins["outside_eclipse"]}s, stopping')
        break

    if current_block == 'wait':
        while now() < next_break:
            # print_prevnext()
            print(tf(now()), f'waiting for C1-{margins["outside_eclipse"]}s ...')
            time.sleep(1)
        continue

    bracket_values = cycle(exposures[current_block])

    while now() < next_break:
        exposure = next(bracket_values)
        # set exposure
        # take image
        # print_prevnext()
        print(tf(now()), f'{current_block}: bracketing {exposures[current_block]}: {exposure}')
        time.sleep(1)






