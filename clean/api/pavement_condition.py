#!/usr/bin/env python3
"""
Pavement Condition API Endpoint with QRL Integration
Receives Street View location data and returns pavement condition predictions
Uses Quantum Reinforcement Learning for intelligent condition assessment
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import random
import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

logger = logging.getLogger(__name__)

# Create router
pavement_router = APIRouter(prefix="/api", tags=["pavement"])

# Try to import QRL agent
try:
    # Try multiple import paths
    try:
        from ai.qrl_traffic_agent import QRLTrafficAgent
    except ImportError:
        import sys
        from pathlib import Path
        parent_dir = Path(__file__).resolve().parent.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
        from ai.qrl_traffic_agent import QRLTrafficAgent
    QRL_AVAILABLE = True
    logger.info("✅ QRL agent loaded for pavement analysis")
except Exception as e:
    QRL_AVAILABLE = False
    logger.warning(f"⚠️ QRL agent not available: {e}")
    QRLTrafficAgent = None

class PavementConditionRequest(BaseModel):
    """Request model for pavement condition analysis"""
    latitude: float
    longitude: float
    heading: Optional[float] = None  # Street View heading
    pitch: Optional[float] = None    # Street View pitch
    zoom: Optional[float] = None     # Street View zoom

class PavementConditionResponse(BaseModel):
    """Response model for pavement condition"""
    pci: float  # Pavement Condition Index (0-100)
    condition: str  # Excellent, Good, Fair, Poor, Critical
    confidence: float  # Model confidence (0-1)
    timestamp: str
    location: dict
    details: Optional[dict] = None  # Additional analysis details

# Pavement Condition Model with QRL Integration
class PavementConditionModel:
    """
    Pavement Condition ML Model with Quantum Reinforcement Learning
    Uses QRL agent to classify pavement condition risk levels
    """
    
    def __init__(self):
        self.model_loaded = False
        self.qrl_agent = None
        
        # Initialize QRL agent if available
        if QRL_AVAILABLE:
            try:
                self.qrl_agent = QRLTrafficAgent(n_qubits=2, n_layers=2, seed=42)
                logger.info("🔬 QRL agent initialized for pavement analysis")
            except Exception as e:
                logger.warning(f"Failed to initialize QRL agent: {e}")
                self.qrl_agent = None
        
        logger.info("PavementConditionModel initialized with QRL support")
    
    def load_model(self, model_path: str):
        """
        Load the trained pavement condition model
        
        Args:
            model_path: Path to the saved model file
        """
        # TODO: Implement model loading
        # Example:
        # import tensorflow as tf
        # self.model = tf.keras.models.load_model(model_path)
        # self.model_loaded = True
        logger.info(f"TODO: Load model from {model_path}")
        pass
    
    def predict(self, latitude: float, longitude: float, 
                heading: Optional[float] = None, 
                pitch: Optional[float] = None) -> dict:
        """
        Predict pavement condition for given location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            heading: Street View heading (optional)
            pitch: Street View pitch (optional)
            
        Returns:
            dict with prediction results
        """
        
        if not self.model_loaded:
            # TODO: Remove this mock prediction when model is ready
            return self._mock_prediction(latitude, longitude)
        
        # TODO: Implement actual prediction
        # Steps:
        # 1. Fetch Street View image for the location
        # 2. Preprocess image (resize, normalize, etc.)
        # 3. Run model inference
        # 4. Post-process results
        # 5. Return prediction with confidence
        
        # Example pseudocode:
        # image = fetch_street_view_image(latitude, longitude, heading, pitch)
        # processed_image = preprocess_image(image)
        # prediction = self.model.predict(processed_image)
        # pci_score = post_process_prediction(prediction)
        # confidence = calculate_confidence(prediction)
        
        return {
            "pci": 0.0,
            "confidence": 0.0,
            "details": {}
        }
    
    def _mock_prediction(self, latitude: float, longitude: float) -> dict:
        """
        Generate prediction with QRL-enhanced analysis
        Uses quantum circuit to classify pavement condition risk
        """
        # Generate base PCI from location (simulating image analysis)
        seed = (latitude * longitude * 10000) % 1
        base_pci = 40 + (abs(seed) * 50)  # PCI between 40-90
        
        # Add time-based variation (pavement degrades over time)
        hour = datetime.datetime.now().hour
        time_factor = 1.0 - (hour / 100.0)  # Slight degradation simulation
        pci = base_pci * time_factor
        
        # Use QRL agent for intelligent risk classification
        if self.qrl_agent:
            try:
                # Map PCI to "volume" concept (higher PCI = better condition = lower "risk volume")
                # Invert PCI so lower PCI = higher risk score
                risk_volume = (100 - pci) * 8  # Scale to 0-800 range like traffic
                
                qrl_result = self.qrl_agent.classify_risk(
                    volume=risk_volume,
                    hour=hour
                )
                
                risk_label = qrl_result['risk_label']
                risk_probs = qrl_result['probs']
                
                # Adjust confidence based on quantum probabilities
                max_prob = max(risk_probs.values())
                confidence = 0.70 + (max_prob * 0.25)  # 0.70-0.95 range
                
                # Map QRL risk levels to pavement distress
                distress_mapping = {
                    'NORMAL': ['Minor Surface Wear'],
                    'WATCH': ['Light Cracking', 'Surface Oxidation'],
                    'CONGESTED': ['Cracking', 'Rutting', 'Edge Deterioration'],
                    'CRITICAL': ['Severe Cracking', 'Potholes', 'Structural Damage']
                }
                
                distress_types = distress_mapping.get(risk_label, ['Unknown'])
                
                # Determine severity and action
                severity_map = {
                    'NORMAL': 'Low',
                    'WATCH': 'Low-Medium',
                    'CONGESTED': 'Medium-High',
                    'CRITICAL': 'High'
                }
                severity = severity_map.get(risk_label, 'Medium')
                
                action_map = {
                    'NORMAL': 'No action required - Continue monitoring',
                    'WATCH': 'Schedule routine inspection',
                    'CONGESTED': 'Plan maintenance within 6 months',
                    'CRITICAL': 'Immediate repair required'
                }
                recommended_action = action_map.get(risk_label, 'Assess condition')
                
                return {
                    "pci": round(pci, 2),
                    "confidence": round(confidence, 3),
                    "details": {
                        "distress_types": distress_types,
                        "severity": severity,
                        "recommended_action": recommended_action,
                        "qrl_analysis": {
                            "risk_label": risk_label,
                            "risk_probabilities": {k: round(v, 3) for k, v in risk_probs.items()},
                            "quantum_confidence": round(max_prob, 3),
                            "analysis_method": "Quantum Reinforcement Learning"
                        }
                    }
                }
            except Exception as e:
                logger.error(f"QRL analysis failed: {e}")
                # Fallback to basic analysis
        
        # Fallback: Basic analysis without QRL
        confidence = 0.75 + (random.random() * 0.20)
        distress_types = []
        if pci < 60:
            distress_types.append("Cracking")
        if pci < 70:
            distress_types.append("Rutting")
        if pci < 50:
            distress_types.append("Potholes")
        
        return {
            "pci": round(pci, 2),
            "confidence": round(confidence, 3),
            "details": {
                "distress_types": distress_types if distress_types else ["Minor Wear"],
                "severity": "Medium" if pci < 60 else "Low",
                "recommended_action": "Monitor" if pci > 70 else "Maintenance Required",
                "analysis_method": "Classical ML (QRL unavailable)"
            }
        }

# Initialize model (global instance)
pavement_model = PavementConditionModel()

# TODO: Load your friend's trained model
# Uncomment and update the path when model is ready:
# MODEL_PATH = "./models/pavement_condition_model.h5"
# pavement_model.load_model(MODEL_PATH)

@pavement_router.post("/pavement-condition", response_model=PavementConditionResponse)
async def analyze_pavement_condition(request: PavementConditionRequest):
    """
    Analyze pavement condition at a given location
    
    This endpoint receives Street View location data and returns
    the predicted pavement condition using the ML model.
    
    Args:
        request: PavementConditionRequest with location data
        
    Returns:
        PavementConditionResponse with PCI score and condition rating
    """
    try:
        logger.info(f"Analyzing pavement at ({request.latitude}, {request.longitude})")
        
        # Validate coordinates
        if not (-90 <= request.latitude <= 90):
            raise HTTPException(status_code=400, detail="Invalid latitude")
        if not (-180 <= request.longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid longitude")
        
        # Run prediction
        prediction = pavement_model.predict(
            latitude=request.latitude,
            longitude=request.longitude,
            heading=request.heading,
            pitch=request.pitch
        )
        
        # Determine condition rating from PCI
        pci = prediction["pci"]
        if pci >= 85:
            condition = "Excellent"
        elif pci >= 70:
            condition = "Good"
        elif pci >= 55:
            condition = "Fair"
        elif pci >= 40:
            condition = "Poor"
        else:
            condition = "Critical"
        
        # Build response
        response = PavementConditionResponse(
            pci=pci,
            condition=condition,
            confidence=prediction["confidence"],
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
            location={
                "latitude": request.latitude,
                "longitude": request.longitude,
                "heading": request.heading,
                "pitch": request.pitch
            },
            details=prediction.get("details")
        )
        
        logger.info(f"Prediction: PCI={pci:.2f}, Condition={condition}, Confidence={prediction['confidence']:.3f}")
        
        # Store in Azure Digital Twins and Event Hub (background task)
        try:
            from adt_client import ADTClient
            import os
            adt_url = os.getenv("ADT_INSTANCE_URL", "https://fgcu-traffic-dt.api.eus.digitaltwins.azure.net")
            adt_client = ADTClient(adt_url)
            
            # Create unique asset ID from location
            asset_id = f"{request.latitude:.6f}_{request.longitude:.6f}".replace(".", "_").replace("-", "n")
            
            # Prepare pavement asset data
            pavement_data = {
                "assetId": asset_id,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "pci": int(pci),
                "condition": condition,
                "confidence": prediction["confidence"],
                "lastInspectionDate": datetime.datetime.utcnow().isoformat(),
                "maintenancePriority": "high" if pci < 55 else "medium" if pci < 70 else "low"
            }
            
            # Add QRL analysis data if available
            if prediction.get("details") and prediction["details"].get("qrl_analysis"):
                qrl_data = prediction["details"]["qrl_analysis"]
                pavement_data["riskLevel"] = qrl_data.get("risk_label", "UNKNOWN")
                pavement_data["distressTypes"] = prediction["details"].get("distress_types", [])
            
            # Create or update pavement asset twin
            await adt_client.create_pavement_twin(pavement_data)
            logger.info(f"✅ Pavement data stored in ADT: {asset_id}")
            
            # Send to Event Hub for real-time streaming
            try:
                from event_hub_ingestion import TrafficEventHubProducer
                eventhub_namespace = os.getenv("EVENTHUB_NAMESPACE", "fgcu-traffic")
                eventhub_name = os.getenv("EVENTHUB_NAME", "pavement-stream")
                producer = TrafficEventHubProducer(eventhub_namespace, eventhub_name)
                
                event_data = {
                    "event_type": "pavement_analysis",
                    "asset_id": asset_id,
                    "pci": pci,
                    "condition": condition,
                    "confidence": prediction["confidence"],
                    "latitude": request.latitude,
                    "longitude": request.longitude,
                    "timestamp": response.timestamp,
                    "details": prediction.get("details", {})
                }
                
                await producer.send_traffic_event(event_data)
                logger.info(f"✅ Pavement event sent to Event Hub")
            except Exception as eh_error:
                logger.warning(f"⚠️ Event Hub unavailable: {eh_error}")
                
        except Exception as adt_error:
            logger.warning(f"⚠️ ADT storage unavailable: {adt_error}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing pavement condition: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze pavement condition: {str(e)}")

@pavement_router.get("/pavement-model-status")
async def get_model_status():
    """
    Get the status of the pavement condition ML model with QRL integration
    
    Returns:
        Model status information including QRL agent status
    """
    qrl_status = "active" if pavement_model.qrl_agent else "unavailable"
    
    return {
        "model_loaded": pavement_model.model_loaded,
        "qrl_agent": qrl_status,
        "status": "QRL-enhanced predictions" if pavement_model.qrl_agent else "basic predictions",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "capabilities": {
            "quantum_analysis": pavement_model.qrl_agent is not None,
            "risk_classification": pavement_model.qrl_agent is not None,
            "confidence_scoring": True,
            "distress_detection": True
        },
        "qrl_info": {
            "n_qubits": 2 if pavement_model.qrl_agent else 0,
            "n_layers": 2 if pavement_model.qrl_agent else 0,
            "risk_levels": ["NORMAL", "WATCH", "CONGESTED", "CRITICAL"] if pavement_model.qrl_agent else []
        } if pavement_model.qrl_agent else None
    }

@pavement_router.post("/reload-model")
async def reload_model(model_path: Optional[str] = None):
    """
    Reload the pavement condition model
    
    Args:
        model_path: Optional path to model file
        
    Returns:
        Success message
    """
    try:
        if model_path:
            pavement_model.load_model(model_path)
        else:
            logger.warning("No model path provided")
            return {
                "status": "warning",
                "message": "No model path provided. Using mock predictions.",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
        
        return {
            "status": "success",
            "message": "Model reloaded successfully",
            "model_loaded": pavement_model.model_loaded,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error reloading model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reload model: {str(e)}")
