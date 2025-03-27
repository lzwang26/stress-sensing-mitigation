import cv2
import time
import numpy as np
import platform
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class VideoReader:
    def __init__(self, camera_id=0):
        """
        Initialize the video reader
        Args:
            camera_id (int): Camera device ID (default is 0 for built-in webcam)
        """
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.window_name = f'Video Feed (Camera {self.camera_id})'
        
        # PPG signal parameters
        self.ppg_values = []
        self.ppg_times = []  # Store timestamps for each PPG value
        self.max_points = 500  # Show last 500 points (10 seconds at 50Hz)
        self.start_time = None
        self.window_size = 10  # Size of the rolling window in seconds
        
        # Plot parameters
        self.fig = None
        self.ax = None
        self.line = None
        self.animation = None
        
    @staticmethod
    def list_cameras():
        """Test available cameras and return a list of working camera IDs."""
        print("Checking for available cameras...")
        available_cameras = []
        
        # On macOS, first try the standard indices
        if platform.system() == 'Darwin':
            print("macOS detected, checking camera indices...")
            # Try indices 0-3 first (most common on macOS)
            test_indices = list(range(4))
            # Then try some additional indices that might work for external cameras
            test_indices.extend([100, 101, 102, 103])  # Additional indices sometimes used by macOS
        else:
            # For other systems, just check 0-9
            test_indices = range(10)
        
        for i in test_indices:
            print(f"\nTesting camera index {i}...")
            cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # Get camera properties
                    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    
                    print(f"✓ Camera ID {i} is available:")
                    print(f"    Resolution: {width}x{height}")
                    print(f"    FPS: {fps}")
                    
                    # On macOS, try to get more camera information
                    if platform.system() == 'Darwin':
                        backend = cap.get(cv2.CAP_PROP_BACKEND)
                        print(f"    Backend: {backend}")
                        
                    available_cameras.append(i)
                else:
                    print(f"✗ Camera {i} opened but couldn't read frame")
                cap.release()
            else:
                print(f"✗ Could not open camera {i}")
        
        if not available_cameras:
            print("\nNo cameras were found!")
        else:
            print(f"\nFound {len(available_cameras)} camera(s): {available_cameras}")
            
        print("\nNote: On macOS:")
        print("- Camera ID 0 is usually the built-in webcam")
        print("- External cameras might use indices like 1, 2, 3 or 100, 101, 102")
        print("- If your external camera isn't detected, try:")
        print("  1. Unplugging and reconnecting the camera")
        print("  2. Checking System Preferences -> Security & Privacy -> Camera")
        print("  3. Closing other applications that might be using the camera")
        
        return available_cameras
    
    def test_camera(self):
        """Test the current camera by displaying its feed"""
        print(f"Testing camera ID {self.camera_id}...")
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print(f"Error: Could not open camera {self.camera_id}")
            return
        
        print("Camera opened successfully")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
                
            cv2.imshow(f'Camera {self.camera_id} Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
    def calculate_ppg(self, frame):
        """Calculate PPG signal from frame"""
        # Extract red channel (assuming BGR format)
        red_channel = frame[:, :, 2]
        
        # Calculate mean intensity of red channel
        ppg_value = np.mean(red_channel)
        
        # Store value and timestamp
        current_time = time.time()
        if self.start_time is None:
            self.start_time = current_time
        relative_time = current_time - self.start_time
        
        self.ppg_values.append(ppg_value)
        self.ppg_times.append(relative_time)
        
        # Keep only last max_points
        if len(self.ppg_values) > self.max_points:
            self.ppg_values.pop(0)
            self.ppg_times.pop(0)
            
        return ppg_value
    
    def update_plot(self, frame):
        """Update the PPG plot"""
        if self.ppg_values and self.ppg_times:
            # Update line data with time on x-axis
            self.line.set_data(self.ppg_times, self.ppg_values)
            
            # Update x-axis to show rolling window
            if len(self.ppg_times) > 0:
                current_time = self.ppg_times[-1]
                x_min = max(0, current_time - self.window_size)
                x_max = current_time + 0.1  # Add small margin
                self.ax.set_xlim(x_min, x_max)
            
            # Auto-scale y-axis
            if self.ppg_values:
                y_min = min(self.ppg_values) - 10
                y_max = max(self.ppg_values) + 10
                self.ax.set_ylim(y_min, y_max)
            
            # Update title with current data rate
            if len(self.ppg_values) > 10:
                data_rate = len(self.ppg_values) / (time.time() - self.start_time)
                self.ax.set_title(f'PPG Signal - {data_rate:.1f} Hz')
        
        return self.line,
    
    def start(self):
        try:
            print(f"\nInitializing camera {self.camera_id}...")
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.camera_id}")
                return

            # Get camera properties
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"Camera properties:")
            print(f"- Resolution: {width}x{height}")
            print(f"- FPS: {fps}")
            
            # Initialize FPS calculation
            frame_count = 0
            start_time = time.time()
            last_fps_print = time.time()
            current_fps = 0.0
            self.is_running = True
            self.start_time = time.time()  # Initialize start time for PPG
            
            # Initialize PPG plot
            self.fig, self.ax = plt.subplots(figsize=(12, 4))
            self.line, = self.ax.plot([], [], 'r-', linewidth=2)
            self.ax.set_title('PPG Signal')
            self.ax.set_xlabel('Time (seconds)')
            self.ax.set_ylabel('Intensity')
            self.ax.grid(True)
            
            # Set initial x-axis limits for rolling window
            self.ax.set_xlim(0, self.window_size)
            
            # Start animation
            self.animation = FuncAnimation(
                self.fig, 
                self.update_plot, 
                interval=10,  # Update every 10ms
                blit=True
            )
            
            # Show plot without blocking
            plt.show(block=False)

            print("Starting video capture...")
            print("Press 'q' to quit")
            
            while self.is_running:
                # Read frame
                ret, frame = self.cap.read()
                if not ret or frame is None or frame.size == 0:
                    print("Error: Failed to read frame")
                    break

                # Calculate PPG signal
                ppg_value = self.calculate_ppg(frame)

                # Calculate and print FPS every second
                frame_count += 1
                current_time = time.time()
                if current_time - last_fps_print >= 1.0:
                    elapsed_time = current_time - start_time
                    current_fps = frame_count / elapsed_time
                    print(f"Current FPS: {current_fps:.1f}")
                    last_fps_print = current_time
                    frame_count = 0
                    start_time = current_time

                # Add FPS and PPG value to frame
                cv2.putText(frame, f"FPS: {current_fps:.1f}", 
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                          1, (0, 255, 0), 2)
                cv2.putText(frame, f"PPG: {ppg_value:.1f}", 
                          (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                          1, (0, 255, 0), 2)

                # Show frame
                try:
                    cv2.imshow('Camera Feed', frame)
                except Exception as e:
                    print(f"Error displaying frame: {e}")
                    break

                # Check for 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Video capture stopped by user")
                    break

        except Exception as e:
            print(f"Error in video capture: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.close()

    def close(self):
        print("Cleaning up...")
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.is_running = False
        if self.animation:
            self.animation.event_source.stop()
        if self.fig:
            plt.close(self.fig)
        print("Video capture closed")


if __name__ == "__main__":
    video_reader = VideoReader()
    video_reader.start()