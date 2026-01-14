"""
Advanced Traffic Control System - Complete Production Software
==============================================================

A comprehensive, intelligent traffic management system featuring:
- Real-time adaptive traffic light control
- Emergency vehicle priority routing
- Weather-based timing adjustments
- Anomaly detection and predictive analytics
- Data persistence and reporting
- Performance monitoring
- GUI interface

Author: Traffic Control Systems Inc.
Version: 2.0.0
"""

import random
import json
import statistics
import uuid
import logging
import csv
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Tuple, Dict, Optional, Any
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time

####################
# Configuration
####################

DEFAULT_CONFIG = {
    "system": {
        "name": "Advanced Traffic Control System",
        "version": "2.0.0",
        "auto_save_interval": 60,
        "log_level": "INFO"
    },
    "intersections": {
        "default_green_time": 10.0,
        "default_yellow_time": 3.0,
        "default_pre_green_time": 1.5,
        "default_red_time": 10.0,
        "max_green_time": 35.0,
        "min_green_time": 3.0,
        "pedestrian_crossing_time": 15.0,
        "max_cars_per_lane": 4
    },
    "sensors": {
        "anomaly_threshold": 2.0,
        "history_size": 100,
        "update_interval": 1.0
    },
    "emergency": {
        "priority_multiplier": 2.0,
        "route_optimization": True
    },
    "reporting": {
        "export_format": "json",
        "report_interval": 300
    }
}

####################
# Enums
####################

