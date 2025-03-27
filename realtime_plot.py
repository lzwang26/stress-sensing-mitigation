import serial
import serial.tools.list_ports
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class ArduinoReader:
    def __init__(self):
        self.serial_port = None
        self.times = []
        self.values = []
        self.max_points = 1000
        self.time_window = 10  # Display last 10 seconds
        self.start_time = None
        self.line = None
        self.fig = None
        self.ax = None
        self.animation = None
        
    def find_arduino_port(self):
        print("Checking available ports...")
        ports = list(serial.tools.list_ports.comports())
        
        for port in ports:
            print(f"Found port: {port.device} - {port.description}")
            if any(identifier in port.description.lower() for identifier in 
                    ['arduino', 'ch340', 'usb serial', 'usb2.0-serial', 'usb2.0-s', 'iobusbhostdevice']) or \
                any(identifier in port.device.lower() for identifier in 
                    ['usbmodem', 'usbserial', 'tty.usbmodem', 'tty.usbserial']):
                print(f"Found Arduino on port: {port.device}")
                return port.device
        
        print("No Arduino found on any port")
        return None
    
    def read_all_available_data(self):
        """Read all available data from Arduino in one go"""
        data_read = False
        
        # Read as much data as is available
        while self.serial_port and self.serial_port.in_waiting:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    value = int(line)
                    print(f"Read: {value} at time {time.time() - self.start_time:.2f}s")
                    
                    # Store value and time
                    current_time = time.time() - self.start_time
                    self.times.append(current_time)
                    self.values.append(value)
                    
                    # Keep only the last max_points
                    if len(self.times) > self.max_points:
                        self.times.pop(0)
                        self.values.pop(0)
                    
                    data_read = True
            except Exception as e:
                print(f"Error reading data: {e}")
        
        return data_read
    
    def update_plot(self, frame):
        """Update function for the animation"""
        # Read all available data
        self.read_all_available_data()
        
        # Update plot
        if self.times and self.values:
            self.line.set_data(self.times, self.values)
            
            # Set fixed y-axis range for stability
            if len(self.values) > 5:  # Wait until we have some data
                current_min = min(self.values)
                current_max = max(self.values)
                y_range = max(50, current_max - current_min)  # Ensure minimum range
                y_mid = (current_min + current_max) / 2
                self.ax.set_ylim(y_mid - y_range/1.8, y_mid + y_range/1.8)
            
            # Get current time since start
            current_time = time.time() - self.start_time
            
            # Update x-axis to show sliding window
            x_min = max(0, current_time - self.time_window)
            x_max = current_time + 0.5  # Add small margin to the right
            
            self.ax.set_xlim(x_min, x_max)
            
            # Update title with current data rate
            if len(self.times) > 10:
                data_rate = len(self.times) / (self.times[-1] - self.times[0])
                self.ax.set_title(f'Arduino Data (Real-time) - {data_rate:.1f} Hz')
        
        return self.line,
    
    def run(self):
        # Find and connect to Arduino
        port = self.find_arduino_port()
        if not port:
            print("No Arduino found!")
            return
        
        print(f"Connecting to Arduino on port {port}")
        self.serial_port = serial.Serial(port, 115200, timeout=0.01)  # Short timeout for responsiveness
        self.serial_port.reset_input_buffer()
        self.start_time = time.time()
        
        # Create plot
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.ax.set_title('Arduino Data (Real-time)')
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('Value')
        self.ax.grid(True)
        
        # Create a line that will be updated
        self.line, = self.ax.plot([], [], 'b-', linewidth=2)
        
        # Initial axes limits
        self.ax.set_xlim(0, self.time_window)
        self.ax.set_ylim(0, 100)  # Initial range, will auto-adjust
        
        try:
            # Set up animation - faster update rate
            self.animation = FuncAnimation(
                self.fig, 
                self.update_plot, 
                interval=10,  # Update every 10ms (100 fps) for smoother display
                blit=True
            )
            
            # Show the plot - this blocks until the window is closed
            plt.show()
            
        finally:
            if self.serial_port:
                self.serial_port.close()
            print("Arduino reader closed")

# Run the application
if __name__ == "__main__":
    reader = ArduinoReader()
    reader.run() 