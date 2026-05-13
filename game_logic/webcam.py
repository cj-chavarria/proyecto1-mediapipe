import cv2

class WebCam:
    def __init__(self, camera_idx=0):
        self.cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {camera_idx}")
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.screen_div = self.width // 3
    
    def draw_gui(self, image, calibration_res):
        limit_jump = calibration_res.limit_jump
        limit_crouch = calibration_res.limit_crouch
        left_line_x, rigth_line_x = calibration_res.limit_moving
        
        
        cv2.line(image, (left_line_x, 0), (left_line_x, self.height), (196, 64, 255), 3)
        cv2.putText(image, 'Izquierda', (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 120), 2)
        
        cv2.line(image, (rigth_line_x, 0), (rigth_line_x, self.height), (196, 64, 255), 3)
        cv2.putText(image, 'Derecha', ((rigth_line_x) + 50, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 120), 2)
        
        cv2.line(image, (0, limit_jump), (self.width, limit_jump), (70, 70, 255), 2)
        cv2.line(image, (left_line_x, limit_crouch), (rigth_line_x, limit_crouch), (70, 70, 255), 2)
        
    def read_frame(self):
        """Reads, processes, and returns the frame for MediaPipe."""
        ret, frame = self.cap.read()
        
        if not ret:
            return False, None
    
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return True, rgb_frame

    def external_output(self, frame):
        cv2.imshow('Webcam External', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        cv2.waitKey(1)
    
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()