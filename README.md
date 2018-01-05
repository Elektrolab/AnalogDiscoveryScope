# AnalogDiscoveryScope
Oscilloscope app for the Digilent Analog Discovery board !

Cloned from https://ez.analog.com/community/university-program/blog/2013/12/07/analog-discovery-bjt-curve-tracer-program


Original blog post below by Doug, in case the link breaks.

"
Analog Discovery BJT Curve Tracer Program

A number of months ago I wrote a blog on a Curve Tracer adapter for Analog Discovery (http://ez.analog.com/community/university-program/blog/2012/06/30/two-wire-curve-tracer). I also published these example Lab experiments on the ADI Wiki University Content web site (https://wiki.analog.com/university/courses/electronics/electronics-lab-4 and https://wiki.analog.com/university/courses/eps/bjt-i-v-curves). While you can configure the supplied Waveforms software to properly drive the device terminal voltages and display the collector current (Ic) vs. the collector emitter voltage (Vce) it isn’t exactly a simple process requiring many steps and multiple screens.

Now that the software development kit (SDK) for Analog Discovery is available I’m finally able to write a dedicated BJT Curve Tracer program to go along with these lab activities. As a place to start and to serve as a learning platform for the SDK, I actually started by writing a generic Oscilloscope / AWG program in Python ( 2.6/2.7 ) loosely based on a sound card oscilloscope program. While doing this I was also testing to see if the program also works in Linux. In the process I uncovered a few bugs in the Linux version of the SDK 2.6.0 ( and the Adept run time 2.13.1) down loadable as of the writing of this Blog. After pointing these bugs out to Digilent, they provided me with access to newer versions of both the Windows and Linux software ( SDK 2.7.0 and Adept 2.14.3 ) to use while developing these programs. So the Python programs attached to the end of this blog have only been tested with these not yet released packages. They might work in Windows with SDK 2.6.2 but probably not in Linux with SDK 2.6.0/Adept 2.13.1. Hopefully, these newer packages will be available for download shortly.

Writing a basic Oscilloscope program first, screen shot shown in figure 1, while by no means a replacement for the supplied Waveforms package, does serve well as a framework for building more hardware specific interfaces like the Curve Tracer. It also provides a means to have software that supports both Windows and Linux operating systems.

![AD_Oscilloscope.gif](Images/AD_Oscilloscope.gif?raw=true " ")

Figure 1, Python Oscilloscope Screen Shot

So let’s get started on the Curve Tracer program. The circuit connections for an NPN BJT transistor is shown in figure 2.  AWG1 provides the variable collector voltage (Vce) and is measured by scope channel 1. The collector current is obtained by measuring the voltage across a low value resistor, Rc, by differential scope input channel 2. AWG2 provides a series of DC voltage steps which are converted into base current steps (Ib) by a high value resistor Rb. The voltage steps generated by AWG channel 2 must be offset by the Vbe of the transistor as shown by the equation for Ib in the figure. This same basic circuit configuration can be used for PNP devices as well, you would just need to change the sign of the voltages applied to the collector and base resistors ( i.e. negative with respect to ground ).

![AD_Oscilloscope.gif](Images/A4_F1.png?raw=true " ")

Figure 1, Curve Tracer configuration for NPN transistor

So our Curve Tracer program must do some simple math to program the voltage generators and properly display a set of Ic vs. Vce curves for a series of Ib values. The user will need to be able to input the values of Rc and Rb that are being used and the range of the Vce sweep and the Ib step size. Figure 3 is a screen shot of the Python Curve Tracer program. This screen snap shot is displaying the characteristic curves for an NPN 2N3904, supplied from the Analog Parts Kit. The Vce is swept from 0 to 5V for 5 different Ib steps of 0.02 mA each. The beta is calculated at the peak Ic and is displayed at the bottom of the screen. This is only accurate if the Vbe offset is adjusted such that the bottom ( Ib = 0 ) curve falls just at the Ic = 0 line.

 
![AD_Oscilloscope.gif](Images/AD_curve_tracer_npn.gif?raw=true " ")

Figure 3, Python BJT Curve Tracer Screen Shot

As you can see on the right hand side of the screen there are the controls for the Vce sweep amplitude/offset, the Ib step size and the Vbe offset. There are places to enter the values for Rc  and Rb (10 Ohms and 20 KOhms in this case). You can also select either NPN or PNP device types. To configure the program for a PNP you simply need to input a negative offset for Vce and negative values for the Ib steps. Controls to turn on and off the fixed power supplies are provided in case these are needed to supply a fixed bias to part of the circuit.

 

Along the bottom of the screen are controls for the vertical and horizontal scales. Ch1 is for the horizontal axis, Vce. You can set both the volts/div and the offset. Likewise Ch2 is for the vertical axis, Ic. Again the scale and offset can be adjusted. Run and Stop buttons are on the left.

 

Along the top of the screen are some additional controls. The program can also display the Vce and Ic waveforms vs. time like a normal scope by toggling the Ic vs Vce button. To have a stable time display, triggering options are provided. It is important to only exit the program by clicking on the Exit button, to properly shut down Analog Discovery, and not use the other conventional window close button.

 

Program files, AD_Scope.zip and AD_Curve_Tracer.zip for this demonstration are attached to this blog. Each archive contains the main Python (2.6/2.7) program, a .csv file containing the stair step waveform for the base current and the ADI logo graphic. Remember, these programs were developed using Waveforms SDK 2.7.0 and the Adept run time 2.14.3 for Linux.

In conclusion, a BJT transistor curve tracer application is a perfect candidate for writing a custom Python control program using the Analog Discovery SDK. The nice thing about open source, interpreted programs like this are that if users don’t like the functionality or the user interface they can modify the program to fit their specific needs. For example, rewriting the base current controls to instead generate gate voltage steps for a MOSFET curve tracer.

As always I welcome comments and suggestions from the user community out there.

Doug
"
