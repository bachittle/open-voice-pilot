import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Function to generate the sine wave data
def generate_sine_wave(x_min, x_max, num_points=1000):
    x = np.linspace(x_min, x_max, num_points)
    y = np.sin(x)
    return x, y

# Initialize plot
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)

# Initial x-axis limits
initial_xmax = 4000
ax.set_xlim(0, initial_xmax)
ax.set_ylim(-1, 1)

# Initialize the line
line.set_data([], [])

# Animation function: this is called sequentially
def animate(i):
    # Increase x_max by 4000 with each frame
    x_max = initial_xmax + 4000 * (i + 1)
    x, y = generate_sine_wave(0, x_max)
    
    # Update plot data
    line.set_data(x, y)
    
    # Update x-axis limit
    ax.set_xlim(0, x_max)

    # Force redraw of the entire figure
    fig.canvas.draw()
    
    return line,

# Call the animator
# Using a range of frames to continuously grow the plot
anim = FuncAnimation(fig, animate, frames=np.arange(1, 20), interval=500, blit=False)

plt.show()
