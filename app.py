"""
NetSentry - Cloud-Based Network Traffic Analysis System
Stage 1: Local REST API Service
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import defaultdict
import re
import subprocess
import socket
import platform
import psutil
import ipaddress
import os
import joblib
import pandas as pd
import numpy as np

# Initialize FastAPI app
app = FastAPI(
    title="NetSentry API",
    description="Network Anomaly Detection System",
    version="1.0.0"
)

# ============================================
# ML Model Loading
# ============================================

# Global variables for ML models
ml_models = {
    'binary': None,
    'multi': None,
    'encoders': None,
    'features': None,
    'attack_mapping': None
}

def load_ml_models():
    """Load trained Random Forest models and preprocessors"""
    models_dir = os.path.join(os.path.dirname(__file__), 'modelBuilding', 'models')
    
    try:
        if os.path.exists(models_dir):
            ml_models['binary'] = joblib.load(os.path.join(models_dir, 'rf_binary_classifier.pkl'))
            ml_models['multi'] = joblib.load(os.path.join(models_dir, 'rf_multiclass_classifier.pkl'))
            ml_models['encoders'] = joblib.load(os.path.join(models_dir, 'label_encoders.pkl'))
            ml_models['features'] = joblib.load(os.path.join(models_dir, 'feature_columns.pkl'))
            ml_models['attack_mapping'] = joblib.load(os.path.join(models_dir, 'attack_mapping.pkl'))
            print("✓ ML models loaded successfully")
            return True
        else:
            print(f"⚠ ML models directory not found: {models_dir}")
            return False
    except Exception as e:
        print(f"⚠ Failed to load ML models: {str(e)}")
        return False

# Load models on startup
models_loaded = load_ml_models()

# Configure CORS to allow frontend access
# Note: Using regex pattern to allow all localhost/127.0.0.1 origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:[0-9]+)?",
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ============================================
# Data Models
# ============================================

class NetworkLog(BaseModel):
    """Model for incoming network traffic log"""
    src_ip: str = Field(..., description="Source IP address")
    dst_ip: str = Field(..., description="Destination IP address")
    protocol: str = Field(..., description="Protocol (TCP, UDP, HTTP, DNS)")
    payload: Optional[str] = Field(None, description="Payload data or log message")
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @validator('src_ip', 'dst_ip')
    def validate_ip(cls, v):
        """Basic IP validation"""
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', v):
            raise ValueError(f'Invalid IP address format: {v}')
        return v
    
    @validator('protocol')
    def validate_protocol(cls, v):
        """Validate protocol type"""
        valid_protocols = ['TCP', 'UDP', 'HTTP', 'DNS', 'HTTPS']
        if v.upper() not in valid_protocols:
            raise ValueError(f'Protocol must be one of {valid_protocols}')
        return v.upper()


class Alert(BaseModel):
    """Model for security alerts"""
    alert_id: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    alert_type: str
    description: str
    src_ip: str
    dst_ip: str
    protocol: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = {}


class AnalysisResponse(BaseModel):
    """Response model for /analyze endpoint"""
    status: str
    alerts: List[Alert]
    message: str


class HealthResponse(BaseModel):
    """Response model for /health endpoint"""
    status: str
    timestamp: str
    version: str


class NetworkInterface(BaseModel):
    """Model for network interface information"""
    name: str
    ip_address: Optional[str] = None
    netmask: Optional[str] = None
    mac_address: Optional[str] = None
    speed_mbps: Optional[int] = None
    is_up: bool
    mtu: Optional[int] = None
    bytes_sent: Optional[int] = None
    bytes_recv: Optional[int] = None


class NetworkDevice(BaseModel):
    """Model for discovered network devices"""
    ip: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    vendor: Optional[str] = None
    status: str  # up, down
    open_ports: List[int] = []


class NetworkScanReport(BaseModel):
    """Response model for network scan endpoint"""
    status: str
    scan_timestamp: str
    local_ip: str
    network_range: str
    gateway: Optional[str] = None
    dns_servers: List[str] = []
    interfaces: List[NetworkInterface]
    discovered_devices: List[NetworkDevice]
    network_metrics: Dict[str, Any]
    recommendations: List[str] = []


class MLFeatures(BaseModel):
    """Model for ML prediction input features (KDDCUP'99 format)"""
    duration: float = 0
    protocol_type: str = "tcp"
    service: str = "http"
    flag: str = "SF"
    src_bytes: float = 0
    dst_bytes: float = 0
    land: int = 0
    wrong_fragment: int = 0
    urgent: int = 0
    hot: int = 0
    num_failed_logins: int = 0
    logged_in: int = 0
    num_compromised: int = 0
    root_shell: int = 0
    su_attempted: int = 0
    num_root: int = 0
    num_file_creations: int = 0
    num_shells: int = 0
    num_access_files: int = 0
    num_outbound_cmds: int = 0
    is_host_login: int = 0
    is_guest_login: int = 0
    count: int = 0
    srv_count: int = 0
    serror_rate: float = 0.0
    srv_serror_rate: float = 0.0
    rerror_rate: float = 0.0
    srv_rerror_rate: float = 0.0
    same_srv_rate: float = 0.0
    diff_srv_rate: float = 0.0
    srv_diff_host_rate: float = 0.0
    dst_host_count: int = 0
    dst_host_srv_count: int = 0
    dst_host_same_srv_rate: float = 0.0
    dst_host_diff_srv_rate: float = 0.0
    dst_host_same_src_port_rate: float = 0.0
    dst_host_srv_diff_host_rate: float = 0.0
    dst_host_serror_rate: float = 0.0
    dst_host_srv_serror_rate: float = 0.0
    dst_host_rerror_rate: float = 0.0
    dst_host_srv_rerror_rate: float = 0.0


class MLPredictionResponse(BaseModel):
    """Response model for ML prediction endpoints"""
    status: str
    model_available: bool
    prediction: Optional[str] = None
    prediction_label: Optional[str] = None
    confidence: Optional[float] = None
    probabilities: Optional[Dict[str, float]] = None
    message: str
    timestamp: str


# ============================================
# In-Memory Storage (for Stage 1)
# ============================================

# Store all alerts
alerts_database: List[Alert] = []

# Track login attempts per IP (for rate limiting detection)
login_attempts: Dict[str, List[str]] = defaultdict(list)

# Suspicious IP blacklist
SUSPICIOUS_IPS = {
    '192.168.100.100',
    '10.0.0.666',  # Obviously fake but for demo
    '172.16.0.100',
    '203.0.113.0',  # TEST-NET-3 (RFC 5737)
}

# Suspicious DNS patterns   
SUSPICIOUS_DNS_PATTERNS = [
    r'\.ru$',  # Russian TLD
    r'\.tk$',  # Free TLD often used for malicious purposes
    r'malware',
    r'phishing',
    r'botnet',
    r'c2server',
    r'[a-f0-9]{32,}',  # Long hex strings (possible C2 communication)
]

# HTTP suspicious patterns
HTTP_SUSPICIOUS_KEYWORDS = [
    'login',
    'admin',
    'password',
    'auth',
    'signin',
    'authenticate'
]


# ============================================
# Anomaly Detection Logic
# ============================================

def generate_alert_id() -> str:
    """Generate unique alert ID"""
    return f"ALERT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{len(alerts_database) + 1}"


def check_suspicious_ip(log: NetworkLog) -> Optional[Alert]:
    """
    Rule 1: Check if source IP is in suspicious IP list
    """
    if log.src_ip in SUSPICIOUS_IPS:
        return Alert(
            alert_id=generate_alert_id(),
            severity="HIGH",
            alert_type="SUSPICIOUS_SOURCE_IP",
            description=f"Traffic detected from known suspicious IP: {log.src_ip}",
            src_ip=log.src_ip,
            dst_ip=log.dst_ip,
            protocol=log.protocol,
            timestamp=log.timestamp,
            metadata={"reason": "IP in blacklist"}
        )
    return None


def check_login_attempts(log: NetworkLog) -> Optional[Alert]:
    """
    Rule 2: Detect too many login attempts from same IP (HTTP)
    Threshold: 5 attempts within the tracking window
    """
    if log.protocol == 'HTTP' and log.payload:
        payload_lower = log.payload.lower()
        
        # Check if payload contains login-related keywords
        if any(keyword in payload_lower for keyword in HTTP_SUSPICIOUS_KEYWORDS):
            # Track this attempt
            login_attempts[log.src_ip].append(log.timestamp)
            
            # Keep only recent attempts (simple implementation for demo)
            # In production, you'd implement time-window logic
            if len(login_attempts[log.src_ip]) > 10:
                login_attempts[log.src_ip] = login_attempts[log.src_ip][-10:]
            
            # Check threshold
            if len(login_attempts[log.src_ip]) >= 5:
                return Alert(
                    alert_id=generate_alert_id(),
                    severity="MEDIUM",
                    alert_type="EXCESSIVE_LOGIN_ATTEMPTS",
                    description=f"Multiple login attempts detected from {log.src_ip}",
                    src_ip=log.src_ip,
                    dst_ip=log.dst_ip,
                    protocol=log.protocol,
                    timestamp=log.timestamp,
                    metadata={
                        "attempt_count": len(login_attempts[log.src_ip]),
                        "payload_snippet": log.payload[:100]
                    }
                )
    return None


def check_suspicious_dns(log: NetworkLog) -> Optional[Alert]:
    """
    Rule 3: Detect suspicious DNS queries
    """
    if log.protocol == 'DNS' and log.payload:
        payload_lower = log.payload.lower()
        
        # Check against suspicious patterns
        for pattern in SUSPICIOUS_DNS_PATTERNS:
            if re.search(pattern, payload_lower):
                return Alert(
                    alert_id=generate_alert_id(),
                    severity="HIGH",
                    alert_type="SUSPICIOUS_DNS_QUERY",
                    description=f"Suspicious DNS query detected: {log.payload}",
                    src_ip=log.src_ip,
                    dst_ip=log.dst_ip,
                    protocol=log.protocol,
                    timestamp=log.timestamp,
                    metadata={
                        "query": log.payload,
                        "matched_pattern": pattern
                    }
                )
    return None


def analyze_log(log: NetworkLog) -> List[Alert]:
    """
    Main analysis function - runs all detection rules
    Returns list of alerts generated for this log
    """
    detected_alerts = []
    
    # Run all detection rules
    detection_rules = [
        check_suspicious_ip,
        check_login_attempts,
        check_suspicious_dns
    ]
    
    for rule in detection_rules:
        alert = rule(log)
        if alert:
            detected_alerts.append(alert)
            alerts_database.append(alert)  # Store in database
    
    return detected_alerts


# ============================================
# Network Scanning Functions
# ============================================



def get_local_ip_and_network() -> tuple:
    """Get the local IP address and network range"""
    try:
        # Get the default gateway interface
        gws = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        # Try to find the active network interface
        for interface_name, interface_addresses in gws.items():
            if interface_name in stats and stats[interface_name].isup:
                for address in interface_addresses:
                    if address.family == socket.AF_INET:
                        ip = address.address
                        # Skip loopback
                        if not ip.startswith('127.'):
                            netmask = address.netmask
                            # Calculate network range
                            network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                            return str(ip), str(network)
        
        # Fallback: get hostname IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip, f"{local_ip}/24"
    except Exception as e:
        return "127.0.0.1", "127.0.0.1/32"


def get_network_interfaces() -> List[NetworkInterface]:
    """Get information about all network interfaces"""
    interfaces = []
    
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        
        for interface_name, interface_addresses in addrs.items():
            # Get interface stats
            is_up = stats[interface_name].isup if interface_name in stats else False
            speed = stats[interface_name].speed if interface_name in stats else None
            mtu = stats[interface_name].mtu if interface_name in stats else None
            
            # Get IP and MAC addresses
            ip_address = None
            mac_address = None
            netmask = None
            
            for addr in interface_addresses:
                if addr.family == socket.AF_INET:
                    ip_address = addr.address
                    netmask = addr.netmask
                elif addr.family == psutil.AF_LINK:
                    mac_address = addr.address
            
            # Get I/O counters
            bytes_sent = None
            bytes_recv = None
            if interface_name in io_counters:
                bytes_sent = io_counters[interface_name].bytes_sent
                bytes_recv = io_counters[interface_name].bytes_recv
            
            interfaces.append(NetworkInterface(
                name=interface_name,
                ip_address=ip_address,
                netmask=netmask,
                mac_address=mac_address,
                speed_mbps=speed,
                is_up=is_up,
                mtu=mtu,
                bytes_sent=bytes_sent,
                bytes_recv=bytes_recv
            ))
    
    except Exception as e:
        pass
    
    return interfaces


def get_gateway() -> Optional[str]:
    """Get the default gateway IP"""
    try:
        gateways = psutil.net_if_addrs()
        # Try to get default gateway via routing table
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(['route', '-n', 'get', 'default'], 
                                  capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'gateway:' in line:
                    return line.split(':')[1].strip()
        elif platform.system() == "Linux":
            result = subprocess.run(['ip', 'route'], 
                                  capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'default' in line:
                    parts = line.split()
                    if len(parts) > 2:
                        return parts[2]
    except Exception:
        pass
    return None


def get_dns_servers() -> List[str]:
    """Get configured DNS servers"""
    dns_servers = []
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(['scutil', '--dns'], 
                                  capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'nameserver' in line.lower():
                    parts = line.split(':')
                    if len(parts) > 1:
                        dns = parts[1].strip()
                        if dns and dns not in dns_servers:
                            dns_servers.append(dns)
        elif platform.system() == "Linux":
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    if line.startswith('nameserver'):
                        dns = line.split()[1]
                        dns_servers.append(dns)
    except Exception:
        pass
    return dns_servers




def calculate_network_metrics(interfaces: List[NetworkInterface]) -> Dict[str, Any]:
    """Calculate network performance metrics"""
    metrics = {
        "total_bytes_sent": 0,
        "total_bytes_received": 0,
        "active_interfaces": 0,
        "max_interface_speed_mbps": 0,
        "total_interfaces": len(interfaces),
    }
    
    for interface in interfaces:
        if interface.is_up:
            metrics["active_interfaces"] += 1
        
        if interface.bytes_sent:
            metrics["total_bytes_sent"] += interface.bytes_sent
        
        if interface.bytes_recv:
            metrics["total_bytes_received"] += interface.bytes_recv
        
        if interface.speed_mbps and interface.speed_mbps > metrics["max_interface_speed_mbps"]:
            metrics["max_interface_speed_mbps"] = interface.speed_mbps
    
    # Calculate total bandwidth in human-readable format
    metrics["total_sent_gb"] = round(metrics["total_bytes_sent"] / (1024**3), 2)
    metrics["total_recv_gb"] = round(metrics["total_bytes_received"] / (1024**3), 2)
    
    return metrics


def generate_network_recommendations(
    interfaces: List[NetworkInterface],
    devices: List[NetworkDevice]
) -> List[str]:
    """Generate network security and performance recommendations"""
    recommendations = []
    
    # Check interface speeds
    for interface in interfaces:
        if interface.is_up and interface.speed_mbps:
            if interface.speed_mbps < 100:
                recommendations.append(
                    f"Interface {interface.name} has low speed ({interface.speed_mbps} Mbps). "
                    "Consider upgrading to Fast Ethernet (100+ Mbps) or Gigabit Ethernet."
                )
    
    # Check for too many devices
    if len(devices) > 20:
        recommendations.append(
            f"High number of devices detected ({len(devices)}). "
            "Consider network segmentation for better security and performance."
        )
    
    # Generic security recommendations
    recommendations.append(
        "Regularly monitor network traffic for suspicious activities using NetSentry's /analyze endpoint."
    )
    
    if len(recommendations) == 1:  # Only generic recommendation
        recommendations.insert(0, "Network configuration looks good. No major issues detected.")
    
    return recommendations


# ============================================
# ML Prediction Functions
# ============================================

def prepare_features_for_prediction(features: MLFeatures) -> pd.DataFrame:
    """Prepare input features for ML model prediction"""
    # Convert to dictionary
    feature_dict = features.dict()
    
    # Create dataframe
    df = pd.DataFrame([feature_dict])
    
    # Encode categorical variables
    categorical_cols = ['protocol_type', 'service', 'flag']
    for col in categorical_cols:
        if col in ml_models['encoders']:
            le = ml_models['encoders'][col]
            try:
                df[col + '_encoded'] = le.transform(df[col])
            except ValueError:
                # If value not seen during training, use most common class
                df[col + '_encoded'] = 0
    
    # Use the exact feature list from training
    if ml_models['features'] is None:
        raise ValueError("Feature list not loaded from training")
    
    # Get the feature columns used during training
    training_features = ml_models['features']
    
    # Create a dataframe with all required features, filling missing ones with 0
    X = pd.DataFrame(columns=training_features)
    
    # Fill in the features we have
    for feature in training_features:
        if feature in df.columns:
            X[feature] = df[feature].values
        else:
            # Fill missing features with 0
            X[feature] = 0
    
    # Ensure correct data types
    X = X.astype(float)
    
    return X


def predict_binary(features: MLFeatures) -> MLPredictionResponse:
    """Predict if traffic is normal or attack (binary classification)"""
    if not models_loaded or ml_models['binary'] is None:
        return MLPredictionResponse(
            status="error",
            model_available=False,
            message="ML model not loaded. Please train the model first.",
            timestamp=datetime.utcnow().isoformat()
        )
    
    try:
        # Prepare features
        X = prepare_features_for_prediction(features)
        
        # Debug logging
        print(f"Prepared features shape: {X.shape}")
        print(f"Feature columns: {X.columns.tolist()}")
        
        # Make prediction
        prediction = ml_models['binary'].predict(X)[0]
        probabilities = ml_models['binary'].predict_proba(X)[0]
        
        # Get prediction label
        prediction_label = "Normal" if prediction == 0 else "Attack"
        confidence = float(probabilities[prediction])
        
        return MLPredictionResponse(
            status="success",
            model_available=True,
            prediction=str(prediction),
            prediction_label=prediction_label,
            confidence=round(confidence, 4),
            probabilities={
                "Normal": round(float(probabilities[0]), 4),
                "Attack": round(float(probabilities[1]), 4)
            },
            message=f"Prediction: {prediction_label} (confidence: {confidence:.2%})",
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        print(f"Prediction error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return MLPredictionResponse(
            status="error",
            model_available=True,
            message=f"Prediction failed: {str(e)}",
            timestamp=datetime.utcnow().isoformat()
        )


def predict_multiclass(features: MLFeatures) -> MLPredictionResponse:
    """Predict attack type (multi-class classification: normal, dos, probe, r2l, u2r)"""
    if not models_loaded or ml_models['multi'] is None:
        return MLPredictionResponse(
            status="error",
            model_available=False,
            message="ML model not loaded. Please train the model first.",
            timestamp=datetime.utcnow().isoformat()
        )
    
    try:
        # Prepare features
        X = prepare_features_for_prediction(features)
        
        # Debug logging
        print(f"Prepared features shape: {X.shape}")
        
        # Make prediction
        prediction = ml_models['multi'].predict(X)[0]
        probabilities = ml_models['multi'].predict_proba(X)[0]
        
        # Get class names
        classes = ml_models['multi'].classes_
        
        # Get prediction label
        prediction_label = prediction.upper()
        confidence = float(probabilities[list(classes).index(prediction)])
        
        # Create probabilities dictionary
        proba_dict = {
            cls.upper(): round(float(prob), 4) 
            for cls, prob in zip(classes, probabilities)
        }
        
        return MLPredictionResponse(
            status="success",
            model_available=True,
            prediction=prediction,
            prediction_label=prediction_label,
            confidence=round(confidence, 4),
            probabilities=proba_dict,
            message=f"Prediction: {prediction_label} (confidence: {confidence:.2%})",
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        print(f"Prediction error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return MLPredictionResponse(
            status="error",
            model_available=True,
            message=f"Prediction failed: {str(e)}",
            timestamp=datetime.utcnow().isoformat()
        )


# ============================================
# API Endpoints
# ============================================

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_traffic(log: NetworkLog):
    """
    Analyze network traffic log and detect anomalies
    
    Request Body:
    - src_ip: Source IP address
    - dst_ip: Destination IP address
    - protocol: Protocol type (TCP, UDP, HTTP, DNS)
    - payload: Optional payload data
    
    Returns:
    - List of alerts if anomalies detected
    """
    try:
        # Analyze the log
        detected_alerts = analyze_log(log)
        
        if detected_alerts:
            return AnalysisResponse(
                status="alert",
                alerts=detected_alerts,
                message=f"Detected {len(detected_alerts)} anomaly/anomalies"
            )
        else:
            return AnalysisResponse(
                status="clean",
                alerts=[],
                message="No anomalies detected"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/alerts", response_model=Dict[str, Any])
async def get_alerts(
    severity: Optional[str] = None,
    limit: Optional[int] = None
):
    """
    Retrieve all stored alerts
    
    Query Parameters:
    - severity: Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
    - limit: Maximum number of alerts to return
    
    Returns:
    - List of all alerts with metadata
    """
    filtered_alerts = alerts_database
    
    # Filter by severity if provided
    if severity:
        filtered_alerts = [a for a in filtered_alerts if a.severity == severity.upper()]
    
    # Apply limit if provided
    if limit:
        filtered_alerts = filtered_alerts[-limit:]
    
    return {
        "total_alerts": len(alerts_database),
        "filtered_count": len(filtered_alerts),
        "alerts": filtered_alerts
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
    - System status and metadata
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "NetSentry",
        "description": "Cloud-Based Network Traffic Analysis System with ML-powered Intrusion Detection",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Analyze network traffic log (rule-based)",
            "GET /alerts": "Retrieve stored alerts",
            "GET /health": "Health check",
            "GET /stats": "Get system statistics",
            "GET /network-scan": "Perform comprehensive network analysis",
            "POST /predict/binary": "ML prediction: Normal vs Attack",
            "POST /predict/multiclass": "ML prediction: Attack type classification",
            "GET /ml/status": "Check ML model status and availability"
        },
        "ml_models": {
            "binary_classifier": "Random Forest - Normal vs Attack",
            "multiclass_classifier": "Random Forest - Normal, DOS, PROBE, R2L, U2R",
            "models_loaded": models_loaded
        },
        "documentation": "/docs"
    }


# ============================================
# Additional Utility Endpoints
# ============================================

@app.delete("/alerts")
async def clear_alerts():
    """
    Clear all stored alerts (for testing/demo purposes)
    """
    alerts_database.clear()
    login_attempts.clear()
    return {"message": "All alerts cleared", "status": "success"}


@app.get("/stats")
async def get_statistics():
    """
    Get system statistics
    """
    severity_counts = defaultdict(int)
    type_counts = defaultdict(int)
    
    for alert in alerts_database:
        severity_counts[alert.severity] += 1
        type_counts[alert.alert_type] += 1
    
    return {
        "total_alerts": len(alerts_database),
        "by_severity": dict(severity_counts),
        "by_type": dict(type_counts),
        "monitored_ips": len(login_attempts),
        "suspicious_ip_count": len(SUSPICIOUS_IPS)
    }


@app.get("/network-scan", response_model=NetworkScanReport)
async def scan_network():
    """
    Perform comprehensive network analysis
    
    This endpoint analyzes the local network and provides detailed information including:
    - Network interfaces and their speeds
    - Local IP and network range
    - Gateway and DNS servers
    - Network performance metrics
    - Security and performance recommendations
    
    Returns:
    - Comprehensive network analysis report
    """
    try:
        # Get local IP and network range
        local_ip, network_range = get_local_ip_and_network()
        
        # Get network interfaces
        interfaces = get_network_interfaces()
        
        # Get gateway and DNS servers
        gateway = get_gateway()
        dns_servers = get_dns_servers()
        
        # No device discovery (nmap removed)
        discovered_devices = []
        
        # Calculate network metrics
        network_metrics = calculate_network_metrics(interfaces)
        
        # Generate recommendations
        recommendations = generate_network_recommendations(
            interfaces, discovered_devices
        )
        
        return NetworkScanReport(
            status="success",
            scan_timestamp=datetime.utcnow().isoformat(),
            local_ip=local_ip,
            network_range=network_range,
            gateway=gateway,
            dns_servers=dns_servers,
            interfaces=interfaces,
            discovered_devices=discovered_devices,
            network_metrics=network_metrics,
            recommendations=recommendations
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Network scan failed: {str(e)}"
        )


@app.post("/predict/binary", response_model=MLPredictionResponse)
async def predict_binary_endpoint(features: MLFeatures):
    """
    Predict if network traffic is Normal or Attack using Random Forest binary classifier
    
    Request Body:
    - All 41 KDDCUP'99 features (see MLFeatures model)
    
    Returns:
    - Prediction: Normal (0) or Attack (1)
    - Confidence score
    - Probability for each class
    """
    return predict_binary(features)


@app.post("/predict/multiclass", response_model=MLPredictionResponse)
async def predict_multiclass_endpoint(features: MLFeatures):
    """
    Predict attack type using Random Forest multi-class classifier
    
    Request Body:
    - All 41 KDDCUP'99 features (see MLFeatures model)
    
    Returns:
    - Prediction: NORMAL, DOS, PROBE, R2L, or U2R
    - Confidence score
    - Probability for each attack type
    """
    return predict_multiclass(features)


@app.get("/ml/status")
async def ml_model_status():
    """
    Check ML model status and availability
    
    Returns:
    - Model loading status
    - Available models
    - Model information
    """
    return {
        "models_loaded": models_loaded,
        "binary_model_available": ml_models['binary'] is not None,
        "multiclass_model_available": ml_models['multi'] is not None,
        "encoders_available": ml_models['encoders'] is not None,
        "features_count": len(ml_models['features']) if ml_models['features'] else 0,
        "message": "ML models ready" if models_loaded else "ML models not loaded. Train models using the notebook.",
        "model_types": {
            "binary": "Random Forest - Normal vs Attack",
            "multiclass": "Random Forest - Normal, DOS, PROBE, R2L, U2R"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

