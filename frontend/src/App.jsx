import { useEffect, useState } from 'react'
import './App.css'

function App() {
  // ==============================
  // Disease Detection State
  // ==============================

  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [location, setLocation] = useState('')

  // ==============================
  // Yield Prediction State
  // ==============================

  const [yieldForm, setYieldForm] = useState({
    crop: '',
    area: 'India',
    year: '2026',
  })

  const [yieldResult, setYieldResult] = useState(null)
  const [yieldLoading, setYieldLoading] = useState(false)
  const [yieldError, setYieldError] = useState('')

  // ==============================
  // Scan History State
  // ==============================

  const [scanHistory, setScanHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState('')
  const [showAllHistory, setShowAllHistory] = useState(false)

  // ==============================
  // Fetch Scan History
  // ==============================

  const fetchScanHistory = async () => {
    setHistoryLoading(true)
    setHistoryError('')

    try {
      const response = await fetch(
        `http://127.0.0.1:8001/scan-history?t=${Date.now()}`,
        {
          method: 'GET',
          cache: 'no-store',
        }
      )

      const responseText = await response.text()

      if (!response.ok) {
        throw new Error(
          `Server returned ${response.status}: ${responseText}`
        )
      }

      const data = JSON.parse(responseText)

      setScanHistory(data.scans || [])
    } catch (error) {
      console.error('Scan History Error:', error)

      setHistoryError(
        `Unable to load scan history: ${error.message}`
      )
    } finally {
      setHistoryLoading(false)
    }
  }

  // ==============================
  // Load Scan History on startup
  // ==============================

  useEffect(() => {
    fetchScanHistory()
  }, [])

  // ==============================
  // Visible History
  // ==============================

  const visibleHistory = showAllHistory
    ? scanHistory
    : scanHistory.slice(0, 3)

  // ==============================
  // Status Class Helpers
  // ==============================

  const getSeverityClass = (severity) => {
    const value = (severity || '').toLowerCase().trim()

    if (value === 'high') {
      return 'status-badge status-high'
    }

    if (value === 'moderate') {
      return 'status-badge status-moderate'
    }

    if (value === 'low') {
      return 'status-badge status-low'
    }

    if (value === 'none') {
      return 'status-badge status-none'
    }

    return 'status-badge status-neutral'
  }

  const getRiskClass = (risk) => {
    const value = (risk || '').toLowerCase().trim()

    if (value === 'very high') {
      return 'status-badge status-very-high'
    }

    if (value === 'high') {
      return 'status-badge status-high'
    }

    if (value === 'moderate') {
      return 'status-badge status-moderate'
    }

    if (value === 'low') {
      return 'status-badge status-low'
    }

    return 'status-badge status-neutral'
  }

  const getPriorityClass = (priority) => {
    const value = (priority || '').toLowerCase().trim()

    if (value === 'urgent') {
      return 'status-badge status-urgent'
    }

    if (value === 'high') {
      return 'status-badge status-high'
    }

    if (value === 'moderate') {
      return 'status-badge status-moderate'
    }

    if (value === 'low') {
      return 'status-badge status-low'
    }

    return 'status-badge status-neutral'
  }

  // ==============================
  // File Selection
  // ==============================

  const handleFileChange = (event) => {
    const file = event.target.files[0]

    if (!file) {
      return
    }

    setSelectedFile(file)
    setPreview(URL.createObjectURL(file))
    setResult(null)
    setError('')
    setYieldResult(null)
    setYieldError('')

    setYieldForm((previous) => ({
      ...previous,
      crop: '',
      area: 'India',
      year: previous.year || '2026',
    }))
  }

  // ==============================
  // Disease Prediction
  // ==============================

  const handlePredict = async () => {
    if (!selectedFile) {
      setError('Please select a leaf image first.')
      return
    }

    setLoading(true)
    setResult(null)
    setError('')
    setYieldResult(null)
    setYieldError('')

    setYieldForm((previous) => ({
      ...previous,
      crop: '',
      area: 'India',
      year: previous.year || '2026',
    }))

    const formData = new FormData()

    formData.append('file', selectedFile)

    formData.append(
      'area',
      location.trim() || 'Chennai'
    )

    try {
      const response = await fetch(
        'http://127.0.0.1:8001/predict',
        {
          method: 'POST',
          body: formData,
        }
      )

      const responseText = await response.text()

      if (!response.ok) {
        throw new Error(
          `Server returned ${response.status}: ${responseText}`
        )
      }

      const data = JSON.parse(responseText)

      console.log('Prediction Result:', data)

      setResult(data)

      await fetchScanHistory()

      // ==============================
      // Low-confidence protection
      // ==============================

      const confidence = Number(
        data.confidence || 0
      )

      const isLowConfidence =
        confidence < 60 ||
        data.prediction === 'Unable to identify'

      if (isLowConfidence) {
        setYieldResult(null)

        setYieldForm({
          crop: '',
          area: 'India',
          year: '2026',
        })

        return
      }

      // ==============================
      // Automatically detect crop
      // ==============================

      const prediction = data.prediction || ''

      const cropName = prediction
        .split('___')[0]
        .replaceAll('_', ' ')
        .trim()

      let detectedCrop = ''

      if (
        cropName
          .toLowerCase()
          .includes('tomato')
      ) {
        detectedCrop = 'Tomato'
      } else if (
        cropName
          .toLowerCase()
          .includes('potato')
      ) {
        detectedCrop = 'Potato'
      } else if (
        cropName
          .toLowerCase()
          .includes('pepper')
      ) {
        detectedCrop = 'Pepper'
      }

      // ==============================
      // Disease → Yield connection
      // ==============================

      setYieldForm((previous) => ({
        ...previous,
        crop:
          detectedCrop ||
          previous.crop,
        area: 'India',
        year:
          previous.year ||
          '2026',
      }))

      // ==============================
      // Update disease scan location
      // ==============================

      if (data.area) {
        setLocation(data.area)
      }
    } catch (error) {
      console.error('Backend Error:', error)

      setError(
        `Backend Error: ${error.message}`
      )
    } finally {
      setLoading(false)
    }
  }

  // ==============================
  // Yield Form Change
  // ==============================

  const handleYieldChange = (event) => {
    const {
      name,
      value,
    } = event.target

    setYieldForm((previous) => ({
      ...previous,
      [name]: value,
    }))

    setYieldError('')
  }

  // ==============================
  // Yield Prediction
  // ==============================

  const handleYieldPredict = async () => {
    setYieldError('')
    setYieldResult(null)

    const {
      crop,
      area,
      year,
    } = yieldForm

    if (!crop || !area || !year) {
      setYieldError(
        'Please select a crop and fill in area and year.'
      )

      return
    }

    setYieldLoading(true)

    try {
      const url =
        `http://127.0.0.1:8001/predict-yield` +
        `?crop=${encodeURIComponent(crop)}` +
        `&area=${encodeURIComponent(area)}` +
        `&year=${encodeURIComponent(year)}`

      const response = await fetch(
        url,
        {
          method: 'POST',
        }
      )

      const responseText =
        await response.text()

      if (!response.ok) {
        throw new Error(
          `Server returned ${response.status}: ${responseText}`
        )
      }

      const data =
        JSON.parse(responseText)

      console.log(
        'Yield Prediction Result:',
        data
      )

      setYieldResult(data)
    } catch (error) {
      console.error(
        'Yield Backend Error:',
        error
      )

      setYieldError(
        `Yield Prediction Error: ${error.message}`
      )
    } finally {
      setYieldLoading(false)
    }
  }

  // ==============================
  // Low Confidence State
  // ==============================

  const isLowConfidence =
    result &&
    (
      Number(result.confidence || 0) < 60 ||
      result.prediction === 'Unable to identify'
    )

  // ==============================
  // Yield Loss Data
  // ==============================

  const yieldLoss =
    result?.yield_loss || null

  // ==============================
  // Disease Risk Data
  // ==============================

  const diseaseRisk =
    result?.disease_risk || null

  // ==============================
  // Treatment Priority Data
  // ==============================

  const treatmentPriority =
    result?.treatment_priority || null

  // ==============================
  // Helper: Crop Name
  // ==============================

  const getCropName = () => {
    if (!result || isLowConfidence) {
      return 'Unknown'
    }

    return (
      (result.prediction || '')
        .split('___')[0]
        ?.replaceAll('_', ' ') ||
      'Unknown'
    )
  }

  // ==============================
  // Helper: Disease Name
  // ==============================

  const getDiseaseName = () => {
    if (!result || isLowConfidence) {
      return 'Unknown'
    }

    return (
      (result.prediction || '')
        .split('___')[1]
        ?.replaceAll('_', ' ') ||
      'Unknown'
    )
  }

  // ==============================
  // Helper: History Disease Name
  // ==============================

  const formatHistoryDisease = (disease) => {
    if (!disease) {
      return 'Unknown'
    }

    const parts = disease.split('___')

    if (parts.length > 1) {
      return parts[1]
        .replaceAll('_', ' ')
        .replaceAll(',', '')
        .trim()
    }

    return disease
      .replaceAll('_', ' ')
      .replaceAll(',', '')
      .trim()
  }

  // ==============================
  // Helper: History Date
  // ==============================

  const formatHistoryDate = (date) => {
    if (!date) {
      return 'Unknown'
    }

    const parsedDate = new Date(
      date.replace(' ', 'T') + 'Z'
    )

    if (Number.isNaN(parsedDate.getTime())) {
      return date
    }

    return parsedDate.toLocaleString()
  }

  // ==============================
  // Helper: History Value
  // ==============================

  const displayHistoryValue = (value, suffix = '') => {
    if (
      value === null ||
      value === undefined ||
      value === ''
    ) {
      return 'Not available'
    }

    return `${value}${suffix}`
  }

  return (
    <div className="app">

      {/* ==============================
          Header
      ============================== */}

      <header className="header">

        <h1>
          🌱 AI Crop Disease & Yield Optimizer
        </h1>

        <p>
          AI-powered crop health analysis
        </p>

      </header>

      <main className="container">

        {/* ==================================================
            FARMER DASHBOARD
        ================================================== */}

        <section className="dashboard">

          <div className="dashboard-header">

            <div>

              <h2>
                📊 Farmer Dashboard
              </h2>

              <p>
                Quick overview of your crop health and
                yield analysis.
              </p>

            </div>

          </div>

          <div className="dashboard-grid">

            {/* Disease Status */}

            <div className="dashboard-card">

              <div className="dashboard-icon">
                🌿
              </div>

              <div>

                <span>
                  Disease Status
                </span>

                <strong>
                  {result
                    ? getDiseaseName()
                    : 'Not analyzed'}
                </strong>

              </div>

            </div>

            {/* AI Confidence */}

            <div className="dashboard-card">

              <div className="dashboard-icon">
                🎯
              </div>

              <div>

                <span>
                  AI Confidence
                </span>

                <strong>
                  {result
                    ? `${result.confidence}%`
                    : 'Not available'}
                </strong>

              </div>

            </div>

            {/* Disease Severity */}

            <div className="dashboard-card">

              <div className="dashboard-icon">
                ⚠️
              </div>

              <div>

                <span>
                  Disease Severity
                </span>

                {result && !isLowConfidence ? (
                  <strong
                    className={getSeverityClass(
                      result.severity
                    )}
                  >
                    {result.severity}
                  </strong>
                ) : (
                  <strong>
                    Not available
                  </strong>
                )}

              </div>

            </div>

            {/* Disease Risk */}

            <div className="dashboard-card">

              <div className="dashboard-icon">
                🚨
              </div>

              <div>

                <span>
                  Disease Risk
                </span>

                {result && !isLowConfidence ? (
                  <strong
                    className={getRiskClass(
                      diseaseRisk?.risk_level
                    )}
                  >
                    {diseaseRisk?.risk_level ||
                      'Not available'}
                  </strong>
                ) : (
                  <strong>
                    Not available
                  </strong>
                )}

              </div>

            </div>

            {/* Treatment Priority */}

            <div className="dashboard-card">

              <div className="dashboard-icon">
                🚨
              </div>

              <div>

                <span>
                  Treatment Priority
                </span>

                {result && !isLowConfidence ? (
                  <strong
                    className={getPriorityClass(
                      treatmentPriority?.priority_level
                    )}
                  >
                    {treatmentPriority?.priority_level ||
                      'Not available'}
                  </strong>
                ) : (
                  <strong>
                    Not available
                  </strong>
                )}

              </div>

            </div>

            {/* Temperature */}

            <div className="dashboard-card">

              <div className="dashboard-icon">
                🌦️
              </div>

              <div>

                <span>
                  Temperature
                </span>

                <strong>
                  {result?.weather && !isLowConfidence
                    ? `${result.weather.temperature}°C`
                    : 'Not available'}
                </strong>

              </div>

            </div>

            {/* Base Predicted Yield */}

            <div className="dashboard-card">

              <div className="dashboard-icon">
                🌾
              </div>

              <div>

                <span>
                  Base Predicted Yield
                </span>

                <strong>
                  {yieldLoss
                    ? `${yieldLoss.base_predicted_yield_kg_ha} kg/ha`
                    : yieldResult
                      ? `${yieldResult.predicted_yield_kg_ha} kg/ha`
                      : 'Not predicted'}
                </strong>

              </div>

            </div>

            {/* Estimated Yield Loss */}

            <div className="dashboard-card">

              <div className="dashboard-icon">
                📉
              </div>

              <div>

                <span>
                  Estimated Yield Loss
                </span>

                <strong>
                  {yieldLoss
                    ? `${yieldLoss.estimated_yield_loss_percentage}%`
                    : 'Not available'}
                </strong>

              </div>

            </div>

            {/* Adjusted Expected Yield */}

            <div className="dashboard-card">

              <div className="dashboard-icon">
                🌱
              </div>

              <div>

                <span>
                  Adjusted Expected Yield
                </span>

                <strong>
                  {yieldLoss
                    ? `${yieldLoss.adjusted_expected_yield_kg_ha} kg/ha`
                    : 'Not available'}
                </strong>

              </div>

            </div>

            {/* Location */}

            <div className="dashboard-card">

              <div className="dashboard-icon">
                🌍
              </div>

              <div>

                <span>
                  Location / Area
                </span>

                <strong>
                  {result?.area ||
                    location ||
                    'Not available'}
                </strong>

              </div>

            </div>

          </div>

        </section>

        {/* ==================================================
            SCAN HISTORY
        ================================================== */}

        <section className="card scan-history-section">

          <div className="history-header">

            <div>

              <h2>
                📜 Scan History
              </h2>

              <p>
                {scanHistory.length > 0
                  ? showAllHistory
                    ? `Showing all ${scanHistory.length} saved scans.`
                    : `Showing latest ${Math.min(
                        3,
                        scanHistory.length
                      )} scans.`
                  : 'View your previous crop disease analysis results.'}
              </p>

            </div>

            <button
              type="button"
              className="history-refresh-button"
              onClick={fetchScanHistory}
              disabled={historyLoading}
            >
              {historyLoading
                ? '🔄 Loading...'
                : '🔄 Refresh'}
            </button>

          </div>

          {historyError && (

            <p className="error">
              {historyError}
            </p>

          )}

          {historyLoading &&
            scanHistory.length === 0 && (

            <p>
              🔄 Loading scan history...
            </p>

          )}

          {!historyLoading &&
            !historyError &&
            scanHistory.length === 0 && (

            <div className="history-empty">

              <div className="upload-icon">
                📭
              </div>

              <p>
                No scan history available yet.
              </p>

              <span>
                Complete a crop disease scan to create history.
              </span>

            </div>

          )}

          {visibleHistory.length > 0 && (

            <div className="history-list">

              {visibleHistory.map((scan, index) => (

                <div
                  className="history-item"
                  key={scan.id}
                >

                  {/* History Item Header */}

                  <div className="history-item-header">

                    <div>

                      <h3>
                        🌱 {scan.crop}

                        {index === 0 && (
                          <span className="latest-scan-badge">
                            ✨ Latest Scan
                          </span>
                        )}

                      </h3>

                      <p>
                        {formatHistoryDisease(
                          scan.disease
                        )}
                      </p>

                    </div>

                    <span className="history-date">
                      {formatHistoryDate(
                        scan.created_at
                      )}
                    </span>

                  </div>

                  {/* History Details */}

                  <div className="history-grid">

                    <div className="history-detail">

                      <span>
                        🎯 Confidence
                      </span>

                      <strong>
                        {displayHistoryValue(
                          scan.confidence,
                          '%'
                        )}
                      </strong>

                    </div>

                    <div className="history-detail">

                      <span>
                        ⚠️ Severity
                      </span>

                      <strong
                        className={
                          scan.severity
                            ? getSeverityClass(scan.severity)
                            : 'status-badge status-neutral'
                        }
                      >
                        {displayHistoryValue(
                          scan.severity
                        )}
                      </strong>

                    </div>

                    <div className="history-detail">

                      <span>
                        🌿 Affected Area
                      </span>

                      <strong>
                        {displayHistoryValue(
                          scan.affected_area,
                          '%'
                        )}
                      </strong>

                    </div>

                    <div className="history-detail">

                      <span>
                        🚨 Disease Risk
                      </span>

                      <strong
                        className={
                          scan.risk_level
                            ? getRiskClass(scan.risk_level)
                            : 'status-badge status-neutral'
                        }
                      >
                        {displayHistoryValue(
                          scan.risk_level
                        )}
                      </strong>

                    </div>

                    <div className="history-detail">

                      <span>
                        🚨 Treatment Priority
                      </span>

                      <strong
                        className={
                          scan.treatment_priority
                            ? getPriorityClass(
                                scan.treatment_priority
                              )
                            : 'status-badge status-neutral'
                        }
                      >
                        {displayHistoryValue(
                          scan.treatment_priority
                        )}
                      </strong>

                    </div>

                    <div className="history-detail">

                      <span>
                        🌡️ Temperature
                      </span>

                      <strong>
                        {displayHistoryValue(
                          scan.temperature,
                          '°C'
                        )}
                      </strong>

                    </div>

                    <div className="history-detail">

                      <span>
                        💧 Humidity
                      </span>

                      <strong>
                        {displayHistoryValue(
                          scan.humidity,
                          '%'
                        )}
                      </strong>

                    </div>

                    <div className="history-detail">

                      <span>
                        📍 Location
                      </span>

                      <strong>
                        {displayHistoryValue(
                          scan.location
                        )}
                      </strong>

                    </div>

                    <div className="history-detail">

                      <span>
                        🌾 Base Yield
                      </span>

                      <strong>
                        {scan.base_yield !== null &&
                        scan.base_yield !== undefined
                          ? `${scan.base_yield} kg/ha`
                          : 'Not available'}
                      </strong>

                    </div>

                    <div className="history-detail">

                      <span>
                        📉 Yield Loss
                      </span>

                      <strong>
                        {scan.yield_loss_percentage !== null &&
                        scan.yield_loss_percentage !== undefined
                          ? `${scan.yield_loss_percentage}%`
                          : 'Not available'}
                      </strong>

                    </div>

                    <div className="history-detail">

                      <span>
                        🌱 Adjusted Yield
                      </span>

                      <strong>
                        {scan.adjusted_yield !== null &&
                        scan.adjusted_yield !== undefined
                          ? `${scan.adjusted_yield} kg/ha`
                          : 'Not available'}
                      </strong>

                    </div>

                  </div>

                </div>

              ))}

            </div>

          )}

          {scanHistory.length > 3 && (

            <div className="history-toggle-container">

              <button
                type="button"
                className="history-view-button"
                onClick={() =>
                  setShowAllHistory(
                    (previous) => !previous
                  )
                }
              >
                {showAllHistory
                  ? '⬆️ Show Latest 3'
                  : `📂 View All History (${scanHistory.length})`}
              </button>

            </div>

          )}

        </section>

        {/* ==================================================
            DISEASE DETECTION
        ================================================== */}

        <section className="hero">

          <h2>
            Detect Crop Disease with AI
          </h2>

          <p>
            Upload a crop leaf image and our MobileNet AI model
            will identify the possible disease.
          </p>

        </section>

        {/* ==================================================
            IMPROVED UPLOAD CARD
        ================================================== */}

        <section className="card upload-card">

          <div className="upload-card-header">

            <div className="upload-title-icon">
              📷
            </div>

            <div>

              <h2>
                Upload Crop Leaf
              </h2>

              <p>
                Choose a clear leaf image for AI disease analysis.
              </p>

            </div>

          </div>

          <label className="upload-box">

            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
            />

            {preview ? (

              <div className="preview-wrapper">

                <img
                  src={preview}
                  alt="Selected crop leaf"
                  className="preview"
                />

                <div className="preview-overlay">
                  <span>
                    🔄 Choose another image
                  </span>
                </div>

              </div>

            ) : (

              <div className="upload-placeholder">

                <div className="upload-icon">
                  🌿
                </div>

                <h3>
                  Click to choose a leaf image
                </h3>

                <p>
                  Upload a clear photo of the crop leaf
                </p>

                <span className="upload-formats">
                  JPG • JPEG • PNG
                </span>

              </div>

            )}

          </label>

          {selectedFile && (

            <div className="selected-file-card">

              <div className="selected-file-icon">
                🖼️
              </div>

              <div className="selected-file-info">

                <span>
                  Selected image
                </span>

                <strong>
                  {selectedFile.name}
                </strong>

              </div>

            </div>

          )}

          {/* Location */}

          <div className="form-group">

            <label>
              📍 Farmer Location
            </label>

            <input
              type="text"
              value={location}
              placeholder="Example: Chennai, Salem, Coimbatore"
              onChange={(event) =>
                setLocation(event.target.value)
              }
              className="location-input"
            />

            <small className="input-hint">
              Leave empty to use Chennai as the default location.
            </small>

          </div>

          {/* Predict Button */}

          <button
            type="button"
            className="predict-button"
            onClick={handlePredict}
            disabled={loading}
          >

            {loading
              ? '🔄 Analyzing Leaf...'
              : '🔍 Detect Disease'}

          </button>

          {error && (

            <p className="error">
              {error}
            </p>

          )}

        </section>

        {/* ==================================================
            LOW CONFIDENCE WARNING
        ================================================== */}

        {isLowConfidence && (

          <section className="result-card">

            <h2>
              ⚠️ Image Could Not Be Confidently Identified
            </h2>

            <div className="result-item">

              <span>
                AI Confidence
              </span>

              <strong>
                {result.confidence}%
              </strong>

            </div>

            <p>
              The uploaded image does not appear to be a
              confidently identifiable tomato, potato, or
              pepper leaf.
            </p>

            <p>
              Please upload a clear leaf image and try again.
            </p>

          </section>

        )}

        {/* ==================================================
            NORMAL DISEASE RESULT
        ================================================== */}

        {result && !isLowConfidence && (

          <section className="result-card">

            <h2>
              🔬 Prediction Result
            </h2>

            <div className="result-item">

              <span>
                Crop
              </span>

              <strong>
                {getCropName()}
              </strong>

            </div>

            <div className="result-item">

              <span>
                Disease
              </span>

              <strong>
                {getDiseaseName()}
              </strong>

            </div>

            <div className="result-item">

              <span>
                Confidence
              </span>

              <strong>
                {result.confidence}%
              </strong>

            </div>

            <div className="result-item">

              <span>
                Severity
              </span>

              <strong
                className={getSeverityClass(
                  result.severity
                )}
              >
                {result.severity}
              </strong>

            </div>

            {result.affected_area !== undefined && (

              <div className="result-item">

                <span>
                  Affected Area
                </span>

                <strong>
                  {result.affected_area}%
                </strong>

              </div>

            )}

            {/* Disease Risk */}

            {diseaseRisk && (

              <div className="yield-loss-section">

                <h2>
                  🚨 Disease Risk & Early Warning
                </h2>

                <p>
                  The current disease severity and weather
                  conditions are used to estimate the present
                  disease risk.
                </p>

                <div className="result-item">

                  <span>
                    Risk Level
                  </span>

                  <strong
                    className={getRiskClass(
                      diseaseRisk.risk_level
                    )}
                  >
                    {diseaseRisk.risk_level}
                  </strong>

                </div>

                <div className="result-item">

                  <span>
                    Risk Score
                  </span>

                  <strong>
                    {diseaseRisk.risk_score}/100
                  </strong>

                </div>

                {diseaseRisk.reason && (

                  <div className="recommendation-list">

                    <h3>
                      ⚠️ Why is the risk at this level?
                    </h3>

                    <p>
                      {diseaseRisk.reason}
                    </p>

                  </div>

                )}

              </div>

            )}

            {/* Treatment Priority */}

            {treatmentPriority && (

              <div className="yield-loss-section">

                <h2>
                  🚨 Treatment Priority
                </h2>

                <p>
                  This priority score combines AI confidence,
                  disease severity, affected leaf area and
                  estimated disease risk.
                </p>

                <div className="result-item">

                  <span>
                    Priority Level
                  </span>

                  <strong
                    className={getPriorityClass(
                      treatmentPriority.priority_level
                    )}
                  >
                    {treatmentPriority.priority_level}
                  </strong>

                </div>

                <div className="result-item">

                  <span>
                    Priority Score
                  </span>

                  <strong>
                    {treatmentPriority.priority_score}/100
                  </strong>

                </div>

                {treatmentPriority.action && (

                  <div className="recommendation-list">

                    <h3>
                      ⚠️ Recommended Action
                    </h3>

                    <p>
                      {treatmentPriority.action}
                    </p>

                  </div>

                )}

                <p className="recommendation-note">
                  ℹ️ This is a heuristic priority estimate
                  designed to help prioritize crop inspection
                  and management. It is not an agricultural
                  ground-truth measurement.
                </p>

              </div>

            )}

            {/* Yield Loss Analysis */}

            {yieldLoss && (

              <div className="yield-loss-section">

                <h2>
                  📉 Disease Impact on Yield
                </h2>

                <p>
                  The estimated disease severity has been used
                  to calculate the possible impact on crop yield.
                </p>

                <div className="result-item">

                  <span>
                    Base Predicted Yield
                  </span>

                  <strong>
                    {yieldLoss.base_predicted_yield_kg_ha} kg/ha
                  </strong>

                </div>

                <div className="result-item">

                  <span>
                    Estimated Yield Loss
                  </span>

                  <strong>
                    {yieldLoss.estimated_yield_loss_percentage}%
                  </strong>

                </div>

                <div className="result-item">

                  <span>
                    Estimated Loss
                  </span>

                  <strong>
                    {yieldLoss.estimated_yield_loss_kg_ha} kg/ha
                  </strong>

                </div>

                <div className="result-item">

                  <span>
                    Adjusted Expected Yield
                  </span>

                  <strong>
                    {yieldLoss.adjusted_expected_yield_kg_ha} kg/ha
                  </strong>

                </div>

                <p className="recommendation-note">
                  ℹ️ This is an estimated disease-related yield
                  impact based on the current severity level.
                  Actual farm yield may vary depending on crop
                  variety, field conditions, weather and management.
                </p>

              </div>

            )}

            {/* Weather */}

            {result.weather && (

              <div className="weather-section">

                <h2>
                  🌦️ Weather Conditions
                </h2>

                <div className="result-item">

                  <span>
                    Temperature
                  </span>

                  <strong>
                    {result.weather.temperature}°C
                  </strong>

                </div>

                <div className="result-item">

                  <span>
                    Humidity
                  </span>

                  <strong>
                    {result.weather.humidity}%
                  </strong>

                </div>

                <div className="result-item">

                  <span>
                    Rainfall
                  </span>

                  <strong>
                    {result.weather.rainfall} mm
                  </strong>

                </div>

                <div className="result-item">

                  <span>
                    Condition
                  </span>

                  <strong>
                    {result.weather.condition}
                  </strong>

                </div>

              </div>

            )}

            {/* Treatment Recommendation */}

            {result.recommendation && (

              <div className="recommendation-section">

                <h2>
                  💊 Treatment Recommendation
                </h2>

                <div className="result-item">

                  <span>
                    Management Level
                  </span>

                  <strong
                    className={getPriorityClass(
                      result.recommendation.priority
                    )}
                  >
                    {result.recommendation.priority}
                  </strong>

                </div>

                <div className="recommendation-urgency">

                  <strong>
                    ⚠️ {result.recommendation.urgency}
                  </strong>

                </div>

                {result.recommendation.actions &&
                  result.recommendation.actions.length > 0 && (

                  <div className="recommendation-list">

                    <h3>
                      🌿 Recommended Actions
                    </h3>

                    <ul>

                      {result.recommendation.actions.map(
                        (action, index) => (

                          <li key={index}>
                            {action}
                          </li>

                        )
                      )}

                    </ul>

                  </div>

                )}

                {result.recommendation.prevention &&
                  result.recommendation.prevention.length > 0 && (

                  <div className="recommendation-list">

                    <h3>
                      🛡️ Prevention
                    </h3>

                    <ul>

                      {result.recommendation.prevention.map(
                        (item, index) => (

                          <li key={index}>
                            {item}
                          </li>

                        )
                      )}

                    </ul>

                  </div>

                )}

                {result.recommendation.weather_advice &&
                  result.recommendation.weather_advice.length > 0 && (

                  <div className="recommendation-list">

                    <h3>
                      🌦️ Weather Advice
                    </h3>

                    <ul>

                      {result.recommendation.weather_advice.map(
                        (advice, index) => (

                          <li key={index}>
                            {advice}
                          </li>

                        )
                      )}

                    </ul>

                  </div>

                )}

                <p className="recommendation-note">
                  ℹ️ These are general crop-management suggestions.
                  Follow locally approved agricultural guidance and
                  product labels before applying any pesticide or treatment.
                </p>

              </div>

            )}

            {/* Confidence Bar */}

            <div className="confidence-bar">

              <div
                className="confidence-fill"
                style={{
                  width: `${result.confidence}%`,
                }}
              ></div>

            </div>

            {/* Grad-CAM */}

            <div className="gradcam-section">

              <h2>
                🔥 AI Attention Map
              </h2>

              <p>
                The highlighted areas show which parts
                of the leaf influenced the AI prediction.
              </p>

              <a
                href="http://127.0.0.1:8001/gradcam/gradcam_result.jpg"
                target="_blank"
                rel="noopener noreferrer"
              >

                <img
                  src="http://127.0.0.1:8001/gradcam/gradcam_result.jpg"
                  alt="Grad-CAM AI attention map"
                  className="gradcam-image"
                />

              </a>

            </div>

            <p className="success">
              ✅ AI prediction completed successfully
            </p>

          </section>

        )}

        {/* ==================================================
            YIELD PREDICTOR
        ================================================== */}

        <section className="card yield-card">

          <h2>
            🌾 Crop Yield Predictor
          </h2>

          <p>
            Select the crop and enter a FAOSTAT-supported
            area/country and year to estimate crop yield.
          </p>

          {/* Crop */}

          <div className="form-group">

            <label>
              🌱 Crop
            </label>

            <select
              name="crop"
              value={yieldForm.crop}
              onChange={handleYieldChange}
            >

              <option value="">
                Select Crop
              </option>

              <option value="Tomato">
                Tomato
              </option>

              <option value="Potato">
                Potato
              </option>

              <option value="Pepper">
                Pepper
              </option>

            </select>

          </div>

          {/* Area */}

          <div className="form-group">

            <label>
              🌍 Yield Area / Country
            </label>

            <input
              type="text"
              name="area"
              placeholder="Example: India"
              value={yieldForm.area}
              onChange={handleYieldChange}
            />

          </div>

          {/* Year */}

          <div className="form-group">

            <label>
              📅 Year
            </label>

            <input
              type="number"
              name="year"
              placeholder="Example: 2026"
              value={yieldForm.year}
              onChange={handleYieldChange}
            />

          </div>

          {/* Yield Error */}

          {yieldError && (

            <p className="error">
              {yieldError}
            </p>

          )}

          {/* Yield Button */}

          <button
            type="button"
            className="predict-button"
            onClick={handleYieldPredict}
            disabled={yieldLoading}
          >

            {yieldLoading
              ? '🔄 Predicting Yield...'
              : '🌾 Predict Crop Yield'}

          </button>

          {/* Yield Result */}

          {yieldResult && (

            <div className="yield-result">

              <h2>
                📊 Yield Prediction Result
              </h2>

              <div className="result-item">

                <span>
                  Crop
                </span>

                <strong>
                  {yieldResult.crop}
                </strong>

              </div>

              <div className="result-item">

                <span>
                  Area
                </span>

                <strong>
                  {yieldResult.area}
                </strong>

              </div>

              <div className="result-item">

                <span>
                  Predicted Yield
                </span>

                <strong>
                  {yieldResult.predicted_yield_kg_ha} kg/ha
                </strong>

              </div>

              <p className="success">
                ✅ Yield prediction completed successfully
              </p>

            </div>

          )}

        </section>

      </main>

    </div>
  )
}

export default App