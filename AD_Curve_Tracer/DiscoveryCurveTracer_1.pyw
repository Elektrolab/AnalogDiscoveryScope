# DiscoveryCurveTracer_1.py(w)  (12-3-2013)
# For Python version 2.6 or 2.7
# For DWF Library 2.7.0 (For Analog Discovery)
# Created by D Mercer
from ctypes import *
import math
import time
import tkFont
from Tkinter import *
from tkFileDialog import askopenfilename
from tkSimpleDialog import askstring
from tkMessageBox import *

# define DWF DLL library
if sys.platform.startswith("win"):
    dwf = cdll.dwf    # for Windows
else:
    dwf = cdll.LoadLibrary("libdwf.so")   # For Linux
#
funcCustom   = c_byte(30)
funcTriangle = c_byte(3)
rgdSamples = (c_double*4096)()
channel1 = c_int(0)
channel2 = c_int(1)
# read data record from file
datafile = open("5_setps_1.csv")
i = 0
for line in datafile:
    rgdSamples[i] = eval(line.rstrip() )
    i = i + 1
datafile.close()
numsamples = i - 1
#
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
# query for Number of Devices
cdevices = c_int()
dwf.FDwfEnum(c_int(0), byref(cdevices))
# Opening first device
hdev = c_int()
dwf.FDwfDeviceOpen(c_int(0), byref(hdev))
# Values that can be modified
GRW = 680                   # Width of the grid
GRH = 400                   # Height of the grid was 500
X0L = 35                    # Left top X value of grid
Y0T = 25                    # Left top Y value of grid

SAMPLErate = 40000        # initial Sample rate of the Scope channels
UPDATEspeed = 0.1           # Update speed, default 0.1, for slower PC's a higher value is perhaps required
TRIGGERlevel = 0.0          # Triggerlevel in volts
# channel 1 configuration - positive ramp
dwf.FDwfAnalogOutNodeEnableSet(hdev, channel1, c_int(0), c_bool(True))
dwf.FDwfAnalogOutNodeFunctionSet(hdev, channel1, c_int(0), funcTriangle)
dwf.FDwfAnalogOutNodePhaseSet(hdev, channel1, c_int(0), c_double(270.0))
dwf.FDwfAnalogOutNodeFrequencySet(hdev, channel1, c_int(0), c_double(100.0)) 
dwf.FDwfAnalogOutNodeAmplitudeSet(hdev, channel1, c_int(0), c_double(2))
# channel 2 configuration - five level step
dwf.FDwfAnalogOutNodeEnableSet(hdev, channel2, c_int(0), c_bool(True))
dwf.FDwfAnalogOutNodeFunctionSet(hdev, channel2, c_int(0), funcCustom)
dwf.FDwfAnalogOutNodePhaseSet(hdev, channel1, c_int(0), c_double(0.0))
dwf.FDwfAnalogOutNodeDataSet(hdev, channel2, c_int(0), rgdSamples, c_int(4096))
dwf.FDwfAnalogOutNodeFrequencySet(hdev, channel2, c_int(0), c_double(20.0)) 
dwf.FDwfAnalogOutNodeAmplitudeSet(hdev, channel2, c_int(0), c_double(2))
# Configure analog in
dwf.FDwfAnalogInFrequencySet(hdev, c_double(SAMPLErate))
dwf.FDwfAnalogInChannelFilterSet(hdev, c_int(-1), c_int(1))
# Set range for all channels to highest range
dwf.FDwfAnalogInChannelRangeSet(hdev, c_int(-1), c_double(50))
# Set sample buffer size
dwf.FDwfAnalogInBufferSizeSet(hdev, c_int(4000))
# set initial trigger conditions
# TRIGTYPE trigtypeEdge = 0
dwf.FDwfAnalogInTriggerTypeSet(hdev, c_int(0))
dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdev, c_double(1.0))
dwf.FDwfAnalogInTriggerHysteresisSet(hdev, c_double(0.01))
dwf.FDwfAnalogInTriggerLevelSet(hdev, c_double(TRIGGERlevel))
dwf.FDwfAnalogInTriggerFilterSet(hdev, c_int(1))
dwf.FDwfAnalogInTriggerHoldOffSet(hdev, c_double(0.0))
dwf.FDwfAnalogInTriggerPositionSet(hdev, c_double(0.0))
dwf.FDwfAnalogInTriggerLengthConditionSet(hdev, c_int(0))
# Vertical Sensitivity list in v/div
CHvpdiv = (0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)
# Time list in ms/div
TMpdiv = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0)

DC1 = DC2 = Min1 = Max1 = Min2 = Max2 = 0

# Colors that can be modified
COLORframes = "#000080"     # Color = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
COLORcanvas = "#000000"
COLORgrid = "#808080"
COLORzeroline = "#0000ff"
COLORtrace1 = "#00ff00"
COLORtrace2 = "#ff8000"
COLORtext = "#ffffff"
COLORtrigger = "#ff0000"

# Button sizes that can be modified
Buttonwidth1 = 10
Buttonwidth2 = 6
Buttonwidth3 = 7
# Initialisation of general variables

ProbeList = (0.1, 1.0, 10, 100)
CH1probe = 1.0              # Probe attenuation factor 1x, 10x or 0.1x channel 1
CH2probe = 1.0              # Probe attenuation factor 1x, 10x or 0.1x channel 2
CH1Offset = 0.0
CH2Offset = 0.0

# Other global variables required in various routines
CANVASwidth = GRW + 2 * X0L # The canvas width
CANVASheight = GRH + 80     # The canvas height

