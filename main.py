import pyawr
import pyawr.mwoffice as mwo
import time
import math
import matplotlib.pyplot as plt
import scipy
import numpy as np
import os
import re

##path = "C:/Users/muhaa/Desktop/Research/Journal paper/data/"

path = "null"

awrde = mwo.CMWOffice()

if  not awrde.Project.EMStructures.Exists("EM Structure 2"):
    awrde.Project.EMStructures.Add("EM Structure 2")

em = awrde.Project.EMStructures("EM Structure 2")

#graph = awrde.Project.Graphs("Graph 1")
# lead_spacing='0.005mm' lead_w='0.00827896825396821mm' Length='0.5mm' LTO_t='0.001mm' metal_t='0.00127262626262626mm' trace_w='0.005mm' Width='0.5mm' xoffset='0.345253267973856mm' [Curve72]"
#peak: 115
#trough: 100
## units in microns ##
wafer_t = 10
SiO2_t = 10

Width = 250
Length = 500
lead_spacing = 16  #round to even number to keep ports on grid
lead_l = 20
trace_w = 5

period = 5
delay = 50
peak = 115
trough = 0

enc_l = 550
enc_w = 400

##enc_l = 550
#enc_w = 1000
em.Enclosure.XDimension = enc_l*1e-6
em.Enclosure.YDimension = enc_w*1e-6

metal_t = 1
LTO_t = 10

DUT_w = 10
DUT_y = 0
rotate_verticle = False
void_w = 14
void_x = 0
draw_void = True

#split ring resonnator#
num_cells = 0

try: 
    cell_size = enc_l/num_cells
except:
    pass
r1_d = 40   #ring1 diameter
r1_w = 3    #ring1 width
r1_g = 1    #ring1 gap
r2_d = 50   #ring2 diameter
r2_w = 3    #ring2 width
r2_g = 1    #ring2 gap

# em.MaterialLayers.Item(1).Thickness = 10/(10**6)     ##LTO_t thickness
# em.MaterialLayers.Item(2).Thickness = LTO_t/(10**6)     ##LTO_t thickness
# em.MaterialLayers.Item(3).Thickness = SiO2_t/(10**6)     ##LTO_t thickness
# em.MaterialLayers.Item(4).Thickness = 10/(10**6)     ##Si thickness

# copper = em.Materials.Item("Copper")

#print(em.Materials.Count)
#print(em.Materials.Exists("Copper"))            ##This is case sensitive
#copper = em.Materials.Item("Copper")