class TrafficLightState(Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    PRE_GREEN = "PRE_GREEN"
    FLASHING_RED = "FLASHING_RED"
    FLASHING_YELLOW = "FLASHING_YELLOW"

class VehicleType(Enum):
    CAR = "CAR"
    JEEP = "JEEP"
    TRUCK = "TRUCK"
    BUS = "BUS"
    MOTORCYCLE = "MOTORCYCLE"
    EMERGENCY = "EMERGENCY"
    PEDESTRIAN = "PEDESTRIAN"

class EmergencyLevel(Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class WeatherCondition(Enum):
    CLEAR = "CLEAR"
    RAIN = "RAIN"
    SNOW = "SNOW"
    FOG = "FOG"
    STORM = "STORM"
    NIGHT = "NIGHT"

class Scenario(Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"
    RUSH_HOUR = "RUSH_HOUR"
    HEAVY_RAIN = "HEAVY_RAIN"
    SNOW_BLIZZARD = "SNOW_BLIZZARD"
    DENSE_FOG = "DENSE_FOG"
    POWER_OUTAGE = "POWER_OUTAGE"
    PEDESTRIAN_SCRAMBLE = "PEDESTRIAN_SCRAMBLE"

class SystemStatus(Enum):
    NORMAL = "NORMAL"
    MAINTENANCE = "MAINTENANCE"
    EMERGENCY = "EMERGENCY"
    FAILURE = "FAILURE"

class Direction(Enum):
    """Direction of travel at intersection"""
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"
    UNKNOWN = "UNKNOWN"

####################
# Data Classes
####################

@dataclass
class Vehicle:
    """Represents a vehicle in the traffic system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: VehicleType = VehicleType.CAR
    speed: float = 0.0  # km/h
    position: Tuple[float, float] = (0.0, 0.0)
    destination: Tuple[float, float] = (0.0, 0.0)
    priority: int = 0
    emergency_level: EmergencyLevel = EmergencyLevel.NONE
    direction: Direction = Direction.UNKNOWN  # Direction of travel
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'type': self.type.value,
            'speed': self.speed,
            'position': self.position,
            'destination': self.destination,
            'priority': self.priority,
            'emergency_level': self.emergency_level.value,
            'direction': self.direction.value,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class TrafficSensor:
    """Represents a traffic sensor monitoring vehicle flow"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    position: Tuple[float, float] = (0.0, 0.0)
    vehicle_count: int = 0
    average_speed: float = 0.0  # km/h
    queue_length: int = 0
    last_update: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'position': self.position,
            'vehicle_count': self.vehicle_count,
            'average_speed': self.average_speed,
            'queue_length': self.queue_length,
            'last_update': self.last_update.isoformat(),
            'is_active': self.is_active
        }

@dataclass
class IntersectionConfig:
    """Configuration for a traffic intersection"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    position: Tuple[float, float] = (0.0, 0.0)
    roads: List[str] = field(default_factory=list)
    default_green_time: float = 30.0
    default_yellow_time: float = 5.0
    default_pre_green_time: float = 1.5
    default_red_time: float = 30.0
    max_green_time: float = 60.0
    min_green_time: float = 10.0
    pedestrian_crossing_time: float = 20.0
    emergency_override: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)

####################
# Logging Manager
####################

class LoggingManager:
    """Manages system-wide logging"""
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        log_file = self.log_dir / f"traffic_system_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("TrafficControlSystem")
        self.logger.info("Logging system initialized")
    
    def log_event(self, level: str, message: str, **kwargs):
        """Log an event with additional context"""
        log_message = f"{message} | {kwargs}" if kwargs else message
        getattr(self.logger, level.lower())(log_message)
    
    def get_recent_logs(self, lines: int = 100) -> List[str]:
        """Get recent log entries"""
        log_file = self.log_dir / f"traffic_system_{datetime.now().strftime('%Y%m%d')}.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                return f.readlines()[-lines:]
        return []

####################
# Configuration Manager
####################

class ConfigurationManager:
    """Manages system configuration"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    return self.config
            except Exception as e:
                logging.error(f"Failed to load config: {e}")
        return self.config
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            return False
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value
    
    def set(self, key_path: str, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value

####################
# Data Persistence Manager
####################

class DataPersistenceManager:
    """Handles saving and loading system state"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def save_system_state(self, system_data: Dict, filename: str = None) -> bool:
        """Save complete system state"""
        if filename is None:
            filename = f"system_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.data_dir / filename
        try:
            with open(filepath, 'w') as f:
                json.dump(system_data, f, indent=2, default=str)
            logging.info(f"System state saved to {filepath}")
            return True
        except Exception as e:
            logging.error(f"Failed to save system state: {e}")
            return False
    
    def load_system_state(self, filename: str) -> Optional[Dict]:
        """Load system state from file"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            logging.error(f"State file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            logging.info(f"System state loaded from {filepath}")
            return data
        except Exception as e:
            logging.error(f"Failed to load system state: {e}")
            return None
    
    def export_analytics(self, analytics_data: List[Dict], format: str = "json") -> bool:
        """Export analytics data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == "json":
            filename = f"analytics_{timestamp}.json"
            filepath = self.data_dir / filename
            try:
                with open(filepath, 'w') as f:
                    json.dump(analytics_data, f, indent=2, default=str)
                logging.info(f"Analytics exported to {filepath}")
                return True
            except Exception as e:
                logging.error(f"Failed to export analytics: {e}")
                return False
        
        elif format == "csv":
            filename = f"analytics_{timestamp}.csv"
            filepath = self.data_dir / filename
            try:
                if analytics_data:
                    keys = analytics_data[0].keys()
                    with open(filepath, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=keys)
                        writer.writeheader()
                        writer.writerows(analytics_data)
                    logging.info(f"Analytics exported to {filepath}")
                    return True
            except Exception as e:
                logging.error(f"Failed to export analytics: {e}")
                return False
        
        return False

####################
# Performance Monitor
####################

class PerformanceMonitor:
    """Monitors system performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'total_steps': 0,
            'total_vehicles_processed': 0,
            'emergency_responses': 0,
            'anomalies_detected': 0,
            'average_response_time': 0.0,
            'system_uptime': 0.0
        }
        self.start_time = datetime.now()
        self.step_times = []
    
    def track_step(self, step_duration: float):
        """Track step execution time"""
        self.step_times.append(step_duration)
        if len(self.step_times) > 1000:
            self.step_times = self.step_times[-1000:]
        self.metrics['total_steps'] += 1
    
    def update_metric(self, metric_name: str, value):
        """Update a specific metric"""
        if metric_name in self.metrics:
            self.metrics[metric_name] = value
    
    def increment_metric(self, metric_name: str, amount: int = 1):
        """Increment a metric counter"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += amount
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of all metrics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        avg_step_time = statistics.mean(self.step_times) if self.step_times else 0
        
        return {
            **self.metrics,
            'system_uptime': uptime,
            'average_step_time': avg_step_time,
            'steps_per_second': self.metrics['total_steps'] / uptime if uptime > 0 else 0
        }
    
    def check_system_health(self) -> Dict:
        """Check system health status"""
        metrics = self.get_metrics_summary()
        health_status = {
            'status': 'HEALTHY',
            'issues': []
        }
        
        if metrics['average_step_time'] > 1.0:
            health_status['issues'].append("High step execution time")
            health_status['status'] = 'WARNING'
        
        if metrics['anomalies_detected'] > 100:
            health_status['issues'].append("High anomaly count")
            health_status['status'] = 'WARNING'
        
        return health_status

####################
# Report Generator
####################

class ReportGenerator:
    """Generates traffic reports and analytics"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_traffic_report(self, system_data: Dict) -> str:
        """Generate comprehensive traffic report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
{'='*80}
TRAFFIC CONTROL SYSTEM REPORT
{'='*80}
Generated: {timestamp}

SYSTEM STATUS
-------------
Status: {system_data.get('system_status', 'UNKNOWN')}
Weather: {system_data.get('weather', 'UNKNOWN')}
Active Intersections: {system_data.get('intersection_count', 0)}
Active Sensors: {system_data.get('sensor_count', 0)}
Active Emergencies: {system_data.get('active_emergencies', 0)}

TRAFFIC ANALYTICS
-----------------
Total Vehicles: {system_data.get('analytics', {}).get('total_vehicles', 0)}
Average Speed: {system_data.get('analytics', {}).get('average_speed', 0):.1f} km/h
Congestion Level: {system_data.get('analytics', {}).get('congestion_level', 0)*100:.1f}%
Anomalies Detected: {len(system_data.get('analytics', {}).get('anomalies', []))}

PERFORMANCE METRICS
-------------------
Total Steps: {system_data.get('performance', {}).get('total_steps', 0)}
System Uptime: {system_data.get('performance', {}).get('system_uptime', 0):.1f}s
Average Step Time: {system_data.get('performance', {}).get('average_step_time', 0):.4f}s

{'='*80}
"""
        return report
    
    def save_report(self, report: str, filename: str = None) -> bool:
        """Save report to file"""
        if filename is None:
            filename = f"traffic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        filepath = self.output_dir / filename
        try:
            with open(filepath, 'w') as f:
                f.write(report)
            logging.info(f"Report saved to {filepath}")
            return True
        except Exception as e:
            logging.error(f"Failed to save report: {e}")
            return False

####################
# Advanced Traffic Light
####################

class AdvancedTrafficLight:
    """Advanced traffic light with adaptive timing"""
    
    def __init__(self, intersection_id: str, config: IntersectionConfig):
        self.intersection_id = intersection_id
        self.config = config
        self.current_state = TrafficLightState.RED
        self.state_start_time = 0
        self.green_time_elapsed = 0.0
        self.cycle_count = 0
        self.emergency_active = False
        self.last_state_change = 0
        self.traffic_patterns = {}
        self.adaptation_factor = 1.0
    
    def get_current_state_duration(self, current_step: int) -> float:
        """Get duration of current state"""
        return current_step - self.state_start_time
    
    def change_state(self, new_state: TrafficLightState, current_step: int):
        """Change traffic light state"""
        logging.debug(f"Intersection {self.intersection_id}: {self.current_state.value} -> {new_state.value}")
        self.current_state = new_state
        self.state_start_time = current_step
        self.last_state_change = current_step
        if self.current_state == TrafficLightState.GREEN:
            self.green_time_elapsed = 0.0
            self.cycle_count += 1
    
    def calculate_optimal_timing(self, sensor_data: List[TrafficSensor],
                                 weather: WeatherCondition,
                                 emergency_level: EmergencyLevel,
                                 is_rush_hour: bool = False,
                                 is_night: bool = False) -> Dict[str, float]:
        """Calculate optimal timing based on conditions, synchronized with HTML formula"""
        # Base timings from config
        timing = {
            'green': self.config.default_green_time,
            'yellow': self.config.default_yellow_time,
            'pre_green': self.config.default_pre_green_time,
            'red': self.config.default_red_time
        }
        
        if emergency_level != EmergencyLevel.NONE:
            timing['green'] = self.config.min_green_time
            self.emergency_active = True
        else:
            self.emergency_active = False
        
        # Density-based logic from HTML: 3.0s base + 3.5s per car
        if sensor_data:
            avg_vehicle_count = sum(sensor.vehicle_count for sensor in sensor_data) / len(sensor_data)
            # Match HTML: this.dynamicDuration = Math.min(CONFIG.MAX_PHASE_DURATION, 3.0 + (dens * 3.5));
            timing['green'] = 3.0 + (avg_vehicle_count * 3.5)
            
            # Weather-based addition from HTML: if (this.isRaining || this.isSnowing) this.dynamicDuration += 4.0;
            if weather in [WeatherCondition.RAIN, WeatherCondition.SNOW, WeatherCondition.STORM]:
                timing['green'] += 4.0
            
            # Rush hour multiplier (HTML slightly slows flux in rush hour)
            if is_rush_hour:
                timing['green'] *= 1.2
            
            # Night adjustment (usually less green time if empty, but HTML doesn't explicitly change timing for night, just visuals)
            if is_night:
                timing['green'] *= 0.8
        
        # Apply bounds
        timing['green'] = max(self.config.min_green_time,
                             min(self.config.max_green_time, timing['green']))
        
        return timing

    def update_state(self, current_step: int, sensor_data: List[TrafficSensor],
                     weather: WeatherCondition,
                     emergency_level: EmergencyLevel,
                     power_outage: bool = False,
                     is_scramble: bool = False,
                     is_rush_hour: bool = False):
        """Update traffic light state with system-wide scenario support"""
        
        # Scenario: Power Outage (Flashing Yellow)
        if power_outage:
            # Flash yellow every 2 steps
            if current_step % 2 == 0:
                self.current_state = TrafficLightState.FLASHING_YELLOW
            else:
                self.current_state = TrafficLightState.RED
            return

        # Scenario: Pedestrian Scramble (All Red)
        if is_scramble:
            self.current_state = TrafficLightState.RED
            self.state_start_time = current_step
            return

        # Emergency override
        if emergency_level != EmergencyLevel.NONE:
            if self.current_state != TrafficLightState.GREEN:
                self.change_state(TrafficLightState.GREEN, current_step)
            return

        timing = self.calculate_optimal_timing(sensor_data, weather, emergency_level, is_rush_hour, weather == WeatherCondition.NIGHT)
        current_duration = self.get_current_state_duration(current_step)
        
        if self.current_state == TrafficLightState.RED:
            if current_duration >= timing['red']:
                self.change_state(TrafficLightState.PRE_GREEN, current_step)
        elif self.current_state == TrafficLightState.PRE_GREEN:
            if current_duration >= timing['pre_green']:
                self.change_state(TrafficLightState.GREEN, current_step)
        elif self.current_state == TrafficLightState.GREEN:
            self.green_time_elapsed = current_duration
            if current_duration >= timing['green']:
                self.change_state(TrafficLightState.YELLOW, current_step)
        elif self.current_state == TrafficLightState.YELLOW or self.current_state == TrafficLightState.FLASHING_YELLOW:
            if current_duration >= timing['yellow']:
                self.change_state(TrafficLightState.RED, current_step)
        
        self._update_adaptation_factor(sensor_data)
    
    def _update_adaptation_factor(self, sensor_data: List[TrafficSensor]):
        """Update adaptation factor based on queue lengths"""
        if not sensor_data:
            return
        
        total_queue_length = sum(sensor.queue_length for sensor in sensor_data)
        avg_queue_length = total_queue_length / len(sensor_data) if sensor_data else 0
        
        if avg_queue_length > 5:
            self.adaptation_factor = min(2.0, self.adaptation_factor + 0.01)
        elif avg_queue_length < 2:
            self.adaptation_factor = max(0.5, self.adaptation_factor - 0.01)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'intersection_id': self.intersection_id,
            'current_state': self.current_state.value,
            'cycle_count': self.cycle_count,
            'adaptation_factor': self.adaptation_factor
        }

####################
# Traffic Monitoring System
####################

class TrafficMonitoringSystem:
    """Monitors and analyzes traffic patterns"""
    
    def __init__(self):
        self.sensor_data_history: Dict[str, List[TrafficSensor]] = {}
        self.anomaly_threshold = 2.0
    
    def process_sensor_data(self, sensors: List[TrafficSensor]) -> Dict[str, Any]:
        """Process sensor data and detect anomalies"""
        processed_data = {
            'total_vehicles': 0,
            'average_speed': 0.0,
            'congestion_level': 0.0,
            'anomalies': [],
            'predictions': {}
        }
        
        if not sensors:
            return processed_data
        
        total_vehicles = sum(sensor.vehicle_count for sensor in sensors)
        active_sensors = [s for s in sensors if s.is_active]
        
        if active_sensors:
            average_speed = sum(sensor.average_speed for sensor in active_sensors) / len(active_sensors)
            avg_queue_length = sum(sensor.queue_length for sensor in active_sensors) / len(active_sensors)
            
            processed_data['total_vehicles'] = total_vehicles
            processed_data['average_speed'] = average_speed
            processed_data['congestion_level'] = min(1.0, avg_queue_length / 10.0)
        
        anomalies = self._detect_anomalies(sensors)
        processed_data['anomalies'] = anomalies
        
        self._update_history(sensors)
        
        return processed_data
    
    def _detect_anomalies(self, sensors: List[TrafficSensor]) -> List[Dict]:
        """Detect traffic anomalies using statistical analysis"""
        anomalies = []
        for sensor in sensors:
            if sensor.id not in self.sensor_data_history:
                self.sensor_data_history[sensor.id] = []
            
            history = self.sensor_data_history[sensor.id]
            
            if len(history) < 5:
                continue
            
            vehicle_counts = [s.vehicle_count for s in history[-10:]]
            if vehicle_counts:
                mean_count = statistics.mean(vehicle_counts)
                if len(vehicle_counts) > 1:
                    stdev_count = statistics.stdev(vehicle_counts)
                    if stdev_count > 0:
                        z_score = abs(sensor.vehicle_count - mean_count) / stdev_count
                        if z_score > self.anomaly_threshold:
                            anomalies.append({
                                'sensor_id': sensor.id,
                                'type': 'vehicle_count',
                                'value': sensor.vehicle_count,
                                'expected_range': (mean_count - 2*stdev_count, mean_count + 2*stdev_count),
                                'timestamp': sensor.last_update
                            })
        
        return anomalies
    
    def _update_history(self, sensors: List[TrafficSensor]):
        """Update sensor history"""
        for sensor in sensors:
            if sensor.id not in self.sensor_data_history:
                self.sensor_data_history[sensor.id] = []
            self.sensor_data_history[sensor.id].append(sensor)
            if len(self.sensor_data_history[sensor.id]) > 100:
                self.sensor_data_history[sensor.id] = self.sensor_data_history[sensor.id][-100:]

####################
# Emergency Management System
####################

class EmergencyManagementSystem:
    """Manages emergency vehicles and priority routing"""
    
    def __init__(self):
        self.active_emergencies: Dict[str, Vehicle] = {}
        self.priority_routes: Dict[str, List[str]] = {}
        self.weather_impact_factors = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.RAIN: 1.2,
            WeatherCondition.SNOW: 1.5,
            WeatherCondition.FOG: 1.8,
            WeatherCondition.STORM: 2.5
        }
    
    def register_emergency_vehicle(self, vehicle: Vehicle) -> bool:
        """Register an emergency vehicle"""
        if vehicle.emergency_level != EmergencyLevel.NONE:
            self.active_emergencies[vehicle.id] = vehicle
            logging.info(f"Emergency vehicle registered: {vehicle.id} - Level: {vehicle.emergency_level.value}")
            return True
        return False
    
    def unregister_emergency_vehicle(self, vehicle_id: str) -> bool:
        """Unregister an emergency vehicle"""
        if vehicle_id in self.active_emergencies:
            del self.active_emergencies[vehicle_id]
            logging.info(f"Emergency vehicle unregistered: {vehicle_id}")
            return True
        return False
    
    def calculate_priority(self, vehicle: Vehicle, weather: WeatherCondition) -> int:
        """Calculate vehicle priority"""
        priority_map = {
            EmergencyLevel.NONE: 0,
            EmergencyLevel.LOW: 1,
            EmergencyLevel.MEDIUM: 3,
            EmergencyLevel.HIGH: 7,
            EmergencyLevel.CRITICAL: 10
        }
        base_priority = priority_map.get(vehicle.emergency_level, 0)
        weather_factor = self.weather_impact_factors.get(weather, 1.0)
        if vehicle.type == VehicleType.EMERGENCY:
            base_priority += 5
        return int(base_priority * weather_factor)
    
    def get_highest_priority_vehicle(self) -> Optional[Vehicle]:
        """Get the highest priority emergency vehicle"""
        if not self.active_emergencies:
            return None
        return max(self.active_emergencies.values(),
                   key=lambda v: self.calculate_priority(v, WeatherCondition.CLEAR))
    
    def generate_priority_route(self, vehicle: Vehicle,
                                intersections: List[IntersectionConfig]) -> List[str]:
        """Generate priority route for emergency vehicle"""
        route = []
        for intersection in intersections[:3]:
            route.append(intersection.id)
        self.priority_routes[vehicle.id] = route
        logging.info(f"Priority route generated for {vehicle.id}: {route}")
        return route

