# IronPython Pad. Write code snippets here and F5 to run. If code is selected, only selection is run.

import json
import datetime
from pathlib import Path
clr.AddReference("System.Drawing")
clr.AddReference("System.Speech")
import System.Drawing
import System.Speech

SharpCap.SelectedCamera.Controls.OutputFormat.Value = 'FITS files (*.fits)'
speech = System.Speech.Synthesis.SpeechSynthesizer()

DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
imagecounter = 1
times = {}

p = Path(r'c:\temp\eclipse.json')
with open(str(p)) as fp:
  times = json.load(fp)
for k in times:
	times[k] = datetime.datetime.strptime(times[k], DATEFORMAT)

print('--- timestamps ---')
for k in times:
	print(k, times[k])
	
	
def capturebracket(**exposuretimes):
    for e in exposuretimes:
	    SharpCap.SelectedCamera.Controls.Exposure.Value = e
		SharpCap.SelectedCamera.CaptureSingleFrameTo(f"c:\\temp\\e\\capture-{imagecounter}-{e*1000}ms.fits")
	imagecounter += 1


print(f'--- waiting for C1 until {times['C1'] - datetime.timedelta(seconds=30)}')
while datetime.datetime.utcnow() < times['C1'] - datetime.timedelta(seconds=30):
    # Before contact
	SharpCap.SelectedCamera.CaptureSingleFrameTo(r"c:\temp\capture.png")
  	time.sleep(1)

while datetime.datetime.utcnow() < times['C2'] - datetime.timedelta(seconds=30):
    # C1..C2
  	time.sleep(1)

speech.Speak("Second Contact! Second Contact! Filters off! Filters off!")	
	
while datetime.datetime.utcnow() < times['MAX'] - datetime.timedelta(seconds=30):
    # C2..C3
  	time.sleep(1)

while datetime.datetime.utcnow() < times['MAX'] + datetime.timedelta(seconds=30):
    # MAX
  	time.sleep(1)

while datetime.datetime.utcnow() < times['C3'] - datetime.timedelta(seconds=30):
    # C3
  	time.sleep(1)

speech.Speak("Filters on! Filters on!")	

	
while datetime.datetime.utcnow() < times['C4'] + datetime.timedelta(seconds=30):
  	time.sleep(1)
