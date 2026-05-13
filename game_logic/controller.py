import keyboard

class Controller:
    def __init__(self, width, height):
        self.left_line_x = -1
        self.rigth_line_x = -1
        self.last_lane = None
        self.is_moving = False
        self.is_jumping = False
        self.is_crouching = False
        self.is_action = False
    
    def _detect_lane(self, x):
        if x < self.left_line_x:
            return 0 #Left
        elif x > self.left_line_x and x < self.rigth_line_x:
            return 1 #Center
        else:
            return 2 #Right
    
    def _change_lanes(self, chest_x):
        chest_lane = self._detect_lane(chest_x)
        
        match chest_lane:
            case 0:
                if not self.is_moving:
                    print('BOTON IZQUIERDA')
                    keyboard.send('a')
                    self.is_moving = True
            case 1:
                self.is_moving = False
            case 2:
                if not self.is_moving:
                    print('BOTON DERECHA')
                    keyboard.send('d')
                    self.is_moving = True
    
    def _jump_and_crouch(self, chest_y, limit_jump, limit_crouch):
        if chest_y < limit_jump and not self.is_jumping:
            print('BOTON ARRIBA')
            keyboard.send('w')
            self.is_jumping = True
            self.is_crouching = False
        elif chest_y > limit_crouch and not self.is_crouching:
            print('BOTON ABAJO')
            keyboard.send('s')
            self.is_crouching = True
            self.is_jumping =  False
        elif limit_jump <= chest_y <= limit_crouch:
            self.is_jumping = False
            self.is_crouching = False
    
    def _action_button(self, r_hand_x, r_hand_y, l_hand_x, l_hand_y, limit):
        r_hand_lane = self._detect_lane(r_hand_x)
        l_hand_lane = self._detect_lane(l_hand_x)
        
        pose_detected = (
            r_hand_lane == 2 and r_hand_y < limit and
            l_hand_lane == 0 and l_hand_y < limit
        )
        
        if pose_detected and not self.is_action:
            print("BOTON ACTION")
            keyboard.send('space')
            self.is_action = True
        elif not pose_detected:
            self.is_action = False 
    
    def update(self, detect_result, calibration_res):
        if not detect_result and not calibration_res:
            return
        
        self.left_line_x, self.rigth_line_x = calibration_res.limit_moving
        limit_jump = calibration_res.limit_jump
        limit_crouch = calibration_res.limit_crouch
        
        r_hand_x, r_hand_y = detect_result.r_hand_pos
        l_hand_x, l_hand_y = detect_result.l_hand_pos
        
        chest_x, chest_y = detect_result.chest_pos
        
        self._change_lanes(chest_x)
        self._jump_and_crouch(chest_y, limit_jump, limit_crouch)
        self._action_button(r_hand_x, r_hand_y, l_hand_x, l_hand_y, limit_jump)