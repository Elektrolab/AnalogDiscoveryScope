# DiscoveryOscilloscope_6.py(w)  (11-13-2013)
# For Python version 2.6 or 2.7
# For DWF 2.7.0 (For Analog Discovery)
# Created by D Mercer ()
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

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
# query for Number of Devices
cdevices = c_int()
dwf.FDwfEnum(c_int(0), byref(cdevices))
# Opening first device
hdev = c_int()
dwf.FDwfDeviceOpen(c_int(0), byref(hdev))
# Values that can be modified
GRW = 700                   # Width of the grid
GRH = 400                   # Height of the grid was 500
X0L = 35                    # Left top X value of grid
Y0T = 25                    # Left top Y value of grid

SAMPLErate = 1000000        # initial Sample rate of the Scope channels
UPDATEspeed = 0.1           # Update speed, default 0.1, for slower PC's a higher value is perhaps required
TRIGGERlevel = 0.0          # Triggerlevel in volts
# Configure but not enable fixed power supplies
#dwf.FDwfAnalogIOChannelNodeSet(hdev, c_int(0), c_int(1), c_int(0))
#dwf.FDwfAnalogIOChannelNodeSet(hdev, c_int(1), c_int(1), c_int(0))
#dwf.FDwfAnalogIOEnableSet(hdev, c_int(1))
# configure AWG1 and 2 for output
dwf.FDwfAnalogOutReset(hdev, -1)
dwf.FDwfAnalogOutRunSet(hdev, 0, 0)
dwf.FDwfAnalogOutRunSet(hdev, 1, 0)
dwf.FDwfAnalogOutRepeatSet(hdev, 0, 0)
dwf.FDwfAnalogOutRepeatSet(hdev, 1, 0)
dwf.FDwfAnalogOutWaitSet(hdev, 0, 0)
dwf.FDwfAnalogOutWaitSet(hdev, 1, 0)
dwf.FDwfAnalogOutTriggerSourceSet(hdev, 0, 0)
dwf.FDwfAnalogOutTriggerSourceSet(hdev, 1, 0)
dwf.FDwfAnalogOutNodeEnableSet(hdev, c_int(0), c_int(0), c_bool(True))
dwf.FDwfAnalogOutNodeEnableSet(hdev, c_int(1), c_int(0), c_bool(True))
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
# AWG Frequency list
AWGFreq = ("Hz", "KHz", "MHz")
# AWG Wave Shapes list
AWGShape = ("DC", "Sine", "Square", "Triangle", "RampUp", "RampDown", "Noise")

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
TRACES = 1                  # Number of traces 1 or 2
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
    global DC1, DC2, Min1, Max1, Min2, Max2

    if (TgChan.get() == 0 ):
        trglvl = (Max1+Min1)/2.0
        DCString = ' {0:.2f} '.format(trglvl)
    else:
        trglvl = (Max2+Min2)/2.0
        DCString = ' {0:.2f} '.format(trglvl)

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
    
    if (RUNstatus == 0):
        RUNstatus = 1
    UpdateScreen()          # Always Update

def BStop():
    global RUNstatus
    
    if (RUNstatus == 1):
        RUNstatus = 0
    elif (RUNstatus == 2):
        RUNstatus = 3
    elif (RUNstatus == 3):
        RUNstatus = 3
    elif (RUNstatus == 4):
        RUNstatus = 3
    UpdateScreen()          # Always Update

def Bprobe():
    global CH1probe
    global CH2probe
    global RUNstatus
    global CH1Probe
    global CH2Probe
    
    CH1probe = eval(CH1Probe.get())
    CH2probe = eval(CH2Probe.get())
    UpdateScreen()          # Always Update

def BView1():
    global TIMEdiv
    global TMsb
    global TriggerPos
    global SAMPLErate
    global RUNstatus
    global hdev
    
    TIMEdiv = eval(TMsb.get())
    TriggerPos = TriggerPos - (TIMEdiv / 1000)
    if abs(TriggerPos) < 0.000001:
        TriggerPos = 0.0
    dwf.FDwfAnalogInTriggerPositionSet(hdev, c_double(TriggerPos))
    UpdateTrace()           # Always Update

