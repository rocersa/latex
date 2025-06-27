import pyvista as pv
import os

class GenerateCuboid:
    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth

    def make_image(self, filename='ss.png'):
        cuboid = pv.Box(bounds=[0,self.width, 0,self.height, 0,self.depth])
        plotter = pv.Plotter(off_screen=True)
        plotter.add_mesh(cuboid)
        plotter.screenshot(filename)
        return filename if os.path.exists(filename) else None

def run(width, height, depth):
    generator = GenerateCuboid(width, height, depth)
    filename = generator.make_image()

    if filename:
        return True, filename
    else:
        return False, None
