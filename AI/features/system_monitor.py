"""
System Monitor Module for Secure Intelligent Desktop Assistant
Real-time system monitoring: CPU, RAM, Disk, Battery
"""

import psutil
import logging
import platform
from pathlib import Path
import sys
import time

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class SystemMonitor:
    """
    Real-time System Monitoring
    Tracks CPU, RAM, Disk, and Battery usage
    """
    
    def __init__(self):
        """Initialize system monitor"""
        self.logger = logging.getLogger('DesktopAssistant.SystemMonitor')
        self.cpu_warning = config.CPU_WARNING_THRESHOLD
        self.ram_warning = config.RAM_WARNING_THRESHOLD
        self.disk_warning = config.DISK_WARNING_THRESHOLD
        self.battery_warning = config.BATTERY_WARNING_THRESHOLD
        
        self.logger.info("System Monitor initialized")
    
    def get_cpu_usage(self, interval=1):
        """
        Get CPU usage percentage
        
        Args:
            interval: Measurement interval in seconds
            
        Returns:
            CPU usage percentage
        """
        return psutil.cpu_percent(interval=interval)
    
    def get_cpu_info(self):
        """
        Get detailed CPU information
        
        Returns:
            Dictionary with CPU details
        """
        cpu_freq = psutil.cpu_freq()
        
        return {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'current_freq_mhz': cpu_freq.current if cpu_freq else None,
            'min_freq_mhz': cpu_freq.min if cpu_freq else None,
            'max_freq_mhz': cpu_freq.max if cpu_freq else None,
            'usage_per_core': psutil.cpu_percent(interval=0.1, percpu=True),
            'total_usage': psutil.cpu_percent(interval=0.1)
        }
    
    def get_memory_info(self):
        """
        Get memory/RAM information
        
        Returns:
            Dictionary with memory details
        """
        mem = psutil.virtual_memory()
        
        return {
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'percent': mem.percent,
            'free_gb': round(mem.free / (1024**3), 2)
        }
    
    def get_disk_info(self, drive='C:'):
        """
        Get disk usage information
        
        Args:
            drive: Drive letter to check
            
        Returns:
            Dictionary with disk details
        """
        try:
            disk = psutil.disk_usage(drive)
            
            return {
                'drive': drive,
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'percent': disk.percent
            }
        except Exception as e:
            self.logger.error(f"Error getting disk info: {e}")
            return None
    
    def get_battery_info(self):
        """
        Get battery information
        
        Returns:
            Dictionary with battery details
        """
        try:
            battery = psutil.sensors_battery()
            
            if battery is None:
                return None
            
            return {
                'percent': battery.percent,
                'charging': battery.power_plugged,
                'time_left_minutes': battery.secsleft / 60 if battery.secsleft > 0 else None,
                'status': 'Charging' if battery.power_plugged else 'Discharging'
            }
        except Exception as e:
            self.logger.debug(f"Battery info not available: {e}")
            return None
    
    def get_system_info(self):
        """
        Get general system information
        
        Returns:
            Dictionary with system details
        """
        boot_time = psutil.boot_time()
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'platform_release': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'boot_time': boot_time,
            'uptime_hours': round((time.time() - boot_time) / 3600, 2)
        }
    
    def get_all_status(self):
        """
        Get complete system status
        
        Returns:
            Dictionary with all system metrics
        """
        return {
            'cpu': {
                'usage_percent': self.get_cpu_usage(),
                'info': self.get_cpu_info()
            },
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'battery': self.get_battery_info(),
            'system': self.get_system_info()
        }
    
    def check_warnings(self):
        """
        Check for system warnings
        
        Returns:
            List of warning messages
        """
        warnings = []
        
        # CPU warning
        cpu_usage = self.get_cpu_usage()
        if cpu_usage > self.cpu_warning:
            warnings.append(f"High CPU usage: {cpu_usage}%")
        
        # RAM warning
        mem = psutil.virtual_memory()
        if mem.percent > self.ram_warning:
            warnings.append(f"High RAM usage: {mem.percent}%")
        
        # Disk warning
        disk = psutil.disk_usage('C:')
        if disk.percent > self.disk_warning:
            warnings.append(f"Low disk space: {disk.percent}% used")
        
        # Battery warning
        battery = psutil.sensors_battery()
        if battery and not battery.power_plugged and battery.percent < self.battery_warning:
            warnings.append(f"Low battery: {battery.percent}%")
        
        return warnings
    
    def get_health_report(self):
        """
        Get a comprehensive health report
        
        Returns:
            Dictionary with health status
        """
        cpu = self.get_cpu_usage()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('C:')
        battery = psutil.sensors_battery()
        
        # Determine overall health
        health_status = "Good"
        
        if cpu > 90 or mem.percent > 90 or disk.percent > 95:
            health_status = "Critical"
        elif cpu > 70 or mem.percent > 80 or disk.percent > 90:
            health_status = "Warning"
        
        # Generate spoken report
        report = {
            'status': health_status,
            'cpu': {
                'value': cpu,
                'status': 'high' if cpu > 70 else 'normal'
            },
            'memory': {
                'value': mem.percent,
                'status': 'high' if mem.percent > 70 else 'normal'
            },
            'disk': {
                'value': disk.percent,
                'status': 'low' if disk.percent > 90 else 'normal'
            },
            'battery': {
                'value': battery.percent if battery else None,
                'status': 'charging' if battery and battery.power_plugged else 'normal'
            }
        }
        
        return report
    
    def speak_health_report(self, voice_engine=None):
        """
        Speak the health report
        
        Args:
            voice_engine: Voice engine for TTS
            
        Returns:
            Spoken report text
        """
        health = self.get_health_report()
        
        report_text = f"System health is {health['status']}. "
        report_text += f"CPU usage is {health['cpu']['value']} percent. "
        report_text += f"Memory usage is {health['memory']['value']} percent. "
        report_text += f"Disk usage is {health['disk']['value']} percent. "
        
        if health['battery']['value'] is not None:
            if health['battery']['status'] == 'charging':
                report_text += f"Battery is {health['battery']['value']} percent and charging."
            else:
                report_text += f"Battery is at {health['battery']['value']} percent."
        
        # Add warnings
        warnings = self.check_warnings()
        if warnings:
            report_text += " Warning: " + ", ".join(warnings)
        
        if voice_engine:
            voice_engine.speak(report_text)
        
        return report_text
    
    def monitor_continuously(self, interval=5, callback=None):
        """
        Monitor system continuously
        
        Args:
            interval: Check interval in seconds
            callback: Function to call with status
            
        Returns:
            None (runs in infinite loop)
        """
        import threading
        
        def _monitor():
            while True:
                status = self.get_all_status()
                warnings = self.check_warnings()
                
                if callback:
                    callback(status, warnings)
                
                time.sleep(interval)
        
        thread = threading.Thread(target=_monitor, daemon=True)
        thread.start()
        
        return thread