def BView2():
    global TIMEdiv
    global TMsb
    global TriggerPos
    global SAMPLErate
    global TIMEdiv1x
    global RUNstatus
    global hdev
    
    TIMEdiv = eval(TMsb.get())
    TriggerPos = TriggerPos + (TIMEdiv / 1000)
    if abs(TriggerPos) < 0.000001:
        TriggerPos = 0.0
    dwf.FDwfAnalogInTriggerPositionSet(hdev, c_double(TriggerPos))  
    UpdateTrace()           # Always Update

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

def BTraces():
    global TRACES
    global RUNstatus
    
    if (TRACES == 1):
        TRACES = 2
    else:
        TRACES = 1

    if RUNstatus == 2:      # Restart if running
        RUNstatus = 4
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
    
def BAWG1Freq(temp):
    global hdev
    global AWG1FreqEntry
    global AWG1Freqvalue
    global AWG1Freqsb

    AWG1Freqvalue = float(eval(AWG1FreqEntry.get()))
    if AWG1Freqsb.get() == "KHz":
        AWG1Freqvalue = AWG1Freqvalue * 1000
    if AWG1Freqsb.get() == "MHz":
        AWG1Freqvalue = AWG1Freqvalue * 1000000
        if AWG1Freqvalue > 10000000: # max freq is 10MHz
            AWG1Freqvalue = 10000000

    dwf.FDwfAnalogOutNodeFrequencySet(hdev, c_int(0), c_int(0), c_double(AWG1Freqvalue))

def BAWG1Phase(temp):
    global hdev
    global AWG1PhaseEntry
    global AWG1Phasevalue

    AWG1Phasevalue = float(eval(AWG1PhaseEntry.get()))
    dwf.FDwfAnalogOutNodePhaseSet(hdev, c_int(0), c_int(0), c_double(AWG1Phasevalue))

def BAWG1Symmetry(temp):
    global hdev
    global AWG1SymmetryEntry
    global AWG1Symmetryvalue

    AWG1Symmetryvalue = float(eval(AWG1SymmetryEntry.get()))
    dwf.FDwfAnalogOutNodeSymmetrySet(hdev, c_int(0), c_int(0), c_double(AWG1Symmetryvalue))        

#FUNC;
#funcDC       = c_byte(0)
#funcSine     = c_byte(1)
#funcSquare   = c_byte(2)
#funcTriangle = c_byte(3)
#funcRampUp   = c_byte(4)
#funcRampDown = c_byte(5)
#funcNoise    = c_byte(6)
#funcCustom   = c_byte(30)
#funcPlay     = c_byte(31)
    
def BAWG1Shape():
    global hdev
    global AWG1Shapesb

    if AWG1Shapesb.get() == "DC":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(0), c_int(0), c_byte(0))
    if AWG1Shapesb.get() == "Sine":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(0), c_int(0), c_byte(1))
    if AWG1Shapesb.get() == "Square":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(0), c_int(0), c_byte(2))
    if AWG1Shapesb.get() == "Triangle":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(0), c_int(0), c_byte(3))
    if AWG1Shapesb.get() == "RampUp":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(0), c_int(0), c_byte(4))
    if AWG1Shapesb.get() == "RampDown":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(0), c_int(0), c_byte(5))
    if AWG1Shapesb.get() == "Noise":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(0), c_int(0), c_byte(6))

def BAWG2Ampl(temp):
    global hdev
    global AWG2AmplEntry
    global AWG2Amplvalue

    AWG2Amplvalue = float(eval(AWG2AmplEntry.get()))
    dwf.FDwfAnalogOutNodeAmplitudeSet(hdev, c_int(1), c_int(0), c_double(AWG2Amplvalue))
    
def BAWG2Offset(temp):
    global hdev
    global AWG2OffsetEntry
    global AWG2Offsetvalue

    AWG2Offsetvalue = float(eval(AWG2OffsetEntry.get()))
    dwf.FDwfAnalogOutNodeOffsetSet(hdev, c_int(1), c_int(0), c_double(AWG2Offsetvalue))
    
