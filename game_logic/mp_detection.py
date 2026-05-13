from attr import dataclass
from pathlib import Path
from typing import Tuple
import mediapipe as mp
import cv2

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

@dataclass
class DetectionResult:
    r_hand_pos: Tuple[int, int]
    l_hand_pos: Tuple[int, int]
    chest_pos: Tuple[int, int]
    shoulders_pos: Tuple[Tuple[int, int],Tuple[int, int]]

class MPDetection:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = Path(__file__).resolve().parent / "mp_model" / "pose_landmarker_heavy.task"
        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=VisionRunningMode.VIDEO,
            num_poses = 1
            )
        self.landmarker = PoseLandmarker.create_from_options(options)
    
    def _get_pixel_pos(self, landmark, width, height):
        return (round(landmark.x * width), round(landmark.y * height))
    
    def from_frame(self, frame, timestamp_ms, width, height, draw_landmarks=True):
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detect_pose = self.landmarker.detect_for_video(mp_img, timestamp_ms).pose_landmarks
        
        if detect_pose:
            landmarks = detect_pose[0]
            
            r_hand_pos = self._get_pixel_pos(landmarks[19], width, height)
            l_hand_pos = self._get_pixel_pos(landmarks[20], width, height)
            r_shoulder_pos = self._get_pixel_pos(landmarks[11], width, height)
            l_shoulder_pos = self._get_pixel_pos(landmarks[12], width, height)
            
            chest_pos = (
                (r_shoulder_pos[0] + l_shoulder_pos[0]) // 2,
                (r_shoulder_pos[1] + l_shoulder_pos[1]) // 2
            )
            
            self.results_pos = DetectionResult(
                r_hand_pos=r_hand_pos,
                l_hand_pos=l_hand_pos,
                chest_pos=chest_pos,
                shoulders_pos=(l_shoulder_pos, r_shoulder_pos)
            )
            
            if draw_landmarks:
                cv2.circle(frame, r_hand_pos, 5, (255, 32, 86), -1)
                cv2.circle(frame, l_hand_pos, 5, (255, 32, 86), -1)
                #cv2.line(frame, r_shoulder_pos, l_shoulder_pos, (237, 106, 255), 2)
                cv2.circle(frame, chest_pos, 8, (237, 106, 255), -1)
            
            return self.results_pos
        return None