import time

simulate = False
SharpCap = None

def init_sharpcap(s):
    global SharpCap, simulate
    SharpCap = s
    if SharpCap == None:
        simulate = True
        print('[camera simulator] SharpCap not found; camera simulation enabled')

def capture_single_frame_to(filename, exposure_ms):
    if simulate:
        print(f'[camera simulator] Capturing single frame, exposure={exposure_ms:0.1f}ms, to={filename}')
        time.sleep(0.3)
        return

    SharpCap.SelectedCamera.Controls.OutputFormat.Value = 'FITS file (*.fits)'
    SharpCap.SelectedCamera.Controls.Exposure.Value = exposure_ms/1000
    SharpCap.SelectedCamera.CaptureSingleFrameTo(filename)

def start_video_capture(exposure_ms):
    if simulate:
        print(f'[camera simulator] Starting video capture, exposure={exposure_ms:0.1f}')
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

    SharpCap.SelectedCamera.StopCapture()