def draw_resonnator():
    x_base = 0
    y_base = 0
    for i in range(num_cells):
        for j in range(num_cells):
            ring_2 = em.Shapes.AddRectangle((x_base+(cell_size-r2_d)/2)*1e-6, (y_base+(cell_size-r2_d)/2)*1e-6,r2_d*1e-6,r2_d*1e-6,"Gatepad")
            em.SelectedObjects.AddFromArea(x_base*1e-6, (y_base+cell_size)*1e-6, (x_base+cell_size)*1e-6, y_base*1e-6)
            ring_2n = em.Shapes.AddRectangle((x_base+r2_w+(cell_size-r2_d)/2)*1e-6, (y_base+r2_w+(cell_size-r2_d)/2)*1e-6,(r2_d-r2_w*2)*1e-6,(r2_d-r2_w*2)*1e-6,"Gatepad")
            gap = em.Shapes.AddRectangle((x_base+(cell_size-r2_g)/2)*1e-6, (y_base+(cell_size-r2_d)/2)*1e-6,(r2_g)*1e-6,(r1_w)*1e-6, "Gatepad")
            em.SelectedObjects.AddFromArea(x_base*1e-6, (y_base+cell_size)*1e-6, (x_base+cell_size)*1e-6, y_base*1e-6)
            em.InvokeCommand("ShapeSubtract", 1, ring_2)
            em.SelectedObjects.RemoveAll()
            x_base+=cell_size
        x_base=0
        y_base+=cell_size

    x_base=0
    y_base=0
    for i in range(num_cells):
        for j in range(num_cells):
            ring_1 = em.Shapes.AddRectangle((x_base+(cell_size-r1_d)/2)*1e-6, (y_base+(cell_size-r1_d)/2)*1e-6,r1_d*1e-6,r1_d*1e-6,"Gatepad")
            em.SelectedObjects.AddFromArea((x_base+(cell_size-r1_d)/2)*1e-6, (y_base+(cell_size-r1_d)/2+r1_d)*1e-6, (x_base+(cell_size-r1_d)/2+r1_d)*1e-6, (y_base+(cell_size-r1_d)/2)*1e-6)
            ring_1n = em.Shapes.AddRectangle((x_base+r1_w+(cell_size-r1_d)/2)*1e-6, (y_base+r1_w+(cell_size-r1_d)/2)*1e-6,(r1_d-r1_w*2)*1e-6,(r1_d-r1_w*2)*1e-6,"Gatepad")
            while(1): break
            gap = em.Shapes.AddRectangle((x_base+(cell_size-r1_g)/2)*1e-6, (y_base+(cell_size+r1_d)/2-r1_w)*1e-6,(r1_g)*1e-6,(r1_w)*1e-6, "Gatepad")
            em.SelectedObjects.AddFromArea((x_base+(cell_size-r1_d)/2)*1e-6, (y_base+(cell_size+r1_d)/2)*1e-6, (x_base+(cell_size-r1_d)/2+r1_d)*1e-6, (y_base+(cell_size-r1_d)/2)*1e-6)
            print(em.SelectedObjects.Count)
            while(1): break
            em.InvokeCommand("ShapeSubtract", 1, ring_1)
            while(1): break
            em.SelectedObjects.RemoveAll()
            x_base+=cell_size

        x_base=0
        y_base+=cell_size
    
def draw_antenna():

    pathWrite = em.DrawingObjects.PathWriter
    pathWrite.LayerName = "Thick Metal"
    pathWrite.Width = trace_w*1e-6
    pathRec = pathWrite.CreatePathRecord()

    x = 0
    y = trace_w/2
    pathRec.AddSegment(x*1e-6,y*1e-6)
    y = lead_l
    pathRec.AddSegment(x*1e-6,y*1e-6)
    x = x-Length/2+lead_spacing/2
    pathRec.AddSegment(x*1e-6,y*1e-6)
    y = y+Width
    pathRec.AddSegment(x*1e-6,y*1e-6)
    x = x+delay
    pathRec.AddSegment(x*1e-6,y*1e-6)
    y_mid = y
    for i in range(period):
        y=y_mid
        if not(i%2):
            y += peak
        else:
            y-=trough
        pathRec.AddSegment(x*1e-6,y*1e-6)
        if i==period-2:
              pathRec.AddSegment(x*1e-6,y*1e-6)    
        x+=(Length-2*delay)/(period*2-1)
        pathRec.AddSegment(x*1e-6,y*1e-6)
    pathRec.AddSegment(x*1e-6,y*1e-6)
    pathRec.Offset(((enc_l-lead_spacing-trace_w)/2)*1e-6,0)
    path = pathWrite.AddPath(pathRec)  
    pathRec.Mirror((enc_l/2)*1e-6)
    path1 = pathWrite.AddPath(pathRec)
                                                                                         ##Port Number##
    em.Shapes.AddFace(((enc_l-lead_spacing)/2-trace_w)*1e-6,0,(enc_l-lead_spacing)/2*1e-6,0, int(1))
    port1 = em.Ports.Item(1)
   #  port1.ReferencePlaneDist = lead_l * 0.6e-6
    em.Shapes.AddFace(((enc_l+lead_spacing)/2)*1e-6,0, ((enc_l+lead_spacing)/2+trace_w)*1e-6,0, int(2))
    port2 = em.Ports.Item(2)
   # port2.ReferencePlaneDist = lead_l * 0.6e-6
    