Ymin = Y0T                  # Minimum position of screen grid (top)
Ymax = Y0T + GRH            # Maximum position of screen grid (bottom)

LONGsweep = False           # True if sweeps longer than 1 second
LONGchunk = LONGsweep       # True if chunk for longsweep is used for the trace

ADsignal1 = []              # AD signal array channel 1    
ADsignal2 = []              # AD signal array channel 2

T1line = []                 # Trace line channel 1
T2line = []                 # Trace line channel 2
Triggerline = []            # Triggerline

SHOWsamples = GRW           # Number of samples on the screen   

TriggerPos = 0.0            # Starting trigger possition of the trace
TRACES = 2                  # Number of traces 1 or 2
TRACESread = 0              # Number of traces that have been read from Discovery
XYMode = 0                  # XY Mode flag
RUNstatus = 0               # 0 stopped, 1 start, 2 running, 3 stop and restart, 4 stop
ADstatus = 0                # 0 Analog Discovery off, 1 = on

TRIGGERsample = 0           # AD sample trigger point

# =========== Start widgets routines =============================
def BTriggerEdge():
    global hdev
    global TgEdge
                                       
# TRIGCOND trigcondRisingPositive = 0
# TRIGCOND trigcondFallingNegative = 1

    dwf.FDwfAnalogInTriggerConditionSet(hdev, c_int(TgEdge.get()))

def BTriggerCH():
    global hdev
    global TgChan

    dwf.FDwfAnalogInTriggerChannelSet(hdev, c_int(TgChan.get()))

def BTrigger50p():
    global hdev
    global TgChan
    global TRIGGERlevel
    global TRIGGERentry
    global DC1, DC2

    if (TgChan.get() == 0 ):
        DCString = ' {0:.2f} '.format(DC1)
    else:
        DCString = ' {0:.2f} '.format(DC2)

    TRIGGERlevel = eval(DCString)
    TRIGGERentry.delete(0,END)
    TRIGGERentry.insert(4, DCString)
    # set new trigger level
    dwf.FDwfAnalogInTriggerLevelSet(hdev, c_double(TRIGGERlevel))
    UpdateTrace()           # Always Update
    
def BTriggerMode():
    global hdev
    global TgMode

    if (TgMode.get() == 0):
        # no trigger
        dwf.FDwfAnalogInTriggerSourceSet(hdev, c_int(0)) 
    elif (TgMode.get() == 1):
        # trigger source set to detector of analog in channels
        dwf.FDwfAnalogInTriggerSourceSet(hdev, c_int(2)) 
        # auto trigger timeout value
        dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdev, c_double(2.0))
    elif (TgMode.get() == 2):
        # trigger source set to detector of analog in channels
        dwf.FDwfAnalogInTriggerSourceSet(hdev, c_int(2)) 
        # 0 disables auto trigger
        dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdev, c_double(0))
    
def BTriglevel(event):
    global TRIGGERlevel
    global TRIGGERentry
    global hdev

    # evalute entry string to a numerical value
    TRIGGERlevel = eval(TRIGGERentry.get())
    # set new trigger level
    dwf.FDwfAnalogInTriggerLevelSet(hdev, c_double(TRIGGERlevel))
    UpdateTrace()           # Always Update

def Bcloseexit():
    global ADstatus
    global RUNstatus
    
    if (ADstatus == 0):
        ADstatus = 1
    else:
        ADstatus = 0

    RUNstatus = 0
    dwf.FDwfDeviceCloseAll()   # close Analog Discovery and exit
    root.destroy()
    exit()

def BStart():
    global RUNstatus
    global hdev
    
    if (RUNstatus == 0):
        RUNstatus = 1
    BRc(0)
    BDevTyp()
    BAWG1Ampl(0)
    BAWG1Offset(0)
    BAWG2Ampl(0)
    # syncronous start analog output
    # make channel 1 master
    dwf.FDwfAnalogOutMasterSet(hdev, c_int(-1), c_int(0))
    # start channel 2, this will only configure the channel
    dwf.FDwfAnalogOutConfigure(hdev, c_int(1), c_bool(True))
    # start channel 1, this will start the slave channels too
    dwf.FDwfAnalogOutConfigure(hdev, c_int(0), c_bool(True))
    UpdateScreen()          # Always Update

def BStop():
    global RUNstatus
    global hdev
    
    if (RUNstatus == 1):
        RUNstatus = 0
    elif (RUNstatus == 2):
        RUNstatus = 3
    elif (RUNstatus == 3):
        RUNstatus = 3
    elif (RUNstatus == 4):
        RUNstatus = 3
# stop analog outputs
    dwf.FDwfAnalogOutConfigure(hdev, c_int(-1), c_bool(False))
    UpdateScreen()          # Always Update

def BTime():
    global TIMEdiv
    global TMsb
    global SAMPLErate
    global RUNstatus
    global hdev

    if RUNstatus == 2:      # Restart if running
        RUNstatus = 4

    TIMEdiv = eval(TMsb.get())
        # change sampele rate based on time scale
    SAMPLErate = 2000 / (0.01 * TIMEdiv)
    if (SAMPLErate > 100000000 ):
        SAMPLErate = 100000000
    dwf.FDwfAnalogInFrequencySet(hdev, c_double(SAMPLErate))
    UpdateTrace()           # Always Update

