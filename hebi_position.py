import pandas as pd
import numpy as np
import keyboard
from hebi_functions import initialize_hebi, get_hebi_feedback, send_hebi_position_command, send_hebi_effort_command
from animation_functions import *

# Initialize initializing controller 1 and 2 integral error sum:
init1_e1 = 0
init1_e2 = 0
init2_e1 = 0
init2_e2 = 0
init_tol1 = 0.1 # rad
init_tol2 = 0.02 # rad
 
# Initialize loop timer previous time:
t_1 = 0

#=== variables for 2 dof ===#
L1 = 0.27
L2 = 0.25
#======#

theta1i = 0.4599
theta2i = 0.4156

def calculate_hebi_position(group, hebi_feedback, scale, offset):
    pos_scale = window_size/(L1+L2)
    theta, omega, torque, hebi_limit_stop_flag = get_hebi_feedback(group, hebi_feedback)
    print(pos_scale)
    theta = theta - np.array([1.58702857, -0.08002613])
    pos = pos_scale*np.array([-L1*np.sin(theta[0]) - L2*np.cos(theta[0]+theta[1]), L1*np.cos(theta[0])-L2*np.sin(theta[0]+theta[1])])
    pos[1] = animation_window_height - pos[1]
    pos += offset
    return pos

# Functions for initial position ========================================================================

def reset_timer():
    global t_1
    t_1 = 0
    t0 = time()
    t = 0
    return t, t0

def loop_timer(t0, T, print_loop_time=False):
    global t_1
    t = time()-t0
    while (t - t_1) < T:
        t = time()-t0
    if print_loop_time:
        print('Loop Time:', round(t-t_1, 8), 'seconds')
    t_1 = t
    return t

def initializing_controller1(theta,theta_d,omega,omega_d, tol):
    global init1_e1
    global init1_e2
    # Gains with cables:
    kp1 = 0.85
    kd1 = 0.055
    ki1 = 0.0035
    kp2 = 0.85
    kd2 = 0.055
    ki2 = 0.0035
    init1_e1 += theta_d[0]-theta[0]
    init1_e2 += theta_d[1]-theta[1]
    effort = np.array([kp1*(theta_d[0]-theta[0]) + kd1*(omega_d[0]-omega[0]) + ki1*init1_e1,
                       kp2*(theta_d[1]-theta[1]) + kd2*(omega_d[1]-omega[1]) + ki2*init1_e2])
    if abs(theta_d[0]-theta[0]) < tol and abs(theta_d[1]-theta[1]) < tol:
        return effort, True
    else:
        return effort, False
    
def initializing_controller2(theta,theta_d,tol):
    global init2_e1
    global init2_e2
    # Gains with cables:
    kp1 = 2.0
    ki1 = 0.15
    kp2 = 2.0
    ki2 = 0.15
    init2_e1 += theta_d[0]-theta[0]
    init2_e2 += theta_d[1]-theta[1]
    effort = np.array([kp1*(theta_d[0]-theta[0]) + ki1*init2_e1,
                       kp2*(theta_d[1]-theta[1]) + ki2*init2_e2])
    if abs(theta_d[0]-theta[0]) < tol and abs(theta_d[1]-theta[1]) < tol:
        return effort, True
    else:
        return effort, False

def set_hebi_position(group, hebi_feedback, theta1i, theta2i):
    print('Moving to initial position')
    theta_d = np.array([theta1i, theta2i])
    omega_d = np.zeros(2)
    converged1 = False
    converged2 = False
    t, t0 = reset_timer()
    while not converged2:
        h_theta, h_omega, _ = get_hebi_feedback(group, hebi_feedback)     
        t = loop_timer(t0, T, print_loop_time=False)
        if not converged1:
            effort, converged1 = initializing_controller1(h_theta,theta_d,h_omega,omega_d, init_tol1)
        else:
            effort, converged2 = initializing_controller2(h_theta,theta_d,init_tol2)
        command.effort = effort
        send_hebi_effort_command(group, command)
        if keyboard.is_pressed('esc'):
            print("(Initialization) Stopping: User input stop command")
            break
    print('Initialization complete')
    print('Running Trajectory')
    return


# ===========================================================================================================

if __name__ == "__main__":
    output = []
    freq = 100 # hz
    square_size = 0.32
    scale_factor = window_size/square_size


    
    group, hebi_feedback, command = initialize_hebi()
    group.feedback_frequency = freq
    group_info = group.request_info()

    if group_info is not None:
        group_info.write_gains("csv/saved_gains.xml")

    theta1i = 0.4599
    theta2i = 0.4156

    set_hebi_position(group, hebi_feedback, theta1i, theta2i)

    animation_window = create_animation_window()
    animation_canvas = create_animation_canvas(animation_window)

    theta, omega, torque, hebi_limit_stop_flag = get_hebi_feedback(group, hebi_feedback) 

    pos0 = calculate_hebi_position(group, hebi_feedback, scale_factor, offset = 0)
    offset = (window_size/2)*np.array([1, 1]) - pos0


    input_ball = Ball(calculate_hebi_position(group, hebi_feedback, scale_factor, offset), input_ball_radius, "white", animation_canvas)
    animation_window.update()

    t0 = time()

    while True:
        pos = calculate_hebi_position(group, hebi_feedback, scale_factor, offset)
        input_ball.move(pos)
        animation_window.update()

        if keyboard.is_pressed('esc'):
            print("Stopping: User input stop command")
            break