def draw_interconnect():
    interconnect = em.DrawingObjects.AddRectangle(0, math.floor((enc_w-DUT_w)/2 + DUT_y)*1e-6, enc_l*1e-6, math.floor(DUT_w)*1e-6, "Gatepad")
    port3 = em.Shapes.AddFace(0, ((enc_w-DUT_w)/2 + DUT_y)*1e-6, 0, ((enc_w/2+DUT_w) + DUT_y)*1e-6, 3)
    port3 = em.Ports.Item(3)
    port4 = em.Shapes.AddFace(enc_l*1e-6, math.floor((enc_w-DUT_w)/2 + DUT_y)*1e-6, enc_l*1e-6, math.floor((enc_w/2+DUT_w) + DUT_y)*1e-6, 4)
    void = em.DrawingObjects.AddEllipse(((enc_l-void_w)/2+void_x)*1e-6, math.floor((enc_w - DUT_w - void_w)/2)*1e-6, void_w*1e-6, void_w*1e-6, "Gatepad")
    em.SelectedObjects.Add(interconnect)
    if(draw_void == True):
        em.SelectedObjects.Add(void)
        em.InvokeCommand("ShapeSubtract", 2, None)
 
def reset():
    #print("previous object count: ", em.DrawingObjects.Count)
    em.SelectedObjects.AddAll()
    for i in range(em.SelectedObjects.Count):
        try:
            em.SelectedObjects(1).Delete()
        except:
            print("object not deleted")
    #print("final object count: ", em.DrawingObjects.Count)
   
def output(graph, folder, title):
    graph = awrde.Project.Graphs(graph)
    #print(type(graph))
    graph.SimulateMeasurements()
    # graph_printed = graph.ExportTraceData("C:/Users/muhaa/Documents/AWR Projects/data/void_testing/{}".format(lead_l - 500))  ##for spacial resolution testing
    #print(path + folder + title + ".txt")
    graph_printed = graph.ExportTraceData(path + folder + title)
    print("graph printed", graph_printed)
    #print("graph printeda for lead_l {}: {}".format(lead_l, graph_printed))

def figure1():                             #figure 1: coupling vs void_width for each DUT_w
    global void_w   #every other scope sees changes made to void_w here
    global DUT_w
    for i in [5, 10, 15, 20, 25, 30]:              #interconnect width
        DUT_w = i                  
        # radius_range = np.linspace(0, i*2*.99, num=25, endpoint=True)              #void radius   
        radius_range = np.linspace(i*2*.80, i*2*.99, num=20, endpoint=True)              #void radius   
        #print(radius_range)
   
        for j in radius_range:      
            void_w = j                                        #void radius loop
            reset()
            draw_antenna()
            draw_interconnect()
            output("Differential Mode", "figure1/DM/", "DUTw{}_voidw{}".format(int(DUT_w*1000), int(void_w*1000)))
            output("Common Mode", "figure1/CM/", "DUTw{}_voidw{}".format(int(DUT_w*1000), int(void_w*1000)))


def plot_figure(directory, x_axis, y_axis, legend):
    CM_traces = plot_mode(directory + "/CM/", "Common Mode coupling with varying " + legend, x_axis, y_axis, legend)
    DM_traces = plot_mode(directory + "/DM/", "Differential Mode coupling with varying " + legend, x_axis, y_axis, legend)

    for DUTw in CM_traces["DUTw"]:
        void_widths =  CM_traces["DUTw"][DUTw]["voidw"]
        CM_data = CM_traces["DUTw"][DUTw]["|DM|"]
        DM_data = DM_traces["DUTw"][DUTw]["|DM|"]
        ratio = [CM_data[i]/DM_data[i] for i in range(len(CM_data))]
        plt.plot(void_widths, ratio, label=  DUTw)

    legend_ob = plt.legend()
    legend_ob.set_title(legend)
    plt.title("Ratio of CM to DM coupling with varying " + legend)
    plt.xlabel("void_width")
    plt.show()