def BCH1level():
    global CH1sb
    global hdev
    
    CHpdvLevel = eval(CH1sb.get())
    if ( CHpdvLevel >= 1.0 ):
        dwf.FDwfAnalogInChannelRangeSet(hdev, c_int(0), c_double(50))
    else:
        dwf.FDwfAnalogInChannelRangeSet(hdev, c_int(0), c_double(4))
        
    UpdateTrace()           # Always Update

def BCH2level():
    global CH2sb
    global hdev
    
    CHpdvLevel = eval(CH2sb.get())
    if ( CHpdvLevel >= 1.0 ):
        dwf.FDwfAnalogInChannelRangeSet(hdev, c_int(1), c_double(50))
    else:
        dwf.FDwfAnalogInChannelRangeSet(hdev, c_int(1), c_double(4))
        
    UpdateTrace()           # Always Update    

def BOffset1(event):
    global CH1Offset
    global CH1OffsetEntry
    global hdev

    # evalute entry string to a numerical value
    CH1Offset = eval(CH1OffsetEntry.get())
    # set new offset level
    dwf.FDwfAnalogInChannelOffsetSet(hdev, c_int(0), c_double(CH1Offset))
    UpdateTrace()           # Always Update

def BOffset2(event):
    global CH2Offset
    global CH2OffsetEntry
    global hdev

    # evalute entry string to a numerical value
    CH2Offset = eval(CH2OffsetEntry.get())
    # set new offset level
    dwf.FDwfAnalogInChannelOffsetSet(hdev, c_int(1), c_double(CH2Offset))
    UpdateTrace()           # Always Update

def BXYMode():
    global XYMode

    if XYMode == 0:
        XYMode = 1
    else:
        XYMode = 0
    UpdateTrace()           # Always Update


def BSupplyOnOff():
    global hdev
    global PfiveV
    global NfiveV
    
    dwf.FDwfAnalogIOEnableSet(hdev, c_int(0))
    time.sleep(0.1)
    if PfiveV.get() > 0: # enable positive supply
        dwf.FDwfAnalogIOChannelNodeSet(hdev, c_int(0), c_int(0), c_double(1))
    else: # disable positive supply
        dwf.FDwfAnalogIOChannelNodeSet(hdev, c_int(0), c_int(0), c_double(0))

    if NfiveV.get() > 0: # enable negative supply
        dwf.FDwfAnalogIOChannelNodeSet(hdev, c_int(1), c_int(0), c_double(1))
    else: # disable negative supply
        dwf.FDwfAnalogIOChannelNodeSet(hdev, c_int(1), c_int(0), c_double(0))
# master supply enable
    dwf.FDwfAnalogIOEnableSet(hdev, c_int(1))    
# Awg functions
def BRc(temp):
    global hdev
    global RcEntry
    global Rcvalue

    Rcvalue = float(eval(RcEntry.get()))

def BRb(temp):
    global hdev
    global RbEntry
    global Rbvalue

    Rbvalue = float(eval(RbEntry.get()))

def BDevTyp():
    global hdev
    global DevTyp

    if (DevTyp.get() == 0):
        # NPN
        dwf.FDwfAnalogOutNodePhaseSet(hdev, c_int(0), c_int(0), c_double(270.0))
    elif (DevTyp.get() == 1):
        # PNP
        dwf.FDwfAnalogOutNodePhaseSet(hdev, c_int(0), c_int(0), c_double(90.0))
    
def BAWG1Ampl(temp):
    global hdev
    global AWG1AmplEntry
    global AWG1Amplvalue

    AWG1Amplvalue = float(eval(AWG1AmplEntry.get()))
    dwf.FDwfAnalogOutNodeAmplitudeSet(hdev, c_int(0), c_int(0), c_double(AWG1Amplvalue))
    
def BAWG1Offset(temp):
    global hdev
    global AWG1OffsetEntry
    global AWG1Offsetvalue

    AWG1Offsetvalue = float(eval(AWG1OffsetEntry.get()))
    dwf.FDwfAnalogOutNodeOffsetSet(hdev, c_int(0), c_int(0), c_double(AWG1Offsetvalue))
    
def BAWG2Ampl(temp):
    global hdev
    global RUNstatus
    global AWG2AmplEntry
    global AWG2Amplvalue
    global AWG2OffsetEntry
    global AWG2Offsetvalue
    global RbEntry
    global Rbvalue
    global Ibvalue

    Ibvalue = eval(AWG2AmplEntry.get())
    if Ibvalue == 0:
        Ibvalue = 0.0001
    Rbvalue = eval(RbEntry.get())
    Vbevalue = eval(AWG2OffsetEntry.get())
    AWG2Amplvalue = 2.0 * Rbvalue * Ibvalue
    AWG2Offsetvalue = AWG2Amplvalue + Vbevalue
    dwf.FDwfAnalogOutNodeAmplitudeSet(hdev, c_int(1), c_int(0), c_double(AWG2Amplvalue))
    dwf.FDwfAnalogOutNodeOffsetSet(hdev, c_int(1), c_int(0), c_double(AWG2Offsetvalue))
    if (RUNstatus == 1):
        # syncronous start analog output
        # make channel 1 master
        dwf.FDwfAnalogOutMasterSet(hdev, c_int(-1), c_int(0))
        # start channel 2, this will only configure the channel
        dwf.FDwfAnalogOutConfigure(hdev, c_int(1), c_bool(True))
        # start channel 1, this will start the slave channels too
        dwf.FDwfAnalogOutConfigure(hdev, c_int(0), c_bool(True))
        