def BAWG2Freq(temp):
    global hdev
    global AWG2FreqEntry
    global AWG2Freqvalue
    global AWG2Freqsb

    AWG2Freqvalue = float(eval(AWG2FreqEntry.get()))
    if AWG2Freqsb.get() == "KHz":
        AWG2Freqvalue = AWG2Freqvalue * 1000
    if AWG2Freqsb.get() == "MHz":
        AWG2Freqvalue = AWG2Freqvalue * 1000000
        if AWG2Freqvalue > 10000000:
            AWG2Freqvalue = 10000000
        
    dwf.FDwfAnalogOutNodeFrequencySet(hdev, c_int(1), c_int(0), c_double(AWG2Freqvalue))

def BAWG2Phase(temp):
    global hdev
    global AWG2PhaseEntry
    global AWG2Phasevalue

    AWG2Phasevalue = float(eval(AWG2PhaseEntry.get()))
    dwf.FDwfAnalogOutNodePhaseSet(hdev, c_int(1), c_int(0), c_double(AWG2Phasevalue))

def BAWG2Symmetry(temp):
    global hdev
    global AWG2SymmetryEntry
    global AWG2Symmetryvalue

    AWG2Symmetryvalue = float(eval(AWG2SymmetryEntry.get()))
    dwf.FDwfAnalogOutNodeSymmetrySet(hdev, c_int(1), c_int(0), c_double(AWG2Symmetryvalue))        

def BAWG2Shape():
    global hdev
    global AWG2Shapesb

    if AWG2Shapesb.get() == "DC":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(1), c_int(0), c_byte(0))
    if AWG2Shapesb.get() == "Sine":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(1), c_int(0), c_byte(1))
    if AWG2Shapesb.get() == "Square":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(1), c_int(0), c_byte(2))
    if AWG2Shapesb.get() == "Triangle":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(1), c_int(0), c_byte(3))
    if AWG2Shapesb.get() == "RampUp":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(1), c_int(0), c_byte(4))
    if AWG2Shapesb.get() == "RampDown":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(1), c_int(0), c_byte(5))
    if AWG2Shapesb.get() == "Noise":
        dwf.FDwfAnalogOutNodeFunctionSet(hdev, c_int(1), c_int(0), c_byte(6))

def BAWGEnab():
    global hdev
    global AWG1Enab
    global AWG2Enab
    global AWGSync

    if  AWG1Enab.get() > 0:
        dwf.FDwfAnalogOutNodeEnableSet(hdev, c_int(0), c_int(0), c_bool(True))
    else:
        dwf.FDwfAnalogOutNodeEnableSet(hdev, c_int(0), c_int(0), c_bool(False))

    if  AWG2Enab.get() > 0:
        dwf.FDwfAnalogOutNodeEnableSet(hdev, c_int(1), c_int(0), c_bool(True))
    else:
        dwf.FDwfAnalogOutNodeEnableSet(hdev, c_int(1), c_int(0), c_bool(False))
        
    if AWGSync.get() > 0:
        # make channel 1 master
        dwf.FDwfAnalogOutMasterSet(hdev, c_int(-1), c_int(0))
        # start channel 2, this will only configure the channel
        dwf.FDwfAnalogOutConfigure(hdev, c_int(1), c_bool(True))
        # start channel 1, this will start the slave channels too
        dwf.FDwfAnalogOutConfigure(hdev, c_int(0), c_bool(True))
    else:
        if AWG1Enab.get() > 0:
            dwf.FDwfAnalogOutConfigure(hdev, c_int(0), c_bool(True))
        else:
            dwf.FDwfAnalogOutConfigure(hdev, c_int(0), c_bool(False))
        if AWG2Enab.get() > 0:
            dwf.FDwfAnalogOutConfigure(hdev, c_int(1), c_bool(True))
        else:
            dwf.FDwfAnalogOutConfigure(hdev, c_int(1), c_bool(False))

