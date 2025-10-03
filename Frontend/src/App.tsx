import { useState, useRef } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000'

type FileType = 'image' | 'video' | null

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fileType, setFileType] = useState<FileType>(null)
  const [previewUrl, setPreviewUrl] = useState<string>('')
  const [resultUrl, setResultUrl] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Reset states
    setError('')
    setResultUrl('')
    
    // Determine file type
    const type = file.type.startsWith('image/') ? 'image' : 
                 file.type.startsWith('video/') ? 'video' : null

    if (!type) {
      setError('Please select a valid image or video file')
      return
    }

    setSelectedFile(file)
    setFileType(type)
    
    // Create preview URL
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
  }

  const handleDetect = async () => {
    if (!selectedFile || !fileType) return

    setIsLoading(true)
    setError('')
    setResultUrl('')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const endpoint = fileType === 'image' ? '/detect/image' : '/detect/video'
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Detection failed: ${response.statusText}`)
      }

      // Create blob URL for the result
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      setResultUrl(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during detection')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setFileType(null)
    setPreviewUrl('')
    setResultUrl('')
    setError('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleDownload = () => {
    if (!resultUrl) return
    
    const a = document.createElement('a')
    a.href = resultUrl
    a.download = `detected_${selectedFile?.name || 'result'}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🥭 Mango Detection</h1>
          <p>Upload an image or video to detect ripe and unripe mangoes</p>
        </header>

        <div className="upload-section">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,video/*"
            onChange={handleFileSelect}
            className="file-input"
            id="file-input"
          />
          <label htmlFor="file-input" className="file-label">
            <span className="upload-icon">📁</span>
            <span>Choose Image or Video</span>
          </label>
          
          {selectedFile && (
            <div className="file-info">
              <span className="file-name">{selectedFile.name}</span>
              <span className="file-type">{fileType?.toUpperCase()}</span>
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {previewUrl && !resultUrl && (
          <div className="preview-section">
            <h3>Preview</h3>
            <div className="media-container">
              {fileType === 'image' ? (
                <img src={previewUrl} alt="Preview" className="preview-media" />
              ) : (
                <video src={previewUrl} controls className="preview-media" />
              )}
            </div>
            <div className="button-group">
              <button 
                onClick={handleDetect} 
                disabled={isLoading}
                className="btn btn-primary"
              >
                {isLoading ? 'Processing...' : '🔍 Detect Mangoes'}
              </button>
              <button onClick={handleReset} className="btn btn-secondary">
                🔄 Reset
              </button>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Processing your {fileType}... This may take a moment.</p>
          </div>
        )}

        {resultUrl && (
          <div className="result-section">
            <h3>Detection Result</h3>
            <div className="media-container">
              {fileType === 'image' ? (
                <img src={resultUrl} alt="Detection Result" className="result-media" />
              ) : (
                <video src={resultUrl} controls className="result-media" />
              )}
            </div>
            <div className="button-group">
              <button onClick={handleDownload} className="btn btn-success">
                💾 Download Result
              </button>
              <button onClick={handleReset} className="btn btn-secondary">
                🔄 Process Another
              </button>
            </div>
          </div>
        )}

        {!selectedFile && !isLoading && (
          <div className="instructions">
            <h3>How to use:</h3>
            <ol>
              <li>Click "Choose Image or Video" to select a file</li>
              <li>Preview your selection</li>
              <li>Click "Detect Mangoes" to run the detection</li>
              <li>View the results with bounding boxes around detected mangoes</li>
              <li>Download or process another file</li>
            </ol>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