def BAWG2Offset(temp):
    global hdev
    global AWG2OffsetEntry
    global AWG2Offsetvalue

    AWG2Offsetvalue = eval(AWG2OffsetEntry.get())
    dwf.FDwfAnalogOutNodeOffsetSet(hdev, c_int(1), c_int(0), c_double(AWG2Offsetvalue))
    
# ========================= Main routine ====================================
    
def Analog_In():   # Read the analog data and store the data into the arrays
    global ADsignal1
    global ADsignal2
    global TRACES
    global TRACESread
    global RUNstatus
    global ADstatus
    global TIMEdiv1x
    global TIMEdiv
    global SAMPLErate
    global LONGsweep
    global LONGchunk
    global UPDATEspeed
    global TRACErefresh
    global SCREENrefresh
    global DCrefresh
    global hdev
    global DC1, DC2, Min1, Max1, Min2, Max2
 
    while (True):                       # Main loop
        # RUNstatus = 1 : Open Acquisition
        # RUNstatus = 2
        if (RUNstatus == 1) or (RUNstatus == 2):
        # Starting acquisition
            # set 2nd argument to 0
            # having it set to true (1), the trigger detector is reconfigured so auto timer would be restarted after each acquisition and auto acquisitions would be slow, at timeout intervals
            dwf.FDwfAnalogInConfigure(hdev, c_int(0), c_int(1))

            # waiting to finish
            sts = c_int()
            while True:
                dwf.FDwfAnalogInStatus(hdev, c_int(1), byref(sts))
                if sts.value == 2 :
                    break
                time.sleep(0.1)
            # done
            # read 4000 data samples
            ADsignal1 = (c_double*4000)()
            ADsignal2 = (c_double*4000)()
            dwf.FDwfAnalogInStatusData(hdev, c_int(0), ADsignal1 , len(ADsignal1))
            dwf.FDwfAnalogInStatusData(hdev, c_int(1), ADsignal2 , len(ADsignal2))     
# 
            DC1 = sum(ADsignal1)/len(ADsignal1) # DC value = average of the data record
            DC2 = sum(ADsignal2)/len(ADsignal2)
            Min1 = min(ADsignal1)
            Max1 = max(ADsignal1)
            Min2 = min(ADsignal2)
            Max2 = max(ADsignal2)
            TRACESread = 2
            UpdateAll()         # Update Data, trace and screen

        # RUNstatus = 3: Stop
        # RUNstatus = 4: Stop and restart
        if (RUNstatus == 3) or (RUNstatus == 4):
            if RUNstatus == 3:
                RUNstatus = 0                               # Status is stopped 
            if RUNstatus == 4:          
                RUNstatus = 1                               # Status is (re)start

            UpdateScreen()     
        # Update tasks and screens by TKinter 
        root.update_idletasks()
        root.update()                   # update screens


def UpdateAll():        # Update Data, trace and screen
    MakeTrace()         # Update the traces
    UpdateScreen()      # Update the screen 

def UpdateTrace():      # Update trace and screen
    MakeTrace()         # Update traces
    UpdateScreen()      # Update the screen

def UpdateScreen():     # Update screen with trace and text
    MakeScreen()        # Update the screen
    root.update()       # Activate updated screens    

