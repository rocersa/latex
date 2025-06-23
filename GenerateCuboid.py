import pyvista as pv

class GenerateCuboid():

    def __init__(self, width, height, depth):
        cuboid = pv.Box(bounds=[0,width, 0,height, 0,depth])
        plotter = pv.Plotter(off_screen=True)
        plotter.add_mesh(cuboid)
        plotter.screenshot('ss.png')


def run(width, height, depth):
    GenerateCuboid(width, height, depth)

