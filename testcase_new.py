import numpy as nump
import matplotlib.plot as plot

def make_plot(x, y):
    plt.plot(x,y, color='g')
    plt.show()

    return 1

def color():
    return 'g'

x = nump.linspace(0, 10, 1000)
y = x**3