def MakeTrace():    # Make the traces
    global ADsignal1
    global ADsignal2
    global T1line
    global T2line
    global Triggerline
    global TgChan
    global X0L
    global Y0T
    global GRW
    global GRH
    global Ymin
    global Ymax
    global SHOWsamples
    global TriggerPos
    global TRACES
    global TRACESread
    global RUNstatus
    global ADstatus
    global XYMode
    global CH1probe
    global CH2probe
    global CH1sb
    global CH2sb
    global CH1Offset
    global CH2Offset
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TIMEdiv      # current spin box value
    global SAMPLErate
    global TRIGGERsample
    global TRIGGERlevel
    global DC1, DC2
 
    # Set the TRACEsize variable
    TRACEsize = len(ADsignal1)               # Set the trace length
    # get time scale
    TIMEdiv = eval(TMsb.get())
    # prevent divide by zero error
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.1
    # get the vertical ranges
    CH1pdvRange = eval(CH1sb.get())
    CH2pdvRange = eval(CH2sb.get())
    # prevent divide by zero error
    if CH1pdvRange < 0.01:
        CH1pdvRange = 0.01
    if CH2pdvRange < 0.01:
        CH2pdvRange = 0.01
        
    # Continue with finding the trigger sample and drawing the traces 
    if TRACEsize == 0:                          # If no trace, skip rest of this routine
        T1line = []                             # Trace line channel 1
        T2line = []                             # Trace line channel 2
        return() 

    # Find trigger sample 
    TRIGGERsample = 0
        
    # set and/or corrected for in range
    SCmin = int(-1 * TRIGGERsample)
    SCmax = int(TRACEsize - TRIGGERsample - 20)
    
    # Make Trace lines etc.

    Yconv1 = float(GRH/10) / CH1pdvRange    # Conversion factors from samples to screen points
    Yconv2 = float(GRH/10) / CH2pdvRange    

    c1 = GRH / 2 + Y0T    # fixed correction channel 1
    c2 = GRH / 2 + Y0T    # fixed correction channel 2

    SHOWsamples = SAMPLErate * 10 * TIMEdiv / 1000 

    T1line = []                     # Trace line channel 1
    T2line = []                     # Trace line channel 2
    t = TRIGGERsample     # t = Start sample in trace
    x = 0                           # Horizontal screen pixel

    if XYMode == 0:
        if (SHOWsamples <= GRW):
            Xstep = GRW / SHOWsamples
            Tstep = 1
            x1 = 0                      # x position of trace line
            y1 = 0.0                    # y position of trace 1 line
   
            while (x <= GRW):
                if (t < TRACEsize):
                    x1 = x + X0L
                    y1 = int(c1 - Yconv1 * (float(ADsignal1[int(t)]) - CH1Offset))

                    if (y1 < Ymin):
                        y1 = Ymin
                    if (y1 > Ymax):
                        y1 = Ymax
                    T1line.append(int(x1))
                    T1line.append(int(y1))        

                    if (TRACESread == 2 and TRACES == 2):
                        y1 = int(c2 - Yconv2 * float(ADsignal2[int(t)]) - CH2Offset)

                        if (y1 < Ymin):
                            y1 = Ymin
                        if (y1 > Ymax):
                            y1 = Ymax
                        T2line.append(int(x1))
                        T2line.append(int(y1))        

                t = t + Tstep
                x = x + Xstep

        if (SHOWsamples > GRW):
            Xstep = 1
            Tstep = SHOWsamples / GRW
            x1 = 0                          # x position of trace line
            ylo = 0.0                       # ymin position of trace 1 line
            yhi = 0.0                       # ymax position of trace 1 line
            t = 2000 - (SHOWsamples / 2)    # set time zero at center of screen
            x = 0                           # Horizontal screen pixel
    
            while (x <= GRW):
                if (t < TRACEsize):
                    x1 = x + X0L
                    ylo = float(ADsignal1[int(t)] - CH1Offset)
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TRACEsize:
                        v = float(ADsignal1[int(n)] - CH1Offset)
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v

                        n = n + 1   
                
                    ylo = int(c1 - Yconv1 * ylo)
                    yhi = int(c1 - Yconv1 * yhi)
                    if (ylo < Ymin):
                        ylo = Ymin
                    if (ylo > Ymax):
                        ylo = Ymax

                    if (yhi < Ymin):
                        yhi = Ymin
                    if (yhi > Ymax):
                        yhi = Ymax
                    T1line.append(int(x1))
                    T1line.append(int(ylo))        
                    T1line.append(int(x1))
                    T1line.append(int(yhi))        

                    if (TRACESread == 2 and TRACES == 2):
                        ylo = float(ADsignal2[int(t)] - CH2Offset)
                        yhi = ylo
                        n = t
                        while n < (t + Tstep) and n < TRACEsize:
                            v = float(ADsignal2[int(n)] - CH2Offset)
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v

                            n = n + 1   
                
                        ylo = int(c2 - Yconv2 * ylo)
                        yhi = int(c2 - Yconv2 * yhi)
                        if (ylo < Ymin):
                            ylo = Ymin
                        if (ylo > Ymax):
                            ylo = Ymax

                        if (yhi < Ymin):
                            yhi = Ymin
                        if (yhi > Ymax):
                            yhi = Ymax
                        T2line.append(int(x1))
                        T2line.append(int(ylo))        
                        T2line.append(int(x1))
                        T2line.append(int(yhi))
                    
                t = t + Tstep
                x = x + Xstep
    else:                           # draw X/Y plot 
        t = 0
        c2 = GRW / 2 + X0L   # Hor correction factor
        Yconv1 = float(GRH/10) / CH2pdvRange
        Yconv2 = float(GRW/10) / CH1pdvRange
        while (t < TRACEsize):
            ylo = float(ADsignal2[int(t)] - CH2Offset)
            xlo = float(ADsignal1[int(t)] - CH1Offset)
            ylo = int(c1 - Yconv1 * ylo)
            xlo = int(c2 + Yconv2 * xlo)
            T1line.append(int(xlo))
            T1line.append(int(ylo))
            t = t + 1
            
    # Make trigger line
    Triggerline = []                # Triggerline
    if ( TgChan.get() == 0 ):
        x1 = X0L
        y1 = int(c1 - Yconv1 * (float(TRIGGERlevel) - CH1Offset))
    else:
        x1 = X0L+GRW
        y1 = int(c2 - Yconv2 * (float(TRIGGERlevel) - CH2Offset))
        
    if (y1 < Ymin):
        y1 = Ymin
    if (y1 > Ymax):
        y1 = Ymax
    Triggerline.append(int(x1-5))
    Triggerline.append(int(y1))        
    Triggerline.append(int(x1+5))
    Triggerline.append(int(y1))        