def BAWGSync():
    global hdev
    global AWGSync

    if AWGSync.get() > 0:
        # make channel 1 master
        dwf.FDwfAnalogOutMasterSet(hdev, c_int(-1), c_int(0))
        # start channel 2, this will only configure the channel
        dwf.FDwfAnalogOutConfigure(hdev, c_int(1), c_bool(True))
        # start channel 1, this will start the slave channels too
        dwf.FDwfAnalogOutConfigure(hdev, c_int(0), c_bool(True))
    else:
        dwf.FDwfAnalogOutConfigure(hdev, c_int(-1), c_bool(False)) 

    
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
        Yconv2 = float(GRW/10) / CH2pdvRange
        while (t < TRACEsize):
            ylo = float(ADsignal1[int(t)] - CH1Offset)
            xlo = float(ADsignal2[int(t)] - CH2Offset)
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
    global CH1probe     # Probe attenuation factor 1x, 10x or 0.1 x of channel 1
    global CH2probe     # Probe attenuation factor 1x, 10x or 0.1 x of channel 2
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
            
        axis_value = CH1probe * (((5-i) * CH1pdvRange ) + CH1Offset)
        axis_label = str(axis_value)
        ca.create_text(x1-3, y, text=axis_label, fill=COLORtrace1, anchor="e", font=("arial", 8 ))
        if (TRACES == 2 and XYMode == 0):
            axis_value = CH2probe * (((5-i) * CH2pdvRange ) + CH2Offset)
            axis_label = str(axis_value)
            ca.create_text(x2+3, y, text=axis_label, fill=COLORtrace2, anchor="w", font=("arial", 8 ))
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
                axis_value = CH2probe * (((i-5) * CH2pdvRange ) + CH2Offset)
                axis_label = str(axis_value)
                ca.create_text(x, y2+3, text=axis_label, fill=COLORtrace2, anchor="n", font=("arial", 8 ))
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
                axis_value = CH2probe * (((i-5) * CH2pdvRange ) + CH2Offset)
                axis_label = str(axis_value)
                ca.create_text(x, y2+3, text=axis_label, fill=COLORtrace2, anchor="n", font=("arial", 8 ))
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
    if CH1probe == 0.1:
        txt = "0.1x CH1: "
                           
    if CH1probe == 1:
        txt = "1x CH1: "
        
    if CH1probe == 10:
        txt = "10x CH1: "

    if CH1probe == 100:
        txt = "100x CH1: "

    vy = CH1probe * CH1pdvRange
    DC1String = ' {0:.4f} '.format(CH1probe * DC1)
    Min1String = ' {0:.4f} '.format(CH1probe * Min1)
    Max1String = ' {0:.4f} '.format(CH1probe * Max1)
    if vy >= 1:
        txt = txt + str(vy) + " V/div DC value = " + DC1String + " Max value = " + Max1String + " Min value = " + Min1String
    if vy < 1:
        txt = txt + str(vy*1000) + " mV/div DC value = " + DC1String + " Max value = " + Max1String + " Min value = " + Min1String
    
    x = X0L
    y = Y0T+GRH+32
    idTXT = ca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)

    # Channel 2 information
    if TRACESread == 2 and TRACES == 2:
        if CH2probe == 0.1:
            txt = "0.1x CH2: "
                           
        if CH2probe == 1:
            txt = "1x CH2: "
        
        if CH2probe == 10:
            txt = "10x CH2: "

        if CH2probe == 100:
            txt = "100x CH2: "
            
        vy = CH2probe * CH2pdvRange
        DC2String = ' {0:.4f} '.format(CH2probe * DC2)
        Min2String = ' {0:.4f} '.format(CH1probe * Min2)
        Max2String = ' {0:.4f} '.format(CH1probe * Max2)
        if vy >= 1:
            txt = txt + str(vy) + " V/div DC value = " + DC2String + " Max value = " + Max2String + " Min value = " + Min2String
        if vy < 1:
            txt = txt + str(vy*1000) + " mV/div DC value = " + DC2String + " Max value = " + Max2String + " Min value = " + Min2String

        x = X0L
        y = Y0T+GRH+44
        idTXT = ca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)
    
