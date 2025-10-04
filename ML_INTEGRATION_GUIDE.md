# ML Model Integration Guide

## Overview

NetSentry now includes **Random Forest machine learning models** for network intrusion detection. The system supports both binary classification (Normal vs Attack) and multi-class classification (Normal, DOS, PROBE, R2L, U2R).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     NetSentry ML System                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌─────────────────────────┐    │
│  │  Training        │      │  Backend API            │    │
│  │  (Jupyter NB)    │──────▶│  (FastAPI)              │    │
│  │                  │      │  - Model Loading        │    │
│  │  - Load KDDCUP   │      │  - Prediction API       │    │
│  │  - Train RF      │      │  - Feature Encoding     │    │
│  │  - Save Models   │      └────────┬────────────────┘    │
│  └──────────────────┘               │                      │
│                                     │                      │
│  ┌──────────────────┐               │                      │
│  │  Saved Models    │◀──────────────┘                      │
│  │  (PKL Files)     │                                      │
│  │                  │               ┌────────────────────┐ │
│  │  - RF Binary     │               │  Frontend UI       │ │
│  │  - RF Multiclass │               │  (Next.js/React)   │ │
│  │  - Encoders      │               │                    │ │
│  │  - Features      │               │  - Input Form      │ │
│  └──────────────────┘               │  - Predictions     │ │
│                                     │  - Visualizations  │ │
│                                     └────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Machine Learning Models

**Location:** `/modelBuilding/models/`

The system includes 5 key model files:

- `rf_binary_classifier.pkl` - Binary classification model (Normal vs Attack)
- `rf_multiclass_classifier.pkl` - Multi-class classification model (5 classes)
- `label_encoders.pkl` - Encoders for categorical features
- `feature_columns.pkl` - List of features used in training
- `attack_mapping.pkl` - Mapping of attacks to categories

### 2. Training Notebook

**Location:** `/modelBuilding/random_forest_intrusion_detection.ipynb`

Features:
- Complete data loading and preprocessing pipeline
- EDA and visualization
- Binary classification (Normal vs Attack)
- Multi-class classification (Normal, DOS, PROBE, R2L, U2R)
- Model evaluation with metrics and confusion matrices
- Feature importance analysis
- Model persistence

### 3. Backend API (FastAPI)

**File:** `app.py`

New endpoints:

#### `POST /predict/binary`
Predict if traffic is Normal or Attack.

**Request Body:**
```json
{
  "duration": 0,
  "protocol_type": "tcp",
  "service": "http",
  "flag": "SF",
  "src_bytes": 181,
  "dst_bytes": 5450,
  "count": 8,
  "srv_count": 8,
  ...
}
```