def MakeScreen():     # Update the screen with traces and text
    global ADsignal1
    global ADsignal2
    global T1line
    global T2line
    global Triggerline
    global X0L          # Left top X value
    global Y0T          # Left top Y value
    global GRW          # Screenwidth
    global GRH          # Screenheight
    global Ymin
    global Ymax
    global SHOWsamples  # Number of samples on the screen
    global TriggerPos
    global TRACES
    global TRACESread   # Number of traces 1 or 2
    global RUNstatus    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global ADstatus     # 0 audio off, 1 audio on
    global Rcvalue      #
    global Rbvalue      #
    global RcEntry
    global RbEntry
    global AWG2AmplEntry
    global DevTyp
    global Ibvalue
    global CH1sb        # spinbox Index for channel 1
    global CH2sb        # spinbox Index for channel 2
    global CH1Offset    # Offset value for channel 1
    global CH2Offset    # Offset value for channel 2
    global XYMode       # 0 = Time axis 1 = X Y mode 
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TIMEdiv      # current spin box value
    global SAMPLErate
    global TRIGGERsample
    global TRIGGERlevel
    global LONGchunk    # If longchunk is used for longsweep
    global COLORgrid    # The colors
    global COLORzeroline
    global COLORtrace1
    global COLORtrace2
    global COLORtext
    global COLORtrigger
    global CANVASwidth
    global CANVASheight
    global TRACErefresh
    global SCREENrefresh
    global DC1, DC2, Min1, Max1, Min2, Max2
    global version      # DWF software library version

    # Delete all items on the screen
    de = ca.find_enclosed ( -1000, -1000, CANVASwidth+1000, CANVASheight+1000)    
    for n in de: 
        ca.delete(n)
    # get time scale
    TIMEdiv = eval(TMsb.get())
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.1
    # get the vertical ranges
    CH1pdvRange = eval(CH1sb.get())
    CH2pdvRange = eval(CH2sb.get())
    # get Rc and Rb values
    Rcvalue = float(eval(RcEntry.get()))
    Rbvalue = float(eval(RbEntry.get()))
    Ibvalue = eval(AWG2AmplEntry.get())
    # prevent divide by zero error
    if CH1pdvRange < 0.01:
        CH1pdvRange = 0.01
    if CH2pdvRange < 0.01:
        CH2pdvRange = 0.01
        
    # Draw horizontal grid lines
    i = 0
    x1 = X0L
    x2 = X0L + GRW
    while (i < 11):
        y = Y0T + i * GRH/10
        Dline = [x1,y,x2,y]
        if i == 5:
            ca.create_line(Dline, fill=COLORzeroline)   # Blue line at center of grid
        else:
            ca.create_line(Dline, fill=COLORgrid)
            
        if XYMode == 0:
            axis_value = (((5-i) * CH1pdvRange ) + CH1Offset)
            axis_label = str(axis_value)
            ca.create_text(x1-3, y, text=axis_label, fill=COLORtrace1, anchor="e", font=("arial", 8 ))
            
        if (TRACES == 2 and XYMode == 0):
            axis_value = (((5-i) * CH2pdvRange ) + CH2Offset)/Rcvalue
            axis_label = str(axis_value)
            ca.create_text(x2+3, y, text=axis_label, fill=COLORtrace2, anchor="w", font=("arial", 8 ))
        if XYMode > 0:
            axis_value = (((5-i) * CH2pdvRange ) + CH2Offset)/Rcvalue
            axis_label = str(axis_value)
            ca.create_text(x1-3, y, text=axis_label, fill=COLORtrace1, anchor="e", font=("arial", 8 ))
            
        i = i + 1

    # Draw vertical grid lines
    i = 0
    y1 = Y0T
    y2 = Y0T + GRH
    vx = TIMEdiv
    while (i < 11):
        x = X0L + i * GRW/10
        Dline = [x,y1,x,y2]
        if (i == 5):
            ca.create_line(Dline, fill=COLORzeroline)   # Blue vertical line at T=0
            if XYMode == 0:
                ca.create_text(x, y2+3, text="0", fill=COLORgrid, anchor="n", font=("arial", 8 ))
            else:
                axis_value = (((i-5) * CH1pdvRange ) + CH1Offset)
                axis_label = str(axis_value)
                ca.create_text(x, y2+3, text=axis_label, fill=COLORtrace1, anchor="n", font=("arial", 8 ))
        else:
            ca.create_line(Dline, fill=COLORgrid)
            if XYMode == 0:
                if vx >= 1000:
                    axis_value = (i-5) * vx / 1000
                    axis_label = str(int(axis_value)) + " s/"
                if vx < 1000 and vx >= 1:
                    axis_value = (i-5) * vx
                    axis_label = str(int(axis_value)) + " ms"
                if vx < 1:
                    axis_value = (i-5) * vx * 1000
                    axis_label = str(int(axis_value)) + " us"
                ca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", 8 ))
            else:
                axis_value = CH1probe * (((i-5) * CH1pdvRange ) + CH1Offset)
                axis_label = str(axis_value)
                ca.create_text(x, y2+3, text=axis_label, fill=COLORtrace1, anchor="n", font=("arial", 8 ))
        i = i + 1

    # Write the trigger line if available
    if len(Triggerline) > 2:                                # Avoid writing lines with 1 coordinate
        ca.create_line(Triggerline, fill=COLORtrigger)

    # Write the traces if available
    if len(T1line) > 4:                                     # Avoid writing lines with 1 coordinate    
        ca.create_line(T1line, fill=COLORtrace1)            # Write the trace 1
    if TRACESread == 2 and TRACES == 2 and len(T2line) > 4: # Write the trace 2 if active
        ca.create_line(T2line, fill=COLORtrace2)            # and avoid writing lines with 1 coordinate

    # General information on top of the grid
    # Sweep information
    if LONGsweep == False and LONGchunk == False:
        sttxt = "Running"
        if (RUNstatus == 0) or (RUNstatus == 3):
            sttxt = "Stopped"

    if LONGsweep == True or LONGchunk == True:
        sttxt = "Running long sweep, wait"
        if (RUNstatus == 0) or (RUNstatus == 3):
            sttxt = "Stopped long sweep, press Start"

    txt = "DWF Library " + version.value + "   Sample rate: " + str(SAMPLErate) + " " + sttxt

    x = X0L
    y = 12
    idTXT = ca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)

    # Time sweep information and view at information
    vx = TIMEdiv
    if vx >= 1000:
        txt = str(int(vx/1000)) + " s/div"
    if vx < 1000 and vx >= 1:
        txt = str(int(vx)) + " ms/div"
    if vx < 1:
        txt = str(int(vx * 1000)) + " us/div"

    txt = txt + "     "
    vt = TriggerPos * -1000   # invert sign and scale to mSec
    txt = txt + "View at "
    if abs(vt) >= 1000:
        txt = txt + str(vt / 1000) + " s "
    if abs(vt) < 1000 and abs(vt) >= 1:
        txt = txt + str(vt) + " ms "
    if abs(vt) < 1:
        txt = txt + str(vt * 1000) + " us "

    x = X0L
    y = Y0T+GRH+20
    idTXT = ca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)

    # Channel 1 information
    
    vy = CH1pdvRange
    DC1String = ' {0:.4f} '.format(DC1)
    Min1String = ' {0:.4f} '.format(Min1)
    Max1String = ' {0:.4f} '.format(Max1)
    if vy >= 1:
        txt = str(vy) + " V/div DC value = " + DC1String + " Max value = " + Max1String + " Min value = " + Min1String
    if vy < 1:
        txt = str(vy*1000) + " mV/div DC value = " + DC1String + " Max value = " + Max1String + " Min value = " + Min1String
    
    x = X0L
    y = Y0T+GRH+32
    idTXT = ca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)

    # Channel 2 information
    if TRACESread == 2 and TRACES == 2:
        if (DevTyp.get() == 0): # NPN
            Ic = (Max2/Rcvalue) * 1000.0
            Ib = Ibvalue*4.0
            if Ib == 0.0:
                Beta = 0.0
            else:
                Beta = Ic/Ib
            IcString = ' {0:.2f} '.format(Ic)
        elif (DevTyp.get() == 1): # PNP
            Ic = (Min2/Rcvalue) * 1000.0
            Ib = Ibvalue*4.0
            if Ib == 0.0:
                Beta = 0.0
            else:
                Beta = Ic/Ib
            IcString = ' {0:.2f} '.format(Ic)
            
        BetaString = ' {0:.1f} '.format(Beta)    
        txt = "Beta at Ic = " + IcString + " mA is " + BetaString
        x = X0L
        y = Y0T+GRH+44
        idTXT = ca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)
    
