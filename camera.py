import time

simulate = False
SharpCap = None

def init_sharpcap(s):
    global SharpCap, simulate
    SharpCap = s
    if SharpCap == None:
        simulate = True
        print('[camera simulator] SharpCap not found; camera simulation enabled')
        return

    SharpCap.SelectedCamera.Controls.ColourSpace.Value = 'MONO16'
    SharpCap.SelectedCamera.Controls.Gain.Automatic = False
    SharpCap.SelectedCamera.Controls.Gain.Value = 0
    SharpCap.SelectedCamera.Controls.Exposure.Automatic = False
    
def set_roi(widthXheight):
    if simulate:
        print(f'[camera simulator] Set ROI to {widthXheight}')
        return
    if SharpCap.SelectedCamera == None:
        print('CAMERA DISCONNECTED')
        return

    SharpCap.SelectedCamera.Controls.Resolution.Value = widthXheight

def set_pan(pan):
    if simulate:
        print(f'[camera simulator] Set Pan to {pan}')
        return
    if SharpCap.SelectedCamera == None:
        print('CAMERA DISCONNECTED')
        return

    SharpCap.SelectedCamera.Controls.Pan.Value = pan
        

def capture_single_frame_to(filename, exposure_ms):
    if simulate:
        print(f'[camera simulator] Capturing single frame, exposure={exposure_ms:0.3f}ms, to={filename}')
        time.sleep(0.3)
        return
    if SharpCap.SelectedCamera == None:
        print('CAMERA DISCONNECTED')
        return

    SharpCap.SelectedCamera.Controls.OutputFormat.Value = 'FITS file (*.fits)'
    SharpCap.SelectedCamera.Controls.Exposure.Value = exposure_ms/1000
    SharpCap.SelectedCamera.CaptureSingleFrameTo(filename)

def start_video_capture(exposure_ms):
    if simulate:
        print(f'[camera simulator] Starting video capture, exposure={exposure_ms:0.3f}')
        return
    if SharpCap.SelectedCamera == None:
        print('CAMERA DISCONNECTED')
        return

    SharpCap.SelectedCamera.Controls.OutputFormat.Value = 'FITS file (*.fits)'
    SharpCap.SelectedCamera.Controls.Exposure.Value = exposure_ms/1000
    SharpCap.SelectedCamera.CaptureConfig.CaptureLimitType = SharpCap.SelectedCamera.CaptureConfig.CaptureLimitType.Unlimited
    SharpCap.SelectedCamera.PrepareToCapture()
    SharpCap.SelectedCamera.RunCapture()

def stop_video_capture():
    if simulate:
        print(f'[camera simulator] Stopping video capture')
        return
    if SharpCap.SelectedCamera == None:
        print('CAMERA DISCONNECTED')
        return

    SharpCap.SelectedCamera.StopCapture()