def plot_mode(directory, title, x_axis, y_axis, legend):

    f1_path = path + directory
    file_list = os.listdir(f1_path)
    traces = {"DUTw": {}}
    for filename in file_list:
        numbers = re.findall(r'-?\d+', filename)               #list of group numbers
        DUTw = str(float(numbers[0])/1000)                                    #DUTw numeric value
        voidw = numbers[1]                                  #voidw numeric
        words = re.findall(r'[a-zA-Z]+', filename)        #list of grouped letters, DUTw, voidw
        if(str(DUTw) not in traces["DUTw"]):
            traces["DUTw"][str(DUTw)] = {"voidw": [], "|DM|": []}

        traces["DUTw"][str(DUTw)]["voidw"].append(float(voidw)/1000)
        with open(f1_path + filename, 'r') as file:
            graph_data = file.readlines()
            DM = graph_data[1].split('\t')[1]
            traces["DUTw"][str(DUTw)]["|DM|"].append(float(DM))
       

    for DUTw in traces["DUTw"]:
        void_widths, diff_mode = traces["DUTw"][DUTw]["voidw"], traces["DUTw"][DUTw]["|DM|"]        #sort entries
        void_widths, diff_mode = (list(t) for t in zip(*sorted(zip(void_widths, diff_mode))))
        traces["DUTw"][DUTw]["voidw"], traces["DUTw"][DUTw]["|DM|"] = void_widths, diff_mode        #reassign sorted entries
        # if(DUTw != "30.0"):
        #     continue
        plt.plot(void_widths, diff_mode, label=  DUTw)

    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.title(title)
    legend_ob = plt.legend()
    legend_ob.set_title(legend)
    plt.show()

    return(traces)

def figure2():          #LTO_t
    global void_w   #every other scope sees changes made to void_w here
    global LTO_t
    for i in range( 5, 55, 10):              #LTO range
        LTO_t = i
        em.MaterialLayers.Item(2).Thickness = LTO_t/(10**6)     ##LTO_t thickness
        radius_range = np.linspace(0, DUT_w*2*.95, num=10, endpoint=True)              #void radius   
        for j in radius_range:      
            void_w = j                                        #void radius loop
            reset()
            draw_antenna()
            draw_interconnect()
            output("Differential Mode", "figure2/DM/", "LTOt{}_voidw{}".format(int(LTO_t*1000), int(void_w*1000)))
            output("Common Mode", "figure2/CM/", "LTOt{}_voidw{}".format(int(LTO_t*1000), int(void_w*1000)))
    return


def figure3():          # void_x
    global void_w   #every other scope sees changes made to void_w here
    global void_x
    for i in range( 0, -240, -40):              #LTO range
        void_x = i
        radius_range = np.linspace(0, DUT_w*2*.95, num=10, endpoint=True)              #void radius   
        for j in radius_range:      
            void_w = j                                        #void radius loop
            reset()
            draw_antenna()
            draw_interconnect()
            output("Differential Mode", "figure3/DM/", "voidx{}_voidw{}".format(int(void_x*1000), int(void_w*1000)))
            output("Common Mode", "figure3/CM/", "voidx{}_voidw{}".format(int(void_x*1000), int(void_w*1000)))
    return


def figure4():          # DUT_y
    global void_w   
    global DUT_y
    offset_range = np.linspace(400, -400, num=20, endpoint=True)              #void radius   
    for j in offset_range:      
        DUT_y = j                                        #void radius loop
        reset()
        draw_antenna()
        draw_interconnect()
        output("Differential Mode", "figure4/DM/", "DUTw{}_DUTy{}".format(int(DUT_w*1000), int(DUT_y*1000)))
        output("Common Mode", "figure4/CM/", "DUTw{}_DUTy{}".format(int(DUT_w*1000), int(DUT_y*1000)))
    return

def figure5():      #figure 5: coupling vs void_width for each DUT_w
    global void_w   #every other scope sees changes made to void_w here
    global DUT_w 
    DUT_w = 40      #choose DUT_w here

    ## 4342289.08	4120521.31	3329233.993 ##
    anneal_times = [90]      #anneal times (seconds)

    for i in anneal_times:              #interconnect width             
        radius_range = np.linspace(0, DUT_w*2*.99, num=8, endpoint=True)              #void radius   

        for j in radius_range:      
            void_w = j                                        #void radius loop
            reset()
            draw_antenna()
            draw_interconnect()
            output("Differential Mode", "figure5/DM/", "anneal_time{}_voidw{}".format(int(i*1000), int(void_w*1000)))
            output("Common Mode", "figure5/CM/", "anneal_time{}_voidw{}".format(int(i*1000), int(void_w*1000)))
        plot_figure("figure5", "void width", "magnitude", "annealing time")
        input("change copper conductivity in AWR and then press enter")