# ================ Make Screen ==========================

root=Tk()
root.title("DiscoveryCurveTracer_1.py(w) (12-3-2013): Discovery Curve Tracer")

root.minsize(100, 100)

frame2r = Frame(root, borderwidth=5, relief=RIDGE)
frame2r.pack(side=RIGHT, expand=1, fill=Y)

frame1 = Frame(root, borderwidth=5, relief=RIDGE)
frame1.pack(side=TOP, expand=1, fill=X)

frame2 = Frame(root, background="black", borderwidth=5, relief=RIDGE)
frame2.pack(side=TOP, expand=1, fill=X)

frame3 = Frame(root, borderwidth=5, relief=RIDGE)
frame3.pack(side=TOP, expand=1, fill=X)
# make Trigger sub Menue
#
TgMode = IntVar(0)   # Trigger mode variable
TgChan = IntVar(0)   # Trigger Channel variable
TgEdge = IntVar(0)   # Trigger Edge variable
#
tm = Radiobutton(frame1, text="None", variable=TgMode, value=0, command=BTriggerMode)
tm.pack(side=LEFT)
tm = Radiobutton(frame1, text="Auto", variable=TgMode, value=1, command=BTriggerMode)
tm.pack(side=LEFT)
# tm = Radiobutton(frame1, text="Nornal", variable=TgMode, value=2, command=BTriggerMode)
# tm.pack(side=LEFT)

tch = Radiobutton(frame1, text="Channel1", variable=TgChan, value=0, command=BTriggerCH)
tch.pack(side=LEFT)
tch = Radiobutton(frame1, text="Channel2", variable=TgChan, value=1, command=BTriggerCH)
tch.pack(side=LEFT)

tedg = Radiobutton(frame1, text="Rising", variable=TgEdge, value=0, command=BTriggerEdge)
tedg.pack(side=LEFT)
tedg = Radiobutton(frame1, text="Falling", variable=TgEdge, value=1, command=BTriggerEdge)
tedg.pack(side=LEFT)

tlab = Label(frame1, text="Trigger Level")
tlab.pack(side=LEFT)
TRIGGERentry = Entry(frame1, width=6)
TRIGGERentry.bind("<Return>", BTriglevel)
TRIGGERentry.pack(side=LEFT, pady=3)

tgb = Button(frame1, text="50%", width=Buttonwidth2, command=BTrigger50p)
tgb.pack(side=LEFT)

b = Button(frame1, text="Exit", width=Buttonwidth2, command=Bcloseexit)
b.pack(side=RIGHT)

b = Button(frame1, text="Ic vs Vce", width=Buttonwidth3, command=BXYMode)
b.pack(side=RIGHT)

ca = Canvas(frame2, width=CANVASwidth, height=CANVASheight, background=COLORcanvas)
ca.pack(side=TOP)

