import tkinter
from time import time, sleep
import numpy as np
from trajectory_functions import Trajectory

preview_time = 1   # time window of trajectory preview  
window_size = 1360   # size of (square) animation window
animation_window_width = 1360    # width of the animation window
animation_window_height = 1200   # height of the animation window
target_ball_radius = 10  
input_ball_radius = 8

class Ball:
    def __init__(self, position, radius, color, canvas):
        self.pos = position
        self.radius = radius
        self.color = color
        self.canvas = canvas
        self.ball = self.canvas.create_oval(self.pos[0]-self.radius,
                                            self.pos[1]-self.radius,
                                            self.pos[0]+self.radius,
                                            self.pos[1]+self.radius,
                                            fill = self.color)

    def move(self, position):
        self.pos = position
        self.canvas.coords(self.ball,
                      self.pos[0]-self.radius,
                      self.pos[1]-self.radius,
                      self.pos[0]+self.radius,
                      self.pos[1]+self.radius)
        return position

def create_animation_window():
  window = tkinter.Tk()
  window.title("Tkinter Animation Demo")
  window.geometry(f'{animation_window_width}x{animation_window_height}')
  return window
 

# Create a canvas for animation and add it to main window
def create_animation_canvas(window):
  canvas = tkinter.Canvas(window)
  canvas.configure(bg="black")
  canvas.pack(fill="both", expand=True)
  return canvas

def draw_preview(canvas, line, trajectory, preview_time, T, t):
    num = 20
    if t < T - preview_time:
        prev_end = t + preview_time
    else:
        prev_end = T

    t_prev = np.linspace(t, prev_end, num)
    traj = trajectory.screen_coordinates(t_prev)
    ypix = np.round(np.linspace(traj[1, 0], traj[1, 0] - 300, num))
    line_array = []
    for i in range(0,num-1):
        line_array += [traj[0, i], ypix[i]]
    canvas.coords(line, line_array)
    return

if __name__ == "__main__":
    T = 120
    trial = 2
    animation_window = create_animation_window()
    animation_canvas = create_animation_canvas(animation_window)
    line = animation_canvas.create_line(0, 0, 0, 0, fill='red', arrow='last', smooth='true', dash=(6,4))

    trajectory = Trajectory("sines", T, None, window_size, trial)
    pos = trajectory.screen_coordinates(0)
    target_ball = Ball(pos, target_ball_radius, "red", animation_canvas)
    input_ball = Ball(pos, input_ball_radius, "white", animation_canvas)
    animation_window.update()

    t0 = time()

    while True:
        t = time() - t0
        draw_preview(animation_canvas, line, trajectory, preview_time, T, t)
        target_ball.move(trajectory.screen_coordinates(t))
        animation_window.update()
        if t > (T):
            print("Stopping: trajectory completed")
            break
