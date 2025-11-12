import React, { useState } from 'react';
import axios from 'axios';
import './LayoutParser.css';

const LayoutParser = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setResult(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await axios.post(`${API_URL}/api/parse-layout`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.error || 
        err.message || 
        'Failed to parse layout. Make sure the backend server is running.'
      );
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="layout-parser">
      <div className="upload-section">
        <div className="upload-area">
          <input
            type="file"
            id="file-input"
            accept="image/*"
            onChange={handleFileSelect}
            className="file-input"
          />
          <label htmlFor="file-input" className="file-label">
            {preview ? (
              <img src={preview} alt="Preview" className="preview-image" />
            ) : (
              <div className="upload-placeholder">
                <span className="upload-icon">📤</span>
                <p>Click to select a newspaper image</p>
                <p className="upload-hint">or drag and drop</p>
              </div>
            )}
          </label>
        </div>

        <div className="controls">
          <button
            onClick={handleUpload}
            disabled={!selectedFile || loading}
            className="btn btn-primary"
          >
            {loading ? 'Parsing...' : 'Parse Layout'}
          </button>
          {selectedFile && (
            <button onClick={handleReset} className="btn btn-secondary">
              Reset
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {result && (
        <div className="results-section">
          <h2>Layout Analysis Results</h2>
          
          {result.image_with_layout && (
            <div className="result-image">
              <h3>Annotated Image</h3>
              <img 
                src={`data:image/png;base64,${result.image_with_layout}`} 
                alt="Layout analysis" 
                className="annotated-image"
              />
            </div>
          )}

          <div className="layout-details">
            <h3>Detected Layout Elements ({result.layout?.length || 0})</h3>
            {result.layout && result.layout.length > 0 ? (
              <div className="layout-list">
                {result.layout.map((element, index) => (
                  <div key={index} className="layout-item">
                    <div className="layout-item-header">
                      <span className="layout-type">{element.type || 'Unknown'}</span>
                      <span className="layout-confidence">
                        Confidence: {(element.score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="layout-coordinates">
                      <div>X: {element.block?.x_1?.toFixed(0) || 'N/A'}</div>
                      <div>Y: {element.block?.y_1?.toFixed(0) || 'N/A'}</div>
                      <div>Width: {element.block?.width?.toFixed(0) || 'N/A'}</div>
                      <div>Height: {element.block?.height?.toFixed(0) || 'N/A'}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-results">No layout elements detected.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default LayoutParser;

