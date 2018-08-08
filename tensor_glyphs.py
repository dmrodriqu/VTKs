'''
Dylan M. Rodriquez
Implementation of Superquadric glyphs in VTK.

takes 8 command line arguments and returns a rendering.

DWI/DTI file required for rendering.

usage:

    python tensor_glyphs.py  some_file.vtk -phires (int) -thetares (int) --phi (float) --theta (float)
        --x (int) --y (int)

8/8/18
number of points to be samples is currently at 10,000. cmd line variable to later be introduced.
higher limits are limited by RAM/GPU

'''


import sys
import vtk


# Class for superquadric source. Uses vtktensorglyph
class superquadrics:
    def __init__(self, thetaresolution, phiresolution, thetaroundness, phiroundness):
        self.tres = thetaresolution
        self.phires = phiresolution
        self.tround = thetaroundness
        self.phiround= phiroundness
        self.probe = vtk.vtkProbeFilter()
        self.datacutmapper = vtk.vtkPolyDataMapper()
        self.dataCutActor = vtk.vtkActor()
        self.tensorEllipsoids = vtk.vtkTensorGlyph()
        self.superquad = vtk.vtkSuperquadricSource()
    def createsuperquadrics(self, inputdata):
        mask = vtk.vtkMaskPoints()
        mask.SetInputConnection(inputdata)
        mask.RandomModeOn()
        mask.SetRandomModeType(2)
        mask.SetMaximumNumberOfPoints(10000)
        self.superquad.SetThetaResolution(self.tres)
        self.superquad.SetPhiResolution(self.phires)
        self.superquad.SetPhiRoundness(self.phiround)
        self.superquad.SetThetaRoundness(self.tround)
        self.superquad.ToroidalOff()
        self.tensorEllipsoids.SetInputConnection(mask.GetOutputPort())
        self.tensorEllipsoids.SetSourceConnection(self.superquad.GetOutputPort())
        self.tensorEllipsoids.ExtractEigenvaluesOn()
        self.tensorEllipsoids.ClampScalingOn()
        self.tensorEllipsoids.SetMaxScaleFactor(2)
        self.tensorEllipsoids.SetColorModeToEigenvalues()
        self.datacutmapper.SetInputConnection(self.tensorEllipsoids.GetOutputPort())
        return self.dataCutActor.SetMapper(self.datacutmapper)

def cutplane(inpt, origin, normal):
    plane = vtk.vtkPlane()
    plane.SetOrigin(origin)
    plane.SetNormal(normal)
    cut = vtk.vtkCutter()
    cut.SetInputConnection(inpt)
    cut.SetCutFunction(plane)
    cut.GenerateCutScalarsOff()
    cut.SetSortByToSortByCell()
    return cut

# create a window of a defined width (x) and y (height)
class Window:
    def __init__(self, x, y):
        self.height = y
        self.width  = x
        self.cam = vtk.vtkInteractorStyleTrackballCamera()
        self.renderer = vtk.vtkRenderer()
        self.renderWindow = vtk.vtkRenderWindow()
        self.interact = vtk.vtkRenderWindowInteractor()

    # initialize window
    def createWindow(self):
        self.renderWindow.AddRenderer(self.renderer)
        self.interact.SetRenderWindow(self.renderWindow)
        self.interact.SetInteractorStyle(self.cam)
    # add any actors from a list of actors
    def _addactors(self,actorlist):
        for i in actorlist:
            self.renderer.AddActor(i)
    # start rendering window
    def startWindow(self, actorlist):
        self._addactors(actorlist)
        self.interact.Initialize()
        self.renderWindow.SetSize(self.width,self.height)
        cam = self.renderer.GetActiveCamera()
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.renderWindow.Render()
        self.interact.Start()

# print help text if needed
def helptext():
    print("="*30)
    print("\n options:\n")
    print("\n --phires: phi resolution\n")
    print("\n --thetares: theta resolution \n")
    print("\n --phi: phi roundness\n")
    print("\n --theta: theta roundness")
    print("\n --p: points to collect")
    print("\n --x: window width")
    print("\n --y: window height")
    print("\n")
    print("="*30)


# function for command line interpretation
def cmdLineInterpret():
    # if any arguments are "help," print help text
    for i in sys.argv:
        if i ==  "--help":
            helptext()
            return
    # default values to be changed from cmdline args
    phires = 4
    thetares = 4
    phi = 1
    theta = 0.5
    points = 10000
    x = 640
    y = 480
    i = 0
    # parse cmdline args
    while i < len(sys.argv):
        ix = sys.argv[i]
        if ix == "--phires":
            phires = int(sys.argv[i+1])
        elif ix == "--thetares":
            thetares = int(sys.argv[i+1])
        elif ix == "--phi":
            phi = float(sys.argv[i+1])
        elif ix == "--theta":
            theta = float(sys.argv[i+1])
        elif ix == "--p":
            points = int(sys.argv[i+1])
        elif ix == "--x":
            x = int(sys.argv[i+1])
        elif ix == "--y":
            y = int(sys.argv[i+1])
        i+=1
    # file will always be at index 1
    data = sys.argv[1]
    reader = vtk.vtkStructuredPointsReader()
    reader.SetFileName(data)
    return reader, phires, thetares, phi, theta, points, x, y

def main():
    # if error, throw help
    try:
        reader, phires, thetares, phi, theta, points, x, y = cmdLineInterpret()
    except:
        helptext()
        return
    # list of actors
    alist = []
    squad = superquadrics(thetares, phires, theta, phi)
    squad.createsuperquadrics(cutplane(reader.GetOutputPort(), (0,0,0), (0,1,0)).GetOutputPort())
    # appnd list of actors
    alist.append(squad.dataCutActor)
    window = Window(x,y)
    window.createWindow()
    # render
    window.startWindow(alist)

main()
