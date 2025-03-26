import serial
import serial.tools.list_ports

class ArduinoReader:
    
    
    def find_arduino_port(self):
        """Find the Arduino port by checking available serial ports"""
        print("Checking available ports...")

        ports = list(serial.tools.list_ports.comports())
        print(ports)
        
        for port in ports:
            print(f"Found port: {port.device} - {port.description}")
            # Check for common Arduino identifiers in the description or device name
            if any(identifier in port.description.lower() for identifier in 
                    ['arduino', 'ch340', 'usb serial', 'usb2.0-serial', 'usb2.0-s', 'iobusbhostdevice']) or \
                any(identifier in port.device.lower() for identifier in 
                    ['usbmodem', 'usbserial', 'tty.usbmodem', 'tty.usbserial']):
                print(f"Found Arduino on port: {port.device}")
                return port.device
        
        print("No Arduino found on any port")
        return None