**Response:**
```json
{
  "status": "success",
  "model_available": true,
  "prediction": "0",
  "prediction_label": "Normal",
  "confidence": 0.95,
  "probabilities": {
    "Normal": 0.95,
    "Attack": 0.05
  },
  "message": "Prediction: Normal (confidence: 95.00%)",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### `POST /predict/multiclass`
Predict attack type.

**Response:**
```json
{
  "status": "success",
  "model_available": true,
  "prediction": "dos",
  "prediction_label": "DOS",
  "confidence": 0.92,
  "probabilities": {
    "NORMAL": 0.02,
    "DOS": 0.92,
    "PROBE": 0.04,
    "R2L": 0.01,
    "U2R": 0.01
  },
  "message": "Prediction: DOS (confidence: 92.00%)",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### `GET /ml/status`
Check ML model status.

**Response:**
```json
{
  "models_loaded": true,
  "binary_model_available": true,
  "multiclass_model_available": true,
  "encoders_available": true,
  "features_count": 44,
  "message": "ML models ready",
  "model_types": {
    "binary": "Random Forest - Normal vs Attack",
    "multiclass": "Random Forest - Normal, DOS, PROBE, R2L, U2R"
  }
}
```

### 4. Frontend UI (React/Next.js)

**Component:** `frontend/components/ml-predictor.tsx`

Features:
- Sample data loading (Normal, DOS, PROBE)
- Interactive feature input form
- Binary and multi-class prediction
- Real-time confidence scores
- Probability visualizations
- Attack type badges with color coding

**Integration:** Added to dashboard as new "ML Prediction" tab

## Setup Instructions

### 1. Train the Models

First, train the Random Forest models using the Jupyter notebook:

```bash
cd modelBuilding
jupyter notebook random_forest_intrusion_detection.ipynb
```

Run all cells in the notebook. This will:
- Load the KDDCUP'99 dataset
- Train both binary and multi-class models
- Save models to `modelBuilding/models/` directory

### 2. Install Dependencies

Update backend dependencies:

```bash
pip install -r requirements.txt
```

New dependencies added:
- `pandas==2.1.3`
- `numpy==1.26.2`
- `scikit-learn==1.3.2`
- `joblib==1.3.2`

### 3. Start the Backend

```bash
python app.py
```

The backend will automatically load ML models on startup. You should see:
```
✓ ML models loaded successfully
```

If models aren't found:
```
⚠ ML models directory not found: /path/to/modelBuilding/models
```

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Access the dashboard at: `http://localhost:3000`

## Usage

### Using the ML Predictor

1. Navigate to the **ML Prediction** tab in the dashboard
2. Load sample data or enter custom features
3. Click **Binary Prediction** or **Multi-class Prediction**
4. View results with confidence scores and probabilities

### Sample Data

The system includes 3 pre-configured samples:

**Normal Traffic:**
- Low connection counts
- Balanced error rates
- Normal service flags (SF)

**DOS Attack:**
- High connection counts (500+)
- High error rates (1.0)
- Many destination hosts (255)

**PROBE Attack:**
- Medium connection counts (123)
- REJ flags (rejected connections)
- Scanning patterns

## Model Performance

### Binary Classification
- Accuracy: ~99%
- Precision: ~99%
- Recall: ~99%
- F1-Score: ~99%
- ROC-AUC: ~0.99

### Multi-class Classification
- Overall Accuracy: ~95%
- DOS Detection: ~98%
- PROBE Detection: ~92%
- R2L Detection: ~85%
- U2R Detection: ~80%

## Attack Categories

### DOS (Denial of Service)
Depletes victim's resources:
- back, neptune, smurf, teardrop, pod, land

### PROBE (Surveillance)
Network scanning and reconnaissance:
- portsweep, ipsweep, nmap, satan, mscan, saint

### R2L (Remote to Local)
Unauthorized remote access:
- ftp_write, guess_passwd, imap, phf, spy, warezclient

### U2R (User to Root)
Privilege escalation:
- buffer_overflow, loadmodule, perl, rootkit

## API Testing

### Test Binary Prediction

```bash
curl -X POST http://localhost:8000/predict/binary \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 0,
    "protocol_type": "tcp",
    "service": "http",
    "flag": "SF",
    "src_bytes": 181,
    "dst_bytes": 5450,
    "count": 8,
    "srv_count": 8,
    "serror_rate": 0,
    "srv_serror_rate": 0,
    "same_srv_rate": 1.0,
    "diff_srv_rate": 0,
    "dst_host_count": 9,
    "dst_host_srv_count": 9,
    "dst_host_same_srv_rate": 1.0,
    "dst_host_diff_srv_rate": 0,
    "dst_host_serror_rate": 0,
    "dst_host_srv_serror_rate": 0
  }'
```

### Test Model Status

```bash
curl http://localhost:8000/ml/status
```

## Troubleshooting

### Models Not Loading

**Issue:** `⚠ ML models directory not found`

**Solution:**
1. Ensure you've run the Jupyter notebook
2. Check that `modelBuilding/models/` directory exists
3. Verify all 5 model files are present

### Import Errors

**Issue:** `ModuleNotFoundError: No module named 'sklearn'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Prediction Errors

**Issue:** `ValueError: X has different number of features`

**Solution:**
- Ensure all 41 KDDCUP features are provided
- Check categorical values match training data
- Reload models if recently retrained

### Frontend Connection Issues

**Issue:** `Cannot connect to backend API`

**Solution:**
1. Verify backend is running on port 8000
2. Check CORS settings in `app.py`
3. Ensure no firewall blocking

## Feature Descriptions

### Basic Features (9)
- **duration**: Connection length in seconds
- **protocol_type**: tcp, udp, icmp
- **service**: http, ftp, smtp, etc.
- **flag**: Connection status (SF, S0, REJ, etc.)
- **src_bytes**: Bytes from source to destination
- **dst_bytes**: Bytes from destination to source
- **land**: Same src/dst IP and port (1/0)
- **wrong_fragment**: Number of wrong fragments
- **urgent**: Number of urgent packets

### Content Features (13)
- **hot**: Number of "hot" indicators
- **num_failed_logins**: Failed login attempts
- **logged_in**: Successfully logged in (1/0)
- **num_compromised**: Compromised conditions
- **root_shell**: Root shell obtained (1/0)
- **su_attempted**: "su root" attempted (1/0)
- **num_root**: Root accesses
- **num_file_creations**: File creation operations
- **num_shells**: Shell prompts
- **num_access_files**: Access control file operations
- **num_outbound_cmds**: Outbound commands in FTP
- **is_host_login**: Login from hot list (1/0)
- **is_guest_login**: Guest login (1/0)

### Traffic Features (9)
- **count**: Connections to same host (2 seconds)
- **srv_count**: Connections to same service (2 seconds)
- **serror_rate**: % of connections with SYN errors
- **srv_serror_rate**: % srv connections with SYN errors
- **rerror_rate**: % connections with REJ errors
- **srv_rerror_rate**: % srv connections with REJ errors
- **same_srv_rate**: % connections to same service
- **diff_srv_rate**: % connections to different services
- **srv_diff_host_rate**: % srv connections to diff hosts

### Host Features (10)
- **dst_host_count**: Connections to same dest host
- **dst_host_srv_count**: Connections to same port
- **dst_host_same_srv_rate**: % same service
- **dst_host_diff_srv_rate**: % different services
- **dst_host_same_src_port_rate**: % same source port
- **dst_host_srv_diff_host_rate**: % different dest machines
- **dst_host_serror_rate**: % SYN errors
- **dst_host_srv_serror_rate**: % srv SYN errors
- **dst_host_rerror_rate**: % REJ errors
- **dst_host_srv_rerror_rate**: % srv REJ errors

## Future Enhancements

1. **Real-time Integration**
   - Auto-analyze live network traffic
   - Continuous monitoring mode
   - Alert generation from ML predictions

2. **Model Updates**
   - Online learning capabilities
   - Model retraining pipeline
   - A/B testing framework

3. **Advanced Features**
   - Deep learning models (LSTM, CNN)
   - Ensemble methods
   - Feature engineering automation

4. **Performance Optimization**
   - Model quantization
   - Batch prediction API
   - Caching layer

## Support

For issues or questions:
1. Check model status: `GET /ml/status`
2. Review logs in backend console
3. Verify all dependencies are installed
4. Ensure models are trained and saved

## References

- KDDCUP'99 Dataset: http://kdd.ics.uci.edu/databases/kddcup99/kddcup99.html
- Random Forest Algorithm: scikit-learn documentation
- FastAPI: https://fastapi.tiangolo.com/
- Next.js: https://nextjs.org/

