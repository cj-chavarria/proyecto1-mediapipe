from attr import dataclass
from typing import Tuple
from game_logic.controller import Controller
from game_logic.webcam import WebCam
from game_logic.mp_detection import MPDetection
import time
import cv2
import webview
import base64
import keyboard

class Game:
    def __init__(self, debug = False):
        self.camera = WebCam()
        self.width = self.camera.width
        self.height = self.camera.height
        
        self.detection = MPDetection()
        self.controller = Controller(self.width, self.height)
        
        self.is_calibrated = False
        self.cal_list = []
        self.start_time =  time.time()
        self.limit_jump = None
        self.limit_crouch = None
        self.limit_moving = None
        self.frame_idx = 0
    
        self.debug = debug

        if not self.debug:
            self.window = webview.create_window(
                'GAME',
                'https://poki.com/en/g/subway-surfers',
                maximized=True
            )
        else:
            self.window = webview.create_window('', hidden=True)

        self.is_running = True   
    
    @dataclass
    class CalibrationResult:
        limit_jump: int
        limit_crouch: int
        limit_moving: Tuple[int, int]
    
    def _calibration(self, frame, detection_pos, calibration_time=15):
        if self.is_calibrated:
            return self.CalibrationResult(
                limit_jump = self.limit_jump,
                limit_crouch = self.limit_crouch,
                limit_moving = self.limit_moving
            )
        
        chest_y = detection_pos.chest_pos[1]    
        self.cal_list.append(chest_y)
        cv2.putText(frame, 'CALIBRANDO', (15, self.height//2), cv2.FONT_HERSHEY_SIMPLEX, 3.2, (66, 211, 242), 3)
        
        elapsed = time.time() - self.start_time
        if elapsed > calibration_time:
            y_mean = round(sum(self.cal_list) / len(self.cal_list))
            
            self.limit_jump = y_mean - (self.height // 25)
            self.limit_crouch = y_mean + (self.height // 10)
            
            l_shoulder, r_shoulder = detection_pos.shoulders_pos
            self.limit_moving = (l_shoulder[0]+(self.width // 20), r_shoulder[0]-(self.width // 20))
            
            self.is_calibrated = True
        
        return None
    
    def stream_cam_to_window(self, frame):
        if not self.is_running:
            return
        
        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.jpg', bgr_frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        
        js_code = f"""
            // Attempt fullscreen click once
            if (!window.__fsClicked) {{
                window.__fsClicked = true;
                setTimeout(function() {{
                    var fsButton = document.getElementById('fullscreen-button');
                    if (fsButton) {{ fsButton.click(); }}
                }}, 500);
            }}

            // Create the image element ONLY if it doesn't exist yet
            if (!document.getElementById('webcam_overlay')) {{
                var img = document.createElement('img');
                img.id = 'webcam_overlay';
                img.style.cssText = "position:fixed; bottom:10px; left:10px; width:450px; border:3px solid white; border-radius:10px; z-index:99999; box-shadow:0 0 15px rgba(0,0,0,0.5); pointer-events:none;";
                document.body.appendChild(img);
            }}
            
            // Update the source of the image
            document.getElementById('webcam_overlay').src = 'data:image/jpeg;base64,{jpg_as_text}';
        """
        try:
            if self.window is not None and self.is_running:
                self.window.evaluate_js(js_code)
        except Exception as e:
            print(f'ERROR -> {e}')
    
    def _run(self):
        calibration_res = None
        while self.is_running:
            success, frame = self.camera.read_frame()
            if not success or frame is None:
                continue
            
            timestamp = self.frame_idx*33
            detection_pos = self.detection.from_frame(frame, timestamp, self.width, self.height)
            
            if detection_pos is not None:
                calibration_res = self._calibration(frame, detection_pos)
                if calibration_res is not None:
                    self.controller.update(detection_pos, calibration_res)
                    self.camera.draw_gui(frame, calibration_res)    
            if self.debug:
                self.camera.external_output(frame)
            else:
                self.stream_cam_to_window(frame)
            
            if keyboard.is_pressed('q'):
                self.is_running = False
                self.camera.release()
                if self.window is not None:
                    self.window.destroy()
                break
            
            self.frame_idx += 1
    
    def start(self):
        webview.start(self._run)