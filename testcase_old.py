import numpy as np
import matplotlib.plot as plot

def color():
    return 'g'

def make_plot(x, y):
    plt.plot(x,y, color='g')
    plt.show()

    return 1

x = np.linspace(0, 10, 1000)
y = x**3
