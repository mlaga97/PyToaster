#!/usr/bin/python

import serial
import time
import wx

from threading import Thread
from wx.lib.pubsub import Publisher

########################################################################

highest_temp = -1000
lowest_temp = 1000
duty_cycle = 10
cycle_length = 6
min_temp = 48
max_temp = 50

########################################################################
class TestThread(Thread):
	"""Test Worker Thread Class."""
    
    #-----------------------------------------------------------------------
	def __init__(self):
		"""Init Worker Thread Class."""
		Thread.__init__(self)
		self.start()    # start the thread
 
    #-----------------------------------------------------------------------
	def run(self):
		"""Run Worker Thread. """
		
		print "Opening serial port..."
		ser = serial.Serial('/dev/ttyACM0', 115200)
		
		print "Waiting for handshake..."
		start = ser.readline()

		print "Received handshake!"
		print "Setting pin modes..."
		ser.write( "m" + chr(6) + chr(1) )

		while True:
			ser.write( "t" )
			temperature = float(ser.readline())
			
			# Post Temperature
			wx.CallAfter(self.postTemp, temperature)
			print time.ctime() + " Temp: " + str(temperature) + "C, Duty Cycle: " + str(duty_cycle) + "%, Cycle Length: " + str(cycle_length) + "s, Min Temp: " + str(min_temp) + "C, Max Temp: " + str(max_temp) + "C"
			
			# Control Loop
			if temperature < max_temp:
				# Turn on relay
				ser.write( "w" + chr(6) + chr(1) )
				time.sleep( float(duty_cycle)/float(100)*float(cycle_length) )
				
				# Turn off relay
				ser.write( "w" + chr(6) + chr(0) )
				time.sleep( float(100-duty_cycle)/float(100)*float(cycle_length) )
			else:
				ser.write( "w" + chr(6) + chr(0) )
				time.sleep(1)
 
	#-----------------------------------------------------------------------
	def postTemp(self, current_temp):
		"""Send current temperature to GUI"""
		Publisher().sendMessage("TemperatureUpdate", current_temp)

########################################################################
class MyForm(wx.Frame):
    #----------------------------------------------------------------------
    def onButton(self, event):
        """
        Runs the thread
        """
        self.displayLbl.SetLabel("Thread started!")
        btn = event.GetEventObject()
        btn.Disable()
 
    #----------------------------------------------------------------------
    def updateDisplay(self, msg):
        """
        Receives data from thread and updates the display
        """
        t = msg.data
        if isinstance(t, int):
            self.displayLbl.SetLabel("Time since thread started: %s seconds" % t)
        else:
            self.displayLbl.SetLabel("%s" % t)
            self.btn.Enable()

########################################################################
class ParameterSelector(wx.Frame):
	
	#-----------------------------------------------------------------------
	def __init__(self, parent, id, title):
 
        # Add a panel so it looks the correct on all platforms
		"""panel = wx.Panel(self, wx.ID_ANY)
		self.displayLbl = wx.StaticText(panel, label="Amount of time since thread started goes here")
		self.btn = btn = wx.Button(panel, label="Start Thread")
 
		btn.Bind(wx.EVT_BUTTON, self.onButton)
 
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.displayLbl, 0, wx.ALL|wx.CENTER, 5)
		sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)
		panel.SetSizer(sizer)
		"""
		
        # create a pubsub receiver
		Publisher().subscribe(self.updateTemperature, "TemperatureUpdate")
		
        # Create Window
		wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(210, 200))
        
        # Min Temp
		wx.StaticText(self, -1, 'C', (80, 20))
		wx.StaticText(self, -1, 'Min Temp', (110, 20))
		self.min_temp_sc = wx.SpinCtrl(self, -1, str(min_temp), (20, 15), (60, -1), min=0, max=300)
        
        # Max Temp
		wx.StaticText(self, -1, 'C', (80, 50))
		wx.StaticText(self, -1, 'Max Temp', (110, 50))
		self.max_temp_sc = wx.SpinCtrl(self, -1, str(max_temp), (20, 45), (60, -1), min=0, max=300)
        
        # Duty Cycle
		wx.StaticText(self, -1, '%', (80, 80))
		wx.StaticText(self, -1, 'Duty Cycle', (110, 80))
		self.duty_cycle_sc = wx.SpinCtrl(self, -1, str(duty_cycle), (20, 75), (60, -1), min=0, max=100)
        
        # Cycle Length
		wx.StaticText(self, -1, 'sec', (80, 110))
		wx.StaticText(self, -1, 'Cycle Length', (110, 110))
		self.cycle_length_sc = wx.SpinCtrl(self, -1, str(cycle_length), (20, 105), (60, -1), min=1, max=30)
       
        # Apply Button
		wx.Button(self, 1, 'Apply', (63, 140))
		self.Bind(wx.EVT_BUTTON, self.onApply, id=1)
        
        # Status Bar
		self.statusbar = self.CreateStatusBar()
		self.statusbar.SetFieldsCount(3)
        
        # Center on Screen
		self.Centre()
        
        # Start Thread
		TestThread()

    #-----------------------------------------------------------------------
	def onApply(self, event):
		global min_temp, max_temp, duty_cycle, cycle_length
		
		min_temp = self.min_temp_sc.GetValue()
		max_temp = self.max_temp_sc.GetValue()
		duty_cycle = self.duty_cycle_sc.GetValue()
		cycle_length = self.cycle_length_sc.GetValue()
        
		self.statusbar.SetStatusText('Applied Config')
		time.sleep(0.5)
		self.statusbar.SetStatusText( "L: " + str(lowest_temp) + "C", 0 )

    #-----------------------------------------------------------------------
	def updateTemperature(self, event):
		global lowest_temp, highest_temp
		
		if event.data < lowest_temp:
			lowest_temp = event.data
			self.statusbar.SetStatusText( "L: " + str(event.data) + "C", 0 )

		self.statusbar.SetStatusText( "C: " + str(event.data) + "C", 1 )

		if event.data > highest_temp:
			highest_temp = event.data
			self.statusbar.SetStatusText( "H: " + str(event.data) + "C", 2 )
		
		

########################################################################
class MyApp(wx.App):
	
	#-----------------------------------------------------------------------
    def OnInit(self):
        frame = ParameterSelector(None, -1, 'Toast Commander')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


app = MyApp(0)
app.MainLoop()
