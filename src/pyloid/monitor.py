from PySide6.QtGui import QScreen
from typing import Optional, Callable, Any

class Monitor():
    def __init__(self, index: int, screen: QScreen):
        """
        Constructor for the Monitor class.

        Parameters
        ----------
        index : int
            Index of the monitor.
        screen : QScreen
            QScreen object of the monitor.
        """
        super().__init__()
        self.index = index
        self.screen = screen

    def capture(self, save_path: str, x: Optional[int] = None, y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None):
        """
        Captures the entire desktop screen.

        Parameters
        ----------
        save_path : str
            Path to save the captured image. If not specified, it will be saved in the current directory.
        x : int, optional
            x-coordinate of the area to capture. Default is None.
        y : int, optional
            y-coordinate of the area to capture. Default is None.
        width : int, optional
            Width of the area to capture. Default is None.
        height : int, optional
            Height of the area to capture. Default is None.

        Returns
        -------
        str or None
            Returns the path of the saved image. Returns None if an error occurs.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        save_path = monitor.capture("screenshot.png")
        print(f"Screenshot saved at: {save_path}")
        ```
        """
        try:    
            screenshot = self.screen.grabWindow(0, x, y, width, height)
            screenshot.save(save_path)
            return save_path
        
        except Exception as e:
            print(f"Error occurred while capturing the desktop: {e}")
            return None

    def info(self) -> dict[str, Any]:
        """
        Returns information about the monitor.

        Returns
        -------
        dict[str, Any]
            A dictionary containing monitor information.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        info = monitor.info()
        print("Monitor Info:", info)
        ```

        Output Example
        --------------
        ```
        {
            "index": 0,
            "name": "Primary Monitor",
            "manufacturer": "Dell",
            "model": "U2718Q",
            "serial_number": "SN123456789",
            "x": 0,
            "y": 0,
            "width": 2560,
            "height": 1440,
            "is_primary": True,
            "geometry": {
                "x": 0,
                "y": 0,
                "width": 2560,
                "height": 1440,
            },    
            "size": {
                "width": 2560,
                "height": 1440,
            },
            "available_geometry": {
                "x": 0,
                "y": 0,
                "width": 2560,
                "height": 1400,
            },
            "available_size": {
                "width": 2560,
                "height": 1400,
            },
            "virtual_geometry":{
                "x": 0,
                "y": 0,
                "width": 5120,
                "height": 1440,
            },
            "virtual_size": {
                "width": 5120,
                "height": 1440,
            },
            "available_virtual_geometry": {
                "x": 0,
                "y": 0,
                "width": 5120,
                "height": 1400,
            },
            "available_virtual_size": {
                "width": 5120,
                "height": 1400,
            },
            "physical_size": {
                "width": 600,
                "height": 340,
            },
            "depth": 24,
            "device_pixel_ratio": 1.0,
            "logical_dots_per_inch": 96.0,
            "logical_dots_per_inch_x": 96.0,
            "logical_dots_per_inch_y": 96.0,
            "orientation": "Landscape",
            "physical_dots_per_inch": 109.0,
            "physical_dots_per_inch_x": 109.0,
            "physical_dots_per_inch_y": 109.0,
            "refresh_rate": 60.0, 
        }
        ```
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
        Checks if the monitor is the primary monitor.

        Returns
        -------
        bool
            Returns True if the monitor is the primary monitor, otherwise False.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_all_monitors()[1]
        is_primary = monitor.is_primary()
        print(f"Is primary monitor: {is_primary}") # False
        ```
        """
        return self.index == 0
    
    def size(self) -> dict[str, int]:
        """
        Returns the size of the monitor.

        Returns
        -------
        dict[str, int]
            A dictionary containing the width and height of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        size = monitor.size()
        print("Monitor Size:", size)
        ```
        """
        monitor = self.screen
        return {
                    "width": monitor.size().width(),
                    "height": monitor.size().height(),
                },

    def geometry(self) -> dict[str, int]:
        """
        Returns the geometry of the monitor.

        Returns
        -------
        dict[str, int]
            A dictionary containing the x and y coordinates, width, and height of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        geometry = monitor.geometry()
        print("Monitor Geometry:", geometry)
        ```
        """
        monitor = self.screen
        return {
            "x": monitor.geometry().x(),    
            "y": monitor.geometry().y(),
            "width": monitor.geometry().width(),
            "height": monitor.geometry().height(),
        }
    
    def available_geometry(self) -> dict[str, int]:
        """
        Returns the available geometry of the monitor.

        The available geometry refers to the portion of the monitor's geometry that is not occupied by system UI elements such as taskbars or docks.

        Returns
        -------
        dict[str, int]
            A dictionary containing the x and y coordinates, width, and height of the available geometry.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        available_geometry = monitor.available_geometry()
        print("Available Geometry:", available_geometry)
        ```
        """
        monitor = self.screen
        return {
            "x": monitor.availableGeometry().x(),
            "y": monitor.availableGeometry().y(),
            "width": monitor.availableGeometry().width(),
            "height": monitor.availableGeometry().height(),
        }
    
    def available_size(self) -> dict[str, int]:
        """
        Returns the available size of the monitor.

        The available size refers to the portion of the monitor's size that is not occupied by system UI elements such as taskbars or docks.

        Returns
        -------
        dict[str, int]
            A dictionary containing the width and height of the available size.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        available_size = monitor.available_size()
        print("Available Size:", available_size)
        ```
        """
        monitor = self.screen
        return {
            "width": monitor.availableSize().width(),
            "height": monitor.availableSize().height(),
        }
    
    def virtual_geometry(self) -> dict[str, int]:
        """
        Returns the virtual geometry of the monitor.

        The virtual geometry refers to the combined geometry of all monitors in a multi-monitor setup.

        Returns
        -------
        dict[str, int]
            A dictionary containing the x and y coordinates, width, and height of the virtual geometry.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        virtual_geometry = monitor.virtual_geometry()
        print("Virtual Geometry:", virtual_geometry)
        ```
        """
        monitor = self.screen
        return {
            "x": monitor.virtualGeometry().x(),
            "y": monitor.virtualGeometry().y(),
            "width": monitor.virtualGeometry().width(),
            "height": monitor.virtualGeometry().height(),
        }
    
    def virtual_size(self) -> dict[str, int]:
        """
        Returns the virtual size of the monitor.

        The virtual size refers to the combined size of all monitors in a multi-monitor setup.

        Returns
        -------
        dict[str, int]
            A dictionary containing the width and height of the virtual size.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        virtual_size = monitor.virtual_size()
        print("Virtual Size:", virtual_size)
        ```
        """
        monitor = self.screen
        return {
            "width": monitor.virtualSize().width(),
            "height": monitor.virtualSize().height(),
        }
    
    def available_virtual_geometry(self) -> dict[str, int]:
        """
        Returns the available virtual geometry of the monitor.

        The available virtual geometry refers to the portion of the virtual geometry that is not occupied by system UI elements such as taskbars or docks.

        Returns
        -------
        dict[str, int]
            A dictionary containing the x and y coordinates, width, and height of the available virtual geometry.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        available_virtual_geometry = monitor.available_virtual_geometry()
        print("Available Virtual Geometry:", available_virtual_geometry)
        ```
        """
        monitor = self.screen
        return {
            "x": monitor.availableVirtualGeometry().x(),
            "y": monitor.availableVirtualGeometry().y(),
            "width": monitor.availableVirtualGeometry().width(),
            "height": monitor.availableVirtualGeometry().height(),
        }
    
    def available_virtual_size(self) -> dict[str, int]:
        """
        Returns the available virtual size of the monitor.

        The available virtual size refers to the portion of the virtual size that is not occupied by system UI elements such as taskbars or docks.

        Returns
        -------
        dict[str, int]
            A dictionary containing the width and height of the available virtual size.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        available_virtual_size = monitor.available_virtual_size()
        print("Available Virtual Size:", available_virtual_size)
        ```
        """
        monitor = self.screen
        return {
            "width": monitor.availableVirtualSize().width(),
            "height": monitor.availableVirtualSize().height(),
        }
    
    def physical_size(self) -> dict[str, float]:
        """
        Returns the physical size of the monitor.

        The physical size refers to the actual physical dimensions of the monitor.

        Returns
        -------
        dict[str, float]
            A dictionary containing the width and height of the physical size.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        physical_size = monitor.physical_size()
        print("Physical Size:", physical_size)
        ```
        """
        monitor = self.screen
        return {
            "width": monitor.physicalSize().width(),
            "height": monitor.physicalSize().height(),
        }
    
    def depth(self) -> int:
        """
        Returns the depth of the monitor.

        The depth refers to the color depth of the monitor, which is the number of bits used to represent the color of a single pixel.

        Returns
        -------
        int
            The color depth of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        depth = monitor.depth()
        print("Color Depth:", depth)
        ```
        """
        monitor = self.screen
        return monitor.depth()      
    
    def device_pixel_ratio(self) -> float:
        """
        Returns the device pixel ratio of the monitor.

        The device pixel ratio is the ratio between physical pixels and device-independent pixels (DIPs).

        Returns
        -------
        float
            The device pixel ratio of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        device_pixel_ratio = monitor.device_pixel_ratio()
        print("Device Pixel Ratio:", device_pixel_ratio)
        ```
        """
        monitor = self.screen
        return monitor.devicePixelRatio()
    
    def logical_dots_per_inch(self) -> float:
        """
        Returns the logical dots per inch (DPI) of the monitor.

        The logical DPI is the number of device-independent pixels (DIPs) per inch.

        Returns
        -------
        float
            The logical DPI of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        logical_dpi = monitor.logical_dots_per_inch()
        print("Logical DPI:", logical_dpi)
        ```
        """
        monitor = self.screen   
        return monitor.logicalDotsPerInch()
    
    def logical_dots_per_inch_x(self) -> float:
        """
        Returns the logical dots per inch (DPI) along the X axis of the monitor.

        The logical DPI along the X axis is the number of device-independent pixels (DIPs) per inch along the horizontal axis.

        Returns
        -------
        float
            The logical DPI along the X axis of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        logical_dpi_x = monitor.logical_dots_per_inch_x()
        print("Logical DPI X:", logical_dpi_x)
        ```
        """
        monitor = self.screen
        return monitor.logicalDotsPerInchX()
    
    def logical_dots_per_inch_y(self) -> float:
        """
        Returns the logical dots per inch (DPI) along the Y axis of the monitor.

        The logical DPI along the Y axis is the number of device-independent pixels (DIPs) per inch along the vertical axis.

        Returns
        -------
        float
            The logical DPI along the Y axis of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        logical_dpi_y = monitor.logical_dots_per_inch_y()
        print("Logical DPI Y:", logical_dpi_y)
        ```
        """
        monitor = self.screen
        return monitor.logicalDotsPerInchY()
    
    def orientation(self) -> str:
        """
        Returns the orientation of the monitor.

        The orientation refers to the current orientation of the monitor, such as landscape or portrait.

        Returns
        -------
        str
            The orientation of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        orientation = monitor.orientation()
        print("Orientation:", orientation)
        ```
        """
        monitor = self.screen
        return monitor.orientation().name
    
    def physical_dots_per_inch(self) -> float:
        """
        Returns the physical dots per inch (DPI) of the monitor.

        The physical DPI is the number of physical pixels per inch.

        Returns
        -------
        float
            The physical DPI of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        physical_dpi = monitor.physical_dots_per_inch()
        print("Physical DPI:", physical_dpi)
        ```
        """
        monitor = self.screen
        return monitor.physicalDotsPerInch()
    
    def physical_dots_per_inch_x(self) -> float:
        """
        Returns the physical dots per inch (DPI) along the X axis of the monitor.

        The physical DPI along the X axis is the number of physical pixels per inch along the horizontal axis.

        Returns
        -------
        float
            The physical DPI along the X axis of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        physical_dpi_x = monitor.physical_dots_per_inch_x()
        print("Physical DPI X:", physical_dpi_x)
        ```
        """
        monitor = self.screen
        return monitor.physicalDotsPerInchX()
    
    def physical_dots_per_inch_y(self) -> float:
        """
        Returns the physical dots per inch (DPI) along the Y axis of the monitor.

        The physical DPI along the Y axis is the number of physical pixels per inch along the vertical axis.

        Returns
        -------
        float
            The physical DPI along the Y axis of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        physical_dpi_y = monitor.physical_dots_per_inch_y()
        print("Physical DPI Y:", physical_dpi_y)
        ```
        """
        monitor = self.screen
        return monitor.physicalDotsPerInchY()
    
    def refresh_rate(self) -> float:
        """
        Returns the refresh rate of the monitor.

        The refresh rate is the number of times the monitor updates with new information per second, measured in Hertz (Hz).

        Returns
        -------
        float
            The refresh rate of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        refresh_rate = monitor.refresh_rate()
        print("Refresh Rate:", refresh_rate)
        ```
        """
        monitor = self.screen
        return monitor.refreshRate()
    
    def manufacturer(self) -> str:
        """
        Returns the manufacturer of the monitor.

        The manufacturer refers to the company that produced the monitor.

        Returns
        -------
        str
            The manufacturer of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        manufacturer = monitor.manufacturer()
        print("Manufacturer:", manufacturer)
        ```
        """
        monitor = self.screen
        return monitor.manufacturer()
    
    def model(self) -> str:
        """
        Returns the model of the monitor.

        The model refers to the specific model name or number assigned by the manufacturer.

        Returns
        -------
        str
            The model of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        model = monitor.model()
        print("Model:", model)
        ```
        """
        monitor = self.screen
        return monitor.model()
    
    def name(self) -> str:
        """
        Returns the name of the monitor.

        The name refers to the user-friendly name assigned to the monitor.

        Returns
        -------
        str
            The name of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        name = monitor.name()
        print("Name:", name)
        ```
        """
        monitor = self.screen
        return monitor.name()
    
    def serial_number(self) -> str:
        """
        Returns the serial number of the monitor.

        The serial number is a unique identifier assigned to the monitor by the manufacturer.

        Returns
        -------
        str
            The serial number of the monitor.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        monitor = app.get_primary_monitor()
        serial_number = monitor.serial_number()
        print("Serial Number:", serial_number)
        ```
        """
        monitor = self.screen
        return monitor.serialNumber()
    
    def geometry_changed(self, callback: Callable):
        """
        Registers a callback for the event that occurs when the geometry of the monitor changes.

        Parameters
        ----------
        callback : Callable
            The function to be called when the geometry changes.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        def on_geometry_changed():
            print("Geometry changed!")

        monitor = app.get_primary_monitor()
        monitor.geometry_changed(on_geometry_changed)
        ```
        """
        monitor = self.screen
        monitor.geometryChanged.connect(callback)

    def orientation_changed(self, callback: Callable):
        """
        Registers a callback for the event that occurs when the orientation of the monitor changes.

        Parameters
        ----------
        callback : Callable
            The function to be called when the orientation changes.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        def on_orientation_changed():
            print("Orientation changed!")

        monitor = app.get_primary_monitor()
        monitor.orientation_changed(on_orientation_changed)
        ```
        """
        monitor = self.screen
        monitor.orientationChanged.connect(callback)

    def refresh_rate_changed(self, callback: Callable):
        """
        Registers a callback for the event that occurs when the refresh rate of the monitor changes.

        Parameters
        ----------
        callback : Callable
            The function to be called when the refresh rate changes.

        Examples
        --------
        ```python
        app = Pyloid("Pyloid-App")

        def on_refresh_rate_changed():
            print("Refresh rate changed!")

        monitor = app.get_primary_monitor()
        monitor.refresh_rate_changed(on_refresh_rate_changed)
        ```
        """
        monitor = self.screen
        monitor.refreshRateChanged.connect(callback)