# make power supply / Function Generator sub Menue
PfiveV = IntVar(0)   # +5 V power supply on/off variable
NfiveV = IntVar(0)   # -5 V power supply on/off variable
#
pslab = Label(frame2r, text="Power Supply")
pslab.grid(row=0, column=0, columnspan=2)
pv = Checkbutton(frame2r, text="+5V", variable=PfiveV, command=BSupplyOnOff)
pv.grid(row=1, column=0)
nv = Checkbutton(frame2r, text="-5V", variable=NfiveV, command=BSupplyOnOff)
nv.grid(row=1, column=1)
# now AWG 1
AWG1Enab = c_int(1)   # AWG1 on/off variable
awg1lab = Label(frame2r, text="Vce CH 1")
awg1lab.grid(row=2, column=0, columnspan=2)
Rclab = Label(frame2r, text="Rc in Ohms")
Rclab.grid(row=3, column=0)
RcEntry = Entry(frame2r, width=6)
RcEntry.bind("<Return>", BRc)
RcEntry.grid(row=3, column=1)
RcEntry.delete(0,"end")
RcEntry.insert(0,10.0)
amp1lab = Label(frame2r, text="Amplitude")
amp1lab.grid(row=4, column=0)
AWG1AmplEntry = Entry(frame2r, width=5)
AWG1AmplEntry.bind("<Return>", BAWG1Ampl)
AWG1AmplEntry.grid(row=4, column=1)
AWG1AmplEntry.delete(0,"end")
AWG1AmplEntry.insert(0,2.5)
off1lab = Label(frame2r, text="Offset")
off1lab.grid(row=5, column=0)
AWG1OffsetEntry = Entry(frame2r, width=5)
AWG1OffsetEntry.bind("<Return>", BAWG1Offset)
AWG1OffsetEntry.grid(row=5, column=1)
AWG1OffsetEntry.delete(0,"end")
AWG1OffsetEntry.insert(0,2.5)

# now AWG 2
AWG2Enab = c_int(1)   # AWG2 on/off variable
awg2lab = Label(frame2r, text="Ib CH 2")
awg2lab.grid(row=6, column=0, columnspan=2)
Rblab = Label(frame2r, text="Rb in KOhms")
Rblab.grid(row=7, column=0)
RbEntry = Entry(frame2r, width=6)
RbEntry.bind("<Return>", BRb)
RbEntry.grid(row=7, column=1)
RbEntry.delete(0,"end")
RbEntry.insert(0,20.0)
amp2lab = Label(frame2r, text="Ib Step (mA)")
amp2lab.grid(row=8, column=0)
AWG2AmplEntry = Entry(frame2r, width=5)
AWG2AmplEntry.bind("<Return>", BAWG2Ampl)
AWG2AmplEntry.grid(row=8, column=1)
AWG2AmplEntry.delete(0,"end")
AWG2AmplEntry.insert(0,0.02)
off2lab = Label(frame2r, text="Vbe Offset")
off2lab.grid(row=9, column=0)
AWG2OffsetEntry = Entry(frame2r, width=5)
AWG2OffsetEntry.bind("<Return>", BAWG2Ampl)
AWG2OffsetEntry.grid(row=9, column=1)
AWG2OffsetEntry.delete(0,"end")
AWG2OffsetEntry.insert(0,0.65)

DevTyp = IntVar(0)   # Device Type variable
dt = Radiobutton(frame2r, text="NPN", variable=DevTyp, value=0, command=BDevTyp)
dt.grid(row=10, column=0)
dt = Radiobutton(frame2r, text="PNP", variable=DevTyp, value=1, command=BDevTyp)
dt.grid(row=10, column=1)

# add ADI logo
logo = PhotoImage(file="adi_logo_small.gif")
ADI1 = Label(frame2r, image=logo, anchor= "sw", height=49, width=116, compound="top")
ADI1.grid(column=0,row=25,columnspan=2,rowspan=2)

# Bottom Buttons
b = Button(frame3, text="Run", width=5, fg="green", command=BStart)
b.pack(side=LEFT)

b = Button(frame3, text="Stop", width=5, fg="red", command=BStop)
b.pack(side=LEFT)

TMsb = Spinbox(frame3, width=5, values= TMpdiv, command=BTime)
TMsb.pack(side=LEFT)
TMsb.delete(0,"end")
TMsb.insert(0,5.0)
TMlab = Label(frame3, text="Time mS/Div")
TMlab.pack(side=LEFT)

CH1sb = Spinbox(frame3, width=4, values=CHvpdiv, command=BCH1level)

CH1sb.pack(side=LEFT)
CH1sb.delete(0,"end")
CH1sb.insert(0,5.0)
CH1lab = Label(frame3, text="Ch1 V/Div")
CH1lab.pack(side=LEFT)

CH1OffsetEntry = Entry(frame3, width=5)
CH1OffsetEntry.bind("<Return>", BOffset1)
CH1OffsetEntry.pack(side=LEFT, pady=3)
CH1OffsetEntry.delete(0,"end")
CH1OffsetEntry.insert(0,2.5)
CH1offlab = Label(frame3, text="CH1 Offset")
CH1offlab.pack(side=LEFT)

CH2sb = Spinbox(frame3, width=4, values=CHvpdiv, command=BCH2level)
CH2sb.pack(side=LEFT)
CH2sb.delete(0,"end")
CH2sb.insert(0,5.0)
CH1lab = Label(frame3, text="Ch2 V/Div")
CH1lab.pack(side=LEFT)

CH2OffsetEntry = Entry(frame3, width=5)
CH2OffsetEntry.bind("<Return>", BOffset2)
CH2OffsetEntry.pack(side=LEFT, pady=3)
CH2OffsetEntry.delete(0,"end")
CH2OffsetEntry.insert(0,0.0)
CH2offlab = Label(frame3, text="CH2 Offset")
CH2offlab.pack(side=LEFT)

# ================ Call main routine ===============================
root.update()               # Activate updated screens
#
# Start sampling
Analog_In()


