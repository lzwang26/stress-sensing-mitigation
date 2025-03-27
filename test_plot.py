import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import random

# Create figure and axis
fig, ax = plt.subplots()
xdata, ydata = [], []
line, = ax.plot([], [], 'r-', lw=2)

# Start time reference
start_time = time.time()

# Initialize function
def init():
    ax.set_xlim(0, 10)  # Initial x-axis range (will adjust dynamically)
    ax.set_ylim(-1, 1)  # y-axis range
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Signal")
    return line,

# Update function
def update(frame):
    current_time = time.time() - start_time  # Elapsed time
    xdata.append(current_time)
    ydata.append(random.randint(0, 1))  # Example: Sine wave
    
    line.set_data(xdata, ydata)

    # Adjust x-axis dynamically to show last 10 seconds
    if current_time > 10:
        ax.set_xlim(current_time - 10, current_time)
    
    return line,

# Create animation
ani = animation.FuncAnimation(fig, update, frames=None, init_func=init, interval=50, blit=False)

plt.show()