# ============================================
# Main function for testing
# ============================================

def test_system_monitor():
    """Test system monitor"""
    print("Testing System Monitor...")
    
    monitor = SystemMonitor()
    
    # Get all status
    print("\n" + "="*60)
    print("System Status:")
    print("="*60)
    
    status = monitor.get_all_status()
    
    print(f"\nCPU Usage: {status['cpu']['usage_percent']}%")
    print(f"CPU Info: {status['cpu']['info']}")
    
    print(f"\nMemory: {status['memory']}")
    
    print(f"\nDisk: {status['disk']}")
    
    if status['battery']:
        print(f"\nBattery: {status['battery']}")
    else:
        print("\nBattery: Not available")
    
    print(f"\nSystem: {status['system']}")
    
    # Health report
    print("\n" + "="*60)
    print("Health Report:")
    print("="*60)
    
    health = monitor.get_health_report()
    print(f"Status: {health['status']}")
    
    # Warnings
    print("\nWarnings:")
    warnings = monitor.check_warnings()
    if warnings:
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("  No warnings")
    
    # Speak health report
    print("\n" + "="*60)
    print("Speaking health report...")
    print("="*60)
    
    report_text = monitor.speak_health_report()
    print(report_text)
    
    return monitor


if __name__ == "__main__":
    test_system_monitor()