####################
# Main Traffic Control System
####################

class InteractiveTrafficControlSystem:
    """Main traffic control system orchestrator"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.logging_manager = LoggingManager(
            log_level=self.config_manager.get('system.log_level', 'INFO')
        )
        self.persistence_manager = DataPersistenceManager()
        self.performance_monitor = PerformanceMonitor()
        self.report_generator = ReportGenerator()
        
        self.intersections: Dict[str, AdvancedTrafficLight] = {}
        self.sensors: Dict[str, TrafficSensor] = {}
        self.monitoring_system = TrafficMonitoringSystem()
        self.emergency_system = EmergencyManagementSystem()
        
        self.system_status = SystemStatus.NORMAL
        self.current_weather = WeatherCondition.CLEAR
        self.current_scenario = Scenario.DAY
        self.power_outage = False
        self.is_rush_hour = False
        self.is_pedestrian_scramble = False
        
        self.current_step = 0
        self.step_log = []
        
        self.logging_manager.log_event('INFO', 'Traffic Control System initialized')
    
    def add_intersection(self, config: IntersectionConfig):
        """Add a new intersection"""
        traffic_light = AdvancedTrafficLight(config.id, config)
        self.intersections[config.id] = traffic_light
        self.logging_manager.log_event('INFO', f'Intersection added: {config.id}')
    
    def add_sensor(self, sensor: TrafficSensor):
        """Add a new sensor"""
        self.sensors[sensor.id] = sensor
        self.logging_manager.log_event('INFO', f'Sensor added: {sensor.id}')
    
    def update_weather(self, weather: WeatherCondition):
        """Update weather conditions"""
        self.current_weather = weather
        self.logging_manager.log_event('INFO', f'Weather updated to: {weather.value}')

    def load_scenario(self, scenario: Scenario):
        """Load a predefined scenario, matching HTML behavior"""
        self.current_scenario = scenario
        self.power_outage = (scenario == Scenario.POWER_OUTAGE)
        self.is_rush_hour = (scenario == Scenario.RUSH_HOUR)
        self.is_pedestrian_scramble = (scenario == Scenario.PEDESTRIAN_SCRAMBLE)
        
        # Adjust configuration based on scenario
        if self.is_rush_hour:
            self.config_manager.set('intersections.max_cars_per_lane', 8)
            # In rush hour, cars might move slightly slower due to flux (matching HTML logic)
            self.logging_manager.log_event('INFO', "Rush Hour Scenario: Increased lane capacity.")
        else:
            self.config_manager.set('intersections.max_cars_per_lane', 4)

        if scenario == Scenario.HEAVY_RAIN:
            self.current_weather = WeatherCondition.RAIN
        elif scenario == Scenario.SNOW_BLIZZARD:
            self.current_weather = WeatherCondition.SNOW
        elif scenario == Scenario.DENSE_FOG:
            self.current_weather = WeatherCondition.FOG
        elif scenario == Scenario.NIGHT:
            self.current_weather = WeatherCondition.NIGHT
        else:
            self.current_weather = WeatherCondition.CLEAR

        if self.power_outage:
            self.system_status = SystemStatus.FAILURE
            self.logging_manager.log_event('WARNING', "Power Outage Scenario: Traffic lights set to flashing yellow.")
        else:
            self.system_status = SystemStatus.NORMAL

        self.logging_manager.log_event('INFO', f'Scenario loaded: {scenario.value}')
    
    def get_all_sensors(self) -> List[TrafficSensor]:
        """Get all sensors"""
        return list(self.sensors.values())
    
    def get_intersection(self, intersection_id: str) -> Optional[AdvancedTrafficLight]:
        """Get intersection by ID"""
        return self.intersections.get(intersection_id)
    
    def process_step(self) -> Dict:
        """Process one simulation step"""
        step_start = time.time()
        self.current_step += 1
        
        # Update sensors
        for sensor in self.sensors.values():
            sensor.vehicle_count = max(0, sensor.vehicle_count + random.randint(-2, 3))
            sensor.average_speed = max(5.0, min(80.0, sensor.average_speed + random.uniform(-5, 5)))
            sensor.queue_length = max(0, min(20, sensor.queue_length + random.randint(-1, 2)))
            sensor.last_update = datetime.now()
        
        sensors = self.get_all_sensors()
        analytics = self.monitoring_system.process_sensor_data(sensors)
        
        priority_vehicle = self.emergency_system.get_highest_priority_vehicle()
        emergency_level = priority_vehicle.emergency_level if priority_vehicle else EmergencyLevel.NONE
        
        # Update intersections
        for intersection in self.intersections.values():
            intersection.update_state(
                self.current_step, 
                sensors, 
                self.current_weather, 
                emergency_level,
                power_outage=self.power_outage,
                is_scramble=self.is_pedestrian_scramble,
                is_rush_hour=self.is_rush_hour
            )
        
        # Update metrics
        self.performance_monitor.update_metric('total_vehicles_processed', analytics['total_vehicles'])
        if analytics['anomalies']:
            self.performance_monitor.increment_metric('anomalies_detected', len(analytics['anomalies']))
        
        step_info = {
            'step': self.current_step,
            'timestamp': datetime.now(),
            'system_status': self.system_status.value,
            'weather': self.current_weather.value,
            'analytics': analytics,
            'intersection_states': {
                iid: {
                    'state': light.current_state.value,
                    'duration': light.get_current_state_duration(self.current_step),
                    'cycle_count': light.cycle_count
                } for iid, light in self.intersections.items()
            },
            'active_emergencies': len(self.emergency_system.active_emergencies)
        }
        
        self.step_log.append(step_info)
        if len(self.step_log) > 1000:
            self.step_log = self.step_log[-1000:]
        
        step_duration = time.time() - step_start
        self.performance_monitor.track_step(step_duration)
        
        return step_info
    
    def handle_emergency_vehicle(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Handle emergency vehicle registration"""
        registered = self.emergency_system.register_emergency_vehicle(vehicle)
        
        if not registered:
            return {'success': False, 'message': 'Vehicle is not an emergency vehicle'}
        
        priority = self.emergency_system.calculate_priority(vehicle, self.current_weather)
        intersections = list(self.intersections.values())
        config_list = [i.config for i in intersections]
        route = self.emergency_system.generate_priority_route(vehicle, config_list)
        
        vehicle.priority = priority
        self.performance_monitor.increment_metric('emergency_responses')
        
        return {
            'success': True,
            'vehicle_id': vehicle.id,
            'priority': priority,
            'route': route,
            'message': f'Emergency vehicle {vehicle.id} registered with priority {priority}'
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        sensors = self.get_all_sensors()
        analytics = self.monitoring_system.process_sensor_data(sensors)
        performance = self.performance_monitor.get_metrics_summary()
        health = self.performance_monitor.check_system_health()
        
        return {
            'step': self.current_step,
            'system_status': self.system_status.value,
            'weather': self.current_weather.value,
            'analytics': analytics,
            'intersection_count': len(self.intersections),
            'sensor_count': len(sensors),
            'active_emergencies': len(self.emergency_system.active_emergencies),
            'performance': performance,
            'health': health
        }
    
    def save_state(self, filename: str = None) -> bool:
        """Save system state"""
        state_data = {
            'timestamp': datetime.now().isoformat(),
            'system_status': self.get_system_status(),
            'intersections': [light.to_dict() for light in self.intersections.values()],
            'sensors': [sensor.to_dict() for sensor in self.sensors.values()],
            'step_log': self.step_log[-100:]
        }
        return self.persistence_manager.save_system_state(state_data, filename)
    
    def export_analytics(self, format: str = "json") -> bool:
        """Export analytics data"""
        return self.persistence_manager.export_analytics(self.step_log, format)
    
    def generate_report(self) -> str:
        """Generate traffic report"""
        system_data = self.get_system_status()
        return self.report_generator.generate_traffic_report(system_data)

####################
# GUI Application
####################

class TrafficControlGUI:
    """GUI interface for traffic control system"""
    
    def __init__(self, system: InteractiveTrafficControlSystem):
        self.system = system
        self.root = tk.Tk()
        self.root.title("Advanced Traffic Control System v2.0")
        self.root.geometry("1000x700")
        
        self.is_running = False
        self.simulation_thread = None
        
        self._create_widgets()
        self._update_display()
    
    def _create_widgets(self):
        """Create GUI widgets"""
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(title_frame, text="🚦 Advanced Traffic Control System",
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        # Control Panel
        control_frame = ttk.LabelFrame(self.root, text="Control Panel", padding="10")
        control_frame.grid(row=1, column=0, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.start_btn = ttk.Button(control_frame, text="▶ Start", command=self.start_simulation)
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏸ Stop", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.step_btn = ttk.Button(control_frame, text="⏭ Step", command=self.single_step)
        self.step_btn.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Weather:").grid(row=1, column=0, padx=5, pady=5)
        self.weather_var = tk.StringVar(value="CLEAR")
        weather_combo = ttk.Combobox(control_frame, textvariable=self.weather_var,
                                     values=[w.value for w in WeatherCondition])
        weather_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        weather_combo.bind('<<ComboboxSelected>>', self.change_weather)

        ttk.Label(control_frame, text="Scenario:").grid(row=2, column=0, padx=5, pady=5)
        self.scenario_var = tk.StringVar(value="DAY")
        scenario_combo = ttk.Combobox(control_frame, textvariable=self.scenario_var,
                                      values=[s.value for s in Scenario])
        scenario_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        scenario_combo.bind('<<ComboboxSelected>>', self.change_scenario)
        
        ttk.Button(control_frame, text="🚨 Add Emergency", command=self.add_emergency).grid(row=3, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(control_frame, text="💾 Save State", command=self.save_state).grid(row=4, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(control_frame, text="📊 Generate Report", command=self.generate_report).grid(row=5, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(control_frame, text="📤 Export Analytics", command=self.export_analytics).grid(row=6, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        # Status Display
        status_frame = ttk.LabelFrame(self.root, text="System Status", padding="10")
        status_frame.grid(row=1, column=1, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.status_text = tk.Text(status_frame, height=20, width=50, font=('Courier', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(status_frame, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        # Metrics Display
        metrics_frame = ttk.LabelFrame(self.root, text="Performance Metrics", padding="10")
        metrics_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        self.metrics_text = tk.Text(metrics_frame, height=8, font=('Courier', 9))
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
    
    def _update_display(self):
        """Update display with current system status"""
        status = self.system.get_system_status()
        
        # Update status text
        self.status_text.delete(1.0, tk.END)
        status_info = f"""
Step: {status['step']}
System Status: {status['system_status']}
Scenario: {self.system.current_scenario.value}
Weather: {status['weather']}
Active Emergencies: {status['active_emergencies']}

Traffic Analytics:
  Total Vehicles: {status['analytics']['total_vehicles']}
  Average Speed: {status['analytics']['average_speed']:.1f} km/h
  Congestion: {status['analytics']['congestion_level']*100:.1f}%
  Anomalies: {len(status['analytics']['anomalies'])}

Intersections:
"""
        self.status_text.insert(1.0, status_info)
        
        # Add intersection states
        for iid, light in self.system.intersections.items():
            state_emoji = {
                'RED': '🔴',
                'YELLOW': '🟡',
                'PRE_GREEN': '🔴🟡',
                'GREEN': '🟢'
            }.get(light.current_state.value, '⚪')
            
            self.status_text.insert(tk.END, f"  {iid}: {state_emoji} {light.current_state.value}\n")
        
        # Update metrics
        self.metrics_text.delete(1.0, tk.END)
        metrics = status['performance']
        metrics_info = f"""
Total Steps: {metrics['total_steps']}
Uptime: {metrics['system_uptime']:.1f}s
Avg Step Time: {metrics['average_step_time']:.4f}s
Steps/Second: {metrics['steps_per_second']:.2f}
Vehicles Processed: {metrics['total_vehicles_processed']}
Emergency Responses: {metrics['emergency_responses']}
Anomalies Detected: {metrics['anomalies_detected']}
"""
        self.metrics_text.insert(1.0, metrics_info)
        
        if self.is_running:
            self.root.after(1000, self._update_display)
    
    def start_simulation(self):
        """Start continuous simulation"""
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        def run_simulation():
            while self.is_running:
                self.system.process_step()
                time.sleep(0.5)
        
        self.simulation_thread = threading.Thread(target=run_simulation, daemon=True)
        self.simulation_thread.start()
        self._update_display()
    
    def stop_simulation(self):
        """Stop simulation"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def single_step(self):
        """Execute single simulation step"""
        self.system.process_step()
        self._update_display()
    
    def change_weather(self, event=None):
        """Change weather condition"""
        weather = WeatherCondition[self.weather_var.get()]
        self.system.update_weather(weather)
        # messagebox.showinfo("Weather Updated", f"Weather changed to {weather.value}")
    
    def change_scenario(self, event=None):
        """Change system scenario"""
        scenario = Scenario[self.scenario_var.get()]
        self.system.load_scenario(scenario)
        # Synchronize weather combo
        self.weather_var.set(self.system.current_weather.value)
        # messagebox.showinfo("Scenario Loaded", f"Scenario changed to {scenario.value}")
    
    def add_emergency(self):
        """Add emergency vehicle"""
        vehicle = Vehicle(
            type=VehicleType.EMERGENCY,
            emergency_level=EmergencyLevel.HIGH,
            position=(random.uniform(0, 300), random.uniform(0, 300)),
            destination=(random.uniform(0, 300), random.uniform(0, 300))
        )
        result = self.system.handle_emergency_vehicle(vehicle)
        messagebox.showinfo("Emergency Vehicle", result['message'])
        self._update_display()
    
    def save_state(self):
        """Save system state"""
        if self.system.save_state():
            messagebox.showinfo("Success", "System state saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save system state")
    
    def generate_report(self):
        """Generate and display report"""
        report = self.system.generate_report()
        
        report_window = tk.Toplevel(self.root)
        report_window.title("Traffic Report")
        report_window.geometry("800x600")
        
        text_widget = tk.Text(report_window, font=('Courier', 9))
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, report)
        
        ttk.Button(report_window, text="Save Report",
                  command=lambda: self.system.report_generator.save_report(report)).pack(pady=5)
    
    def export_analytics(self):
        """Export analytics data"""
        if self.system.export_analytics("json"):
            messagebox.showinfo("Success", "Analytics exported successfully!")
        else:
            messagebox.showerror("Error", "Failed to export analytics")
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

####################
# Helper Functions
####################

def create_sample_setup() -> InteractiveTrafficControlSystem:
    """Create sample traffic system"""
    system = InteractiveTrafficControlSystem()
    
    # Create intersections
    for i in range(2):
        for j in range(2):
            intersection = IntersectionConfig(
                id=f"intersection_{i}_{j}",
                position=(i * 150.0, j * 150.0),
                roads=[f"Road {i}-{j}A", f"Road {i}-{j}B"],
                default_green_time=25.0,
                default_yellow_time=4.0,
                default_red_time=25.0,
                max_green_time=45.0,
                min_green_time=8.0
            )
            system.add_intersection(intersection)
    
    # Create sensors
    for i in range(2):
        for j in range(2):
            for k in range(2):
                sensor = TrafficSensor(
                    id=f"sensor_{i}_{j}_{k}",
                    position=(i * 150.0 + k * 30.0, j * 150.0 + k * 25.0),
                    vehicle_count=random.randint(5, 15),
                    average_speed=random.uniform(20.0, 50.0),
                    queue_length=random.randint(1, 8),
                    is_active=True
                )
                system.add_sensor(sensor)
    
    return system

def visualize_system_state(system: InteractiveTrafficControlSystem, step_info: Dict):
    """Text-based visualization"""
    print("\n" + "="*60)
    print("TRAFFIC CONTROL SYSTEM - STEP {}".format(step_info['step']))
    print("="*60)
    
    print(f"System Status: {step_info['system_status']}")
    print(f"Weather Condition: {step_info['weather']}")
    print(f"Active Emergencies: {step_info['active_emergencies']}")
    
    analytics = step_info['analytics']
    print(f"\nTraffic Analytics:")
    print(f"  Total Vehicles: {analytics['total_vehicles']}")
    print(f"  Average Speed: {analytics['average_speed']:.1f} km/h")
    print(f"  Congestion Level: {analytics['congestion_level']*100:.1f}%")
    print(f"  Anomalies Detected: {len(analytics['anomalies'])}")
    
    print(f"\nIntersection States:")
    for iid, state_info in step_info['intersection_states'].items():
        duration = state_info['duration']
        state = state_info['state']
        cycle = state_info['cycle_count']
        
        state_color = {
            'RED': '[RED]',
            'YELLOW': '[YELLOW]',
            'PRE_GREEN': '[READY]',
            'GREEN': '[GREEN]',
        }.get(state, f'[{state}]')
        
        print(f"  {iid}: {state_color} ({duration:.1f}s) - Cycle #{cycle}")
    
    print("="*60)

def console_demo():
    """Run console-based demo"""
    print("[*] Starting Traffic Control System Console Demo")
    
    system = create_sample_setup()
    print(f"[OK] Created system with {len(system.intersections)} intersections and {len(system.sensors)} sensors")
    
    print("\n[*] Running simulation steps...")
    for i in range(10):
        step_info = system.process_step()
        if i % 2 == 0:
            visualize_system_state(system, step_info)
        time.sleep(0.5)
    
    print("\n[EMERGENCY] Adding emergency vehicle...")
    emergency_vehicle = Vehicle(
        type=VehicleType.EMERGENCY,
        emergency_level=EmergencyLevel.HIGH,
        position=(50.0, 50.0),
        destination=(300.0, 300.0)
    )
    result = system.handle_emergency_vehicle(emergency_vehicle)
    print(f"[OK] {result['message']}")
    
    for i in range(5):
        step_info = system.process_step()
        visualize_system_state(system, step_info)
        time.sleep(0.5)
    
    print("\n[*] Generating final report...")
    report = system.generate_report()
    print(report)
    
    print("\n[*] Saving system state...")
    system.save_state()
    
    print("\n[*] Exporting analytics...")
    system.export_analytics("json")
    
    print("\n[SUCCESS] Demo completed successfully!")

####################
# Main Entry Point
####################

if __name__ == "__main__":
    import sys
    import webbrowser
    import os

    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    print("=" * 60)
    print("  ADVANCED TRAFFIC CONTROL SYSTEM v2.0")
    print("=" * 60)
    print("\nChoose interface mode:")
    print("1. 3D Simulation Mode (Competition Edition)")
    print("2. Console Analytics Mode")
    
    try:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == "1":
            print("\n[*] Launching 3D Traffic Simulation Engine...")
            
            # Target HTML file path
            html_path = r"d:\DOCUMENTS\Sigma Web Development Course\Traffic Control System\TRAFFIC_AI_PRO_SUBMISSION\TrafficSystem3D_COMPETITION.html"
            
            if os.path.exists(html_path):
                print(f"[*] Opening: {html_path}")
                webbrowser.open(f'file:///{html_path}')
                print("[SUCCESS] Simulation launched in default browser.")
                print("Press standard browser controls (F11) for full screen.")
            else:
                print(f"\n[ERROR] Simulation file not found at:\n{html_path}")
                print("Please ensure the file exists or check the path.")
                
        elif choice == "2":
            print("\n[*] Starting console mode...")
            console_demo()
        else:
            print("\n[!] Invalid choice. Launching Simulation by default...")
            html_path = r"d:\DOCUMENTS\Sigma Web Development Course\Traffic Control System\TRAFFIC_AI_PRO_SUBMISSION\TrafficSystem3D_COMPETITION.html"
            if os.path.exists(html_path):
                webbrowser.open(f'file:///{html_path}')
                
    except KeyboardInterrupt:
        print("\n\n[*] System shutdown requested. Goodbye!")
    except Exception as e:
        logging.error(f"System error: {e}")
        print(f"\n[ERROR] {e}")