# ================ Make Screen ==========================

root=Tk()
root.title("DiscoveryOscilloscope_6.py(w) (11-17-2013): Discovery Oscilloscope")

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

b = Button(frame1, text="1/2 Channels", width=Buttonwidth1, command=BTraces)
b.pack(side=RIGHT)

b = Button(frame1, text="X-Y Mode", width=Buttonwidth3, command=BXYMode)
b.pack(side=RIGHT)

ca = Canvas(frame2, width=CANVASwidth, height=CANVASheight, background=COLORcanvas)
ca.pack(side=TOP)

# make power supply / Function Generator sub Menue
PfiveV = IntVar(0)   # +5 V power supply on/off variable
NfiveV = IntVar(0)   # -5 V power supply on/off variable
#
ps1lab = Label(frame2r, text="Power Supply")
ps1lab.grid(row=0, column=0, columnspan=2)
pv = Checkbutton(frame2r, text="+5V", variable=PfiveV, command=BSupplyOnOff)
pv.grid(row=1, column=0)
nv = Checkbutton(frame2r, text="-5V", variable=NfiveV, command=BSupplyOnOff)
nv.grid(row=1, column=1)
# now AWG 1
AWG1Enab = IntVar(0)   # AWG1 on/off variable
awg1lab1 = Label(frame2r, text="AWG CH 1")
awg1lab1.grid(row=2, column=0, columnspan=2)
awg1en = Checkbutton(frame2r, text="Enable", variable=AWG1Enab, command=BAWGEnab)
awg1en.grid(row=3, column=0)
amp1lab = Label(frame2r, text="Amplitude")
amp1lab.grid(row=4, column=0)
AWG1AmplEntry = Entry(frame2r, width=5)
AWG1AmplEntry.bind("<Return>", BAWG1Ampl)
AWG1AmplEntry.grid(row=4, column=1)
AWG1AmplEntry.delete(0,"end")
AWG1AmplEntry.insert(0,0.0)
off1lab = Label(frame2r, text="Offset")
off1lab.grid(row=5, column=0)
AWG1OffsetEntry = Entry(frame2r, width=5)
AWG1OffsetEntry.bind("<Return>", BAWG1Offset)
AWG1OffsetEntry.grid(row=5, column=1)
AWG1OffsetEntry.delete(0,"end")
AWG1OffsetEntry.insert(0,0.0)
freq1lab = Label(frame2r, text="Frequency")
freq1lab.grid(row=6, column=0)
AWG1FreqEntry = Entry(frame2r, width=5)
AWG1FreqEntry.bind("<Return>", BAWG1Freq)
AWG1FreqEntry.grid(row=6, column=1)
AWG1FreqEntry.delete(0,"end")
AWG1FreqEntry.insert(0,0.0)
AWG1Freqsb = Spinbox(frame2r, width=4, values=AWGFreq, command=BAWG1Freq)
AWG1Freqsb.grid(row=7, column=1)
phase1lab = Label(frame2r, text="Phase")
phase1lab.grid(row=8, column=0)
AWG1PhaseEntry = Entry(frame2r, width=5)
AWG1PhaseEntry.bind("<Return>", BAWG1Phase)
AWG1PhaseEntry.grid(row=8, column=1)
AWG1PhaseEntry.delete(0,"end")
AWG1PhaseEntry.insert(0,0.0)
sym1lab = Label(frame2r, text="Symmetry")
sym1lab.grid(row=9, column=0)
AWG1SymmetryEntry = Entry(frame2r, width=5)
AWG1SymmetryEntry.bind("<Return>", BAWG1Symmetry)
AWG1SymmetryEntry.grid(row=9, column=1)
AWG1SymmetryEntry.delete(0,"end")
AWG1SymmetryEntry.insert(0,50.0)
AWG1Shapesb = Spinbox(frame2r, width=7, values=AWGShape, command=BAWG1Shape)
AWG1Shapesb.grid(row=10, column=0)

