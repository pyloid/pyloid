from PySide6.QtGui import QScreen
from typing import Optional, Callable

class Monitor():
    def __init__(self, index: int, screen: QScreen):
        super().__init__()
        self.index = index
        self.screen = screen

    def capture(self, save_path: str, x: Optional[int] = None, y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None):
        """
        Captures the entire desktop screen.
        
        :param save_path: Path to save the captured image. If not specified, it will be saved in the current directory.
        :return: Path of the saved image
        """
        try:    
            screenshot = self.screen.grabWindow(0, x, y, width, height)
            screenshot.save(save_path)
            return save_path
        
        except Exception as e:
            print(f"Error occurred while capturing the desktop: {e}")
            return None

    def info(self):
        """
        Returns monitor information.
        
        :return: Dictionary containing monitor information
        """
        monitor = self.screen

        monitor_data = {
                "index": self.index,
                "name": monitor.name(),
                "manufacturer": monitor.manufacturer(),
                "model": monitor.model(),
                "serial_number": monitor.serialNumber(),
                "x": monitor.geometry().x(),
                "y": monitor.geometry().y(),
                "width": monitor.size().width(),
                "height": monitor.size().height(),
                "is_primary": self.is_primary(),
                "geometry": {
                    "x": monitor.geometry().x(),
                    "y": monitor.geometry().y(),
                    "width": monitor.geometry().width(),
                    "height": monitor.geometry().height(),
                },    
                "size": {
                    "width": monitor.size().width(),
                    "height": monitor.size().height(),
                },
                "available_geometry": {
                    "x": monitor.availableGeometry().x(),
                    "y": monitor.availableGeometry().y(),
                    "width": monitor.availableGeometry().width(),
                    "height": monitor.availableGeometry().height(),
                },
                "available_size": {
                    "width": monitor.availableSize().width(),
                    "height": monitor.availableSize().height(),
                },
                "virtual_geometry":{
                    "x": monitor.virtualGeometry().x(),
                    "y": monitor.virtualGeometry().y(),
                    "width": monitor.virtualGeometry().width(),
                    "height": monitor.virtualGeometry().height(),
                },
                "virtual_size": {
                    "width": monitor.virtualSize().width(),
                    "height": monitor.virtualSize().height(),
                },
                "available_virtual_geometry": {
                    "x": monitor.availableVirtualGeometry().x(),
                    "y": monitor.availableVirtualGeometry().y(),
                    "width": monitor.availableVirtualGeometry().width(),
                    "height": monitor.availableVirtualGeometry().height(),
                },
                "available_virtual_size": {
                    "width": monitor.availableVirtualSize().width(),
                    "height": monitor.availableVirtualSize().height(),
                },
                "physical_size": {
                    "width": monitor.physicalSize().width(),
                    "height": monitor.physicalSize().height(),
                },
                "depth": monitor.depth(),
                "device_pixel_ratio": monitor.devicePixelRatio(),
                "logical_dots_per_inch": monitor.logicalDotsPerInch(),
                "logical_dots_per_inch_x": monitor.logicalDotsPerInchX(),
                "logical_dots_per_inch_y": monitor.logicalDotsPerInchY(),
                "orientation": monitor.orientation().name,
                "physical_dots_per_inch": monitor.physicalDotsPerInch(),
                "physical_dots_per_inch_x": monitor.physicalDotsPerInchX(),
                "physical_dots_per_inch_y": monitor.physicalDotsPerInchY(),
                "refresh_rate": monitor.refreshRate(), 
        }

        return monitor_data
    
    def is_primary(self) -> bool:
        """
        Checks if the given monitor is the primary monitor.
        
        :return: True if the primary monitor, False otherwise
        """
        return self.index == 0
    
    def size(self) -> dict:
        """
        Returns the size of the monitor.
        
        :return: Size of the monitor
        """
        monitor = self.screen
        return {
                    "width": monitor.size().width(),
                    "height": monitor.size().height(),
                },

    def geometry(self) -> dict:
        """
        Returns the geometry of the monitor.
        
        :return: Geometry of the monitor
        """
        monitor = self.screen
        return {
            "x": monitor.geometry().x(),    
            "y": monitor.geometry().y(),
            "width": monitor.geometry().width(),
            "height": monitor.geometry().height(),
        }
    
    def available_geometry(self) -> dict:
        """
        Returns the available geometry of the monitor.
        
        :return: Available geometry of the monitor
        """
        monitor = self.screen
        return {
            "x": monitor.availableGeometry().x(),
            "y": monitor.availableGeometry().y(),
            "width": monitor.availableGeometry().width(),
            "height": monitor.availableGeometry().height(),
        }
    
    def available_size(self) -> dict:
        """
        Returns the available size of the monitor.
        
        :return: Available size of the monitor
        """
        monitor = self.screen
        return {
            "width": monitor.availableSize().width(),
            "height": monitor.availableSize().height(),
        }
    
    def virtual_geometry(self) -> dict:
        """
        Returns the virtual geometry of the monitor.
        
        :return: Virtual geometry of the monitor
        """
        monitor = self.screen
        return {
            "x": monitor.virtualGeometry().x(),
            "y": monitor.virtualGeometry().y(),
            "width": monitor.virtualGeometry().width(),
            "height": monitor.virtualGeometry().height(),
        }
    
    def virtual_size(self) -> dict:
        """
        Returns the virtual size of the monitor.
        
        :return: Virtual size of the monitor
        """
        monitor = self.screen
        return {
            "width": monitor.virtualSize().width(),
            "height": monitor.virtualSize().height(),
        }
    
    def available_virtual_geometry(self) -> dict:
        """
        Returns the available virtual geometry of the monitor.
        
        :return: Available virtual geometry of the monitor
        """
        monitor = self.screen
        return {
            "x": monitor.availableVirtualGeometry().x(),
            "y": monitor.availableVirtualGeometry().y(),
            "width": monitor.availableVirtualGeometry().width(),
            "height": monitor.availableVirtualGeometry().height(),
        }
    
    def available_virtual_size(self) -> dict:
        """
        Returns the available virtual size of the monitor.
        
        :return: Available virtual size of the monitor
        """
        monitor = self.screen
        return {
            "width": monitor.availableVirtualSize().width(),
            "height": monitor.availableVirtualSize().height(),
        }
    
    def physical_size(self) -> dict:
        """
        Returns the physical size of the monitor.
        
        :return: Physical size of the monitor
        """
        monitor = self.screen
        return {
            "width": monitor.physicalSize().width(),
            "height": monitor.physicalSize().height(),
        }
    
    def depth(self) -> int:
        """
        Returns the depth of the monitor.
        
        :return: Depth of the monitor
        """
        monitor = self.screen
        return monitor.depth()      
    
    def device_pixel_ratio(self) -> float:
        """
        Returns the device pixel ratio of the monitor.
        
        :return: Device pixel ratio of the monitor
        """
        monitor = self.screen
        return monitor.devicePixelRatio()
    
    def logical_dots_per_inch(self) -> float:
        """
        Returns the logical dots per inch of the monitor.
        
        :return: Logical dots per inch of the monitor
        """
        monitor = self.screen   
        return monitor.logicalDotsPerInch()
    
    def logical_dots_per_inch_x(self) -> float:
        """
        Returns the logical dots per inch X of the monitor.
        
        :return: Logical dots per inch X of the monitor
        """ 
        monitor = self.screen
        return monitor.logicalDotsPerInchX()
    
    def logical_dots_per_inch_y(self) -> float:
        """
        Returns the logical dots per inch Y of the monitor.
        
        :return: Logical dots per inch Y of the monitor
        """
        monitor = self.screen
        return monitor.logicalDotsPerInchY()
    
    def orientation(self) -> str:
        """
        Returns the orientation of the monitor.
        
        :return: Orientation of the monitor
        """ 
        monitor = self.screen
        return monitor.orientation().name
    
    def physical_dots_per_inch(self) -> float:
        """
        Returns the physical dots per inch of the monitor.
        
        :return: Physical dots per inch of the monitor
        """
        monitor = self.screen
        return monitor.physicalDotsPerInch()
    
    def physical_dots_per_inch_x(self) -> float:
        """
        Returns the physical dots per inch X of the monitor.
        
        :return: Physical dots per inch X of the monitor
        """
        monitor = self.screen
        return monitor.physicalDotsPerInchX()
    
    def physical_dots_per_inch_y(self) -> float:
        """
        Returns the physical dots per inch Y of the monitor.
        
        :return: Physical dots per inch Y of the monitor
        """
        monitor = self.screen
        return monitor.physicalDotsPerInchY()
    
    def refresh_rate(self) -> float:
        """
        Returns the refresh rate of the monitor.
        
        :return: Refresh rate of the monitor
        """
        monitor = self.screen
        return monitor.refreshRate()
    
    def manufacturer(self) -> str:
        """
        Returns the manufacturer of the monitor.
        
        :return: Manufacturer of the monitor
        """
        monitor = self.screen
        return monitor.manufacturer()
    
    def model(self) -> str:
        """
        Returns the model of the monitor.
        
        :return: Model of the monitor
        """
        monitor = self.screen
        return monitor.model()
    
    def name(self) -> str:
        """
        Returns the name of the monitor.
        
        :return: Name of the monitor
        """
        monitor = self.screen
        return monitor.name()
    
    def serial_number(self) -> str:
        """
        Returns the serial number of the monitor.
        
        :return: Serial number of the monitor
        """
        monitor = self.screen
        return monitor.serialNumber()
    
    def geometry_changed(self, callback: Callable):
        """
        Returns the event that occurs when the geometry of the monitor changes.
        """
        monitor = self.screen
        monitor.geometryChanged.connect(callback)

    def orientation_changed(self, callback: Callable):
        """
        Returns the event that occurs when the orientation of the monitor changes.
        """
        monitor = self.screen
        monitor.orientationChanged.connect(callback)

    def refresh_rate_changed(self, callback: Callable):
        """
        Returns the event that occurs when the refresh rate of the monitor changes.
        """
        monitor = self.screen
        monitor.refreshRateChanged.connect(callback)
