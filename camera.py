import time

simulate = not('SharpCap' in globals())
if simulate:
    print('[camera simulator] SharpCap not found; camera simulation enabled')

def capture_single_frame_to(filename, exposure_ms):
    if simulate:
        print(f'[camera simulator] Capturing single frame, exposure={exposure_ms}ms, to={filename}')
        time.sleep(0.3)
        return

    SharpCap.SelectedCamera.Controls.OutputFormat.Value = 'FITS file (*.fits)'
    SharpCap.SelectedCamera.Controls.Exposure.Value = exposure_ms
    SharpCap.SelectedCamera.CaptureSingleFrameTo(filename)

def start_video_capture(exposure_ms):
    if simulate:
        print(f'[camera simulator] Starting video capture, exposure={exposure_ms}')
        return

    SharpCap.SelectedCamera.Controls.OutputFormat.Value = 'FITS file (*.fits)'
    SharpCap.SelectedCamera.CaptureConfig.CaptureLimitType = SharpCap.SelectedCamera.CaptureConfig.CaptureLimitType.Unlimited
    SharpCap.SelectedCamera.PrepareToCapture()
    SharpCap.SelectedCamera.RunCapture()

def stop_video_capture():
    if simulate:
        print(f'[camera simulator] Stopping video capture')
        return

    SharpCap.SelectedCamera.StopCapture()