# now AWG 2
AWG2Enab = IntVar(0)   # AWG2 on/off variable
awg2lab1 = Label(frame2r, text="AWG CH 2")
awg2lab1.grid(row=11, column=0, columnspan=2)
awg2en = Checkbutton(frame2r, text="Enable", variable=AWG2Enab, command=BAWGEnab)
awg2en.grid(row=12, column=0)
amp2lab = Label(frame2r, text="Amplitude")
amp2lab.grid(row=13, column=0)
AWG2AmplEntry = Entry(frame2r, width=5)
AWG2AmplEntry.bind("<Return>", BAWG2Ampl)
AWG2AmplEntry.grid(row=13, column=1)
AWG2AmplEntry.delete(0,"end")
AWG2AmplEntry.insert(0,0.0)
off2lab = Label(frame2r, text="Offset")
off2lab.grid(row=14, column=0)
AWG2OffsetEntry = Entry(frame2r, width=5)
AWG2OffsetEntry.bind("<Return>", BAWG2Offset)
AWG2OffsetEntry.grid(row=14, column=1)
AWG2OffsetEntry.delete(0,"end")
AWG2OffsetEntry.insert(0,0.0)
freq2lab = Label(frame2r, text="Frequency")
freq2lab.grid(row=15, column=0)
AWG2FreqEntry = Entry(frame2r, width=5)
AWG2FreqEntry.bind("<Return>", BAWG2Freq)
AWG2FreqEntry.grid(row=15, column=1)
AWG2FreqEntry.delete(0,"end")
AWG2FreqEntry.insert(0,0.0)
AWG2Freqsb = Spinbox(frame2r, width=4, values=AWGFreq, command=BAWG2Freq)
AWG2Freqsb.grid(row=16, column=1)
phase2lab = Label(frame2r, text="Phase")
phase2lab.grid(row=17, column=0)
AWG2PhaseEntry = Entry(frame2r, width=5)
AWG2PhaseEntry.bind("<Return>", BAWG2Phase)
AWG2PhaseEntry.grid(row=17, column=1)
AWG2PhaseEntry.delete(0,"end")
AWG2PhaseEntry.insert(0,0.0)
sym2lab = Label(frame2r, text="Symmetry")
sym2lab.grid(row=18, column=0)
AWG2SymmetryEntry = Entry(frame2r, width=5)
AWG2SymmetryEntry.bind("<Return>", BAWG2Symmetry)
AWG2SymmetryEntry.grid(row=18, column=1)
AWG2SymmetryEntry.delete(0,"end")
AWG2SymmetryEntry.insert(0,50.0)
AWG2Shapesb = Spinbox(frame2r, width=7, values=AWGShape, command=BAWG2Shape)
AWG2Shapesb.grid(row=19, column=0)

AWGSync = IntVar(0) # Sync start both AWG channels
awgsync = Checkbutton(frame2r, text="Sync AWG", variable=AWGSync, command=BAWGSync)
awgsync.grid(row=20, column=0)
#
prbslab = Label(frame2r, text="Input Probes")
prbslab.grid(row=21, column=0, columnspan=2)
probe1lab = Label(frame2r, text="Probe 1")
probe1lab.grid(row=22, column=0)
probe2lab = Label(frame2r, text="Probe 2")
probe2lab.grid(row=22, column=1)
CH2Probe = Spinbox(frame2r, width=4, values=ProbeList, command=Bprobe)
CH2Probe.grid(row=23, column=0)
CH2Probe.delete(0,"end")
CH2Probe.insert(0,1.0)
CH1Probe = Spinbox(frame2r, width=4, values=ProbeList, command=Bprobe)
CH1Probe.grid(row=23, column=1)
CH1Probe.delete(0,"end")
CH1Probe.insert(0,1.0)
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
TMsb.insert(0,0.2)
TMlab = Label(frame3, text="Time mS/Div")
TMlab.pack(side=LEFT)

b = Button(frame3, text="+HPan", width=Buttonwidth2, command=BView1)
b.pack(side=LEFT)

b = Button(frame3, text="-HPan", width=Buttonwidth2, command=BView2)
b.pack(side=LEFT)
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
CH1OffsetEntry.insert(0,0.0)
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