def graph():
    i = 0
    x = []
    S13 = []
    for i in range(190, 710):
        try: 
            with open("C:/Users/muhaa/Documents/AWR Projects/data/x_resolution/{}".format(i), 'r') as f: 
                lines = f.readlines()
                labels = lines.pop(0)
                parameters = lines.pop(0)       #this line is only for smith charts, comment out if data comes from table
                for line in lines:
                    print(line)
                    meas = line.split("\t")
                    freq = meas[0]
                    real = float(meas[1].strip())
                    imag = float(meas[2].strip())
                    S13.append(math.sqrt(real**2 + imag**2))
                    x.append(i)
                    break
        except:
            pass
    plt.plot(x, S13)
    plt.show()
    max_pwr = max(S13)
    dB = []

   

    for i in S13:
        dB.append(10 * math.log10(i/max_pwr))


    interp = scipy.interpolate.CubicSpline(x, dB)

    cutoffs = interp.solve(-3.0)            #spatial resolution cutoff (dB)
    spatial_res = abs(cutoffs[0] - cutoffs[1])
    print(spatial_res)


    #plt.axhline(y = -3, color = 'r', linestyle = '-') #horizontal line at -3dB cutoff
    plt.axvline(x = cutoffs[0], color = 'b', linestyle = '-')
    plt.axvline(x = cutoffs[1], color = 'b', linestyle = '-')
    plt.ylabel("S(1,2) Coupling (dB)")
    plt.xlabel("x-offset (um)")
    plt.title("Coupling between DUT and antenna vs x-offset")
   
     
    plt.plot(x, dB)
    plt.show()

def space_res():
    global lead_l       #every other scope sees changes made to lead_l here
    for i in range(200, 300, 10):
        lead_l = i
        reset()
        draw_antenna()
        draw_interconnect()
        output()    #simulates and outputs
        print("simulation done for lead_l:  {}".format(lead_l))

def void_testing():
    global void_w   #every other scope sees changes made to void_w here
    for i in range(10, 22):
        void_w = i
        reset()
        draw_antenna()
        draw_interconnect()
        output()    #simulates and outputs
        print("simulation done for void_w:  {}".format(void_w))
        
def main():
    #reset()
    ##draw_antenna()
    #draw_interconnect()
    # figure1()
    # figure4()
    # figure3()
    # figure1()
    #figure5()

    plot_figure("figure1", "trace width", "magnitude", "interconnect width")
    plot_figure("figure2", "trace width", "magnitude", "SiO2 thickness")
    plot_figure("figure3", "trace width", "magnitude", "void x position ")
    plot_figure("figure4", "trace x-offset", "magnitude", "DUTw")
    plot_figure("figure5", "void width", "magnitude", "annealing time")
    
    # #void_testing()
    #graph()
  
main()
#base lead_l position in y direction: 500


# for i in range(shape_count):
#     print(em.Shapes(i+1).Type)
    
#em.DrawingObjects.RemoveAll()
#em.Drawing.Objects.RemoveAll
# for i in range(em.DrawingObjects.Count):
#     print(i)
#     em.DrawingObjects(i+1).Delete()

#em.SelectedObjects.RemoveAll()

#em.DrawingObjects.Item(1).Delete()
#path1 = em.Shapes.AddPath([(1e-6,0),(100e-6,0)])


# print("num material layers: ", em.MaterialLayers.Count) #Print Dielectric
# for i in range(em.MaterialLayers.Count):
#     print(em.MaterialLayers[i].Name)

# for i in range(em.Shapes.Count):  #Print each shape's drawing layer
#     print(em.Shapes[i].DrawingLayer.Name)
