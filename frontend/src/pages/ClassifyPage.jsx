import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUploadCloud, FiX, FiAlertCircle, FiImage, FiCamera, FiRefreshCw } from 'react-icons/fi';
import axios from 'axios';

const ClassifyPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Mode state: 'upload' or 'camera'
  const [inputMode, setInputMode] = useState('upload');
  
  // Images state
  const [images, setImages] = useState([]);
  const [previews, setPreviews] = useState([]);

  // Camera state
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [availableCameras, setAvailableCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState('');
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [stream, setStream] = useState(null);
  const [isVideoReady, setIsVideoReady] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const imageLabels = ['View 1', 'View 2', 'View 3', 'View 4', 'View 5'];

  // Get available cameras on mount
  const isInitialMount = useRef(true);
  const shouldAutoStart = useRef(false);
  
  // Callback ref for video element to detect when it's mounted
  const setVideoRef = (element) => {
    videoRef.current = element;
    if (element) {
      console.log('Video element mounted');
      setIsVideoReady(true);
    } else {
      console.log('Video element unmounted');
      setIsVideoReady(false);
    }
  };
  
  // Get cameras when switching to camera mode
  useEffect(() => {
    if (inputMode === 'camera') {
      shouldAutoStart.current = true;
      getCameras();
    } else {
      isInitialMount.current = true;
      shouldAutoStart.current = false;
      setIsVideoReady(false);
    }
    return () => {
      stopCamera();
    };
  }, [inputMode]);

  // Auto-start camera when video element is ready
  useEffect(() => {
    if (inputMode === 'camera' && isVideoReady && shouldAutoStart.current && !isCameraActive) {
      console.log('Video element is ready, starting camera...');
      shouldAutoStart.current = false;
      if (isInitialMount.current) {
        isInitialMount.current = false;
      }
      // Small delay to ensure everything is settled
      setTimeout(() => {
        startCamera();
      }, 200);
    }
  }, [inputMode, isVideoReady, isCameraActive]);

  // Restart camera when selectedCamera changes (for camera switching)
  useEffect(() => {
    // Only restart if we're not on initial mount and camera is active
    if (!isInitialMount.current && inputMode === 'camera' && isCameraActive && selectedCamera) {
      const restartCamera = async () => {
        stopCamera();
        await new Promise(resolve => setTimeout(resolve, 100));
        startCamera();
      };
      restartCamera();
    }
  }, [selectedCamera]);

  const getCameras = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      setAvailableCameras(videoDevices);
      if (videoDevices.length > 0 && !selectedCamera) {
        setSelectedCamera(videoDevices[0].deviceId);
      }
    } catch (err) {
      console.error('Error getting cameras:', err);
      setError('Failed to access camera devices. Please check permissions.');
    }
  };

  const startCamera = async () => {
    try {
      stopCamera(); // Stop any existing stream
      
      console.log('Starting camera with device:', selectedCamera);
      console.log('Video element ready:', !!videoRef.current);
      
      const constraints = {
        video: {
          deviceId: selectedCamera ? { exact: selectedCamera } : undefined,
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      console.log('Media stream obtained:', mediaStream);
      console.log('Video tracks:', mediaStream.getVideoTracks());
      
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        
        // Wait for metadata to load before playing
        videoRef.current.onloadedmetadata = () => {
          console.log('Video metadata loaded, starting playback');
          videoRef.current.play()
            .then(() => {
              console.log('Video playing successfully');
              setIsCameraActive(true);
              setError(null);
            })
            .catch(playErr => {
              console.error('Error playing video:', playErr);
              setError('Failed to play video stream.');
              setIsCameraActive(false);
            });
        };
      } else {
        console.error('Video element not found');
        setError('Video element not ready. Please try again.');
        setIsCameraActive(false);
      }
      
    } catch (err) {
      console.error('Error starting camera:', err);
      let errorMessage = 'Failed to start camera.';
      
      if (err.name === 'NotAllowedError') {
        errorMessage = 'Camera access denied. Please allow camera permissions.';
      } else if (err.name === 'NotFoundError') {
        errorMessage = 'No camera found. Please connect a camera.';
      } else if (err.name === 'NotReadableError') {
        errorMessage = 'Camera is already in use by another application.';
      } else if (err.name === 'OverconstrainedError') {
        errorMessage = 'Camera does not support the requested settings.';
      }
      
      setError(errorMessage);
      setIsCameraActive(false);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  };

  const captureImage = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `${imageLabels[currentImageIndex]}.jpg`, { type: 'image/jpeg' });
        const preview = URL.createObjectURL(blob);
        
        setImages(prev => [...prev, file]);
        setPreviews(prev => [...prev, preview]);
        
        if (currentImageIndex < 4) {
          setCurrentImageIndex(prev => prev + 1);
        } else {
          stopCamera();
          setCurrentImageIndex(0);
        }
        setError(null);
      }
    }, 'image/jpeg', 0.95);
  };

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files);
    
    if (files.length !== 5) {
      setError("Please select exactly 5 images");
      return;
    }
    
    setImages(files);
    const newPreviews = files.map(file => URL.createObjectURL(file));
    setPreviews(newPreviews);
    setError(null);
  };

  const removeImage = (index) => {
    const newImages = images.filter((_, i) => i !== index);
    const newPreviews = previews.filter((_, i) => i !== index);
    setImages(newImages);
    setPreviews(newPreviews);
    
    if (inputMode === 'camera' && newImages.length < 5) {
      setCurrentImageIndex(newImages.length);
    }
  };

  const changeInputMode = (mode) => {
    setInputMode(mode);
    setImages([]);
    setPreviews([]);
    setCurrentImageIndex(0);
    setError(null);
    stopCamera();
  };

  const handleCameraChange = (e) => {
    setSelectedCamera(e.target.value);
    // Camera restart is now handled by useEffect watching selectedCamera
  };

  const validateForm = () => {
    if (images.length !== 5) {
      setError("Please capture or upload exactly 5 images.");
      return false;
    }
    setError(null);
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setError(null);

    try {
      const createResponse = await axios.post('http://127.0.0.1:8000/api/v1/classification/create', {});
      if (!createResponse.data.success) throw new Error("Failed to create record");
      
      const classificationId = createResponse.data.data.id;

      const imageFormData = new FormData();
      images.forEach(image => {
        imageFormData.append('images', image);
      });

      const uploadResponse = await axios.post(
        `http://127.0.0.1:8000/api/v1/classification/${classificationId}/upload-images`,
        imageFormData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      if (!uploadResponse.data.success) throw new Error("Failed to upload images");

      const processResponse = await axios.post(
        `http://127.0.0.1:8000/api/v1/classification/${classificationId}/process`
      );

      if (processResponse.data.success) {
        navigate(`/classification/${classificationId}`);
      } else {
        throw new Error("Processing failed");
      }

    } catch (err) {
      console.error("Classification error:", err);
      let errorMessage = "An unexpected error occurred.";
      
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          errorMessage = detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ');
        } else if (typeof detail === 'object') {
          errorMessage = JSON.stringify(detail);
        } else {
          errorMessage = detail;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pt-20">
      {/* Header */}
      <section className="bg-gradient-to-r from-slate-900 to-slate-800 text-white py-16 border-b-4 border-orange-500">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center">
            <p className="text-xs font-bold tracking-widest uppercase text-gray-400 mb-4">Official Type Evaluation System</p>
            <h1 className="text-5xl md:text-6xl font-bold mb-6 tracking-tight">Classify Livestock</h1>
            <p className="text-lg text-gray-300 leading-relaxed max-w-2xl mx-auto font-medium">
              Upload 5 standardized images or capture them live for comprehensive type score analysis following the official Annex II format with 20 traits across 5 sections.
            </p>
          </div>
        </div>
      </section>

      {/* Form Section */}
      <section className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="space-y-8">
            
            {/* Mode Selection */}
            <div className="bg-white border-2 border-gray-200 p-6">
              <h3 className="text-sm font-bold uppercase tracking-wide mb-4 text-gray-700">Select Input Method</h3>
              <div className="grid grid-cols-2 gap-4">
                <button
                  type="button"
                  onClick={() => changeInputMode('upload')}
                  className={`p-6 border-2 transition-all ${
                    inputMode === 'upload'
                      ? 'border-orange-500 bg-orange-50'
                      : 'border-gray-300 bg-white hover:border-gray-400'
                  }`}
                >
                  <FiUploadCloud className={`w-8 h-8 mx-auto mb-3 ${inputMode === 'upload' ? 'text-orange-500' : 'text-gray-400'}`} />
                  <p className={`font-bold text-sm uppercase ${inputMode === 'upload' ? 'text-orange-600' : 'text-gray-600'}`}>
                    Upload Files
                  </p>
                </button>
                <button
                  type="button"
                  onClick={() => changeInputMode('camera')}
                  className={`p-6 border-2 transition-all ${
                    inputMode === 'camera'
                      ? 'border-orange-500 bg-orange-50'
                      : 'border-gray-300 bg-white hover:border-gray-400'
                  }`}
                >
                  <FiCamera className={`w-8 h-8 mx-auto mb-3 ${inputMode === 'camera' ? 'text-orange-500' : 'text-gray-400'}`} />
                  <p className={`font-bold text-sm uppercase ${inputMode === 'camera' ? 'text-orange-600' : 'text-gray-600'}`}>
                    Use Camera
                  </p>
                </button>
              </div>
            </div>

            {/* Upload Mode */}
            {inputMode === 'upload' && (
              <div className="bg-white border-2 border-gray-200 overflow-hidden">
                <div className="bg-slate-900 text-white px-8 py-6 border-b-4 border-orange-500">
                  <h2 className="text-xl font-bold uppercase tracking-wide">Upload Images</h2>
                  <p className="text-sm text-gray-300 mt-2 font-medium">Select 5 images at once</p>
                </div>

                <div className="p-8">
                  {images.length === 0 ? (
                    <div className="relative">
                      <input
                        type="file"
                        accept="image/*"
                        multiple
                        onChange={handleImageSelect}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                      />
                      <div className="border-4 border-dashed border-gray-400 hover:border-orange-500 transition-all bg-white p-16 text-center cursor-pointer">
                        <div className="flex flex-col items-center">
                          <div className="w-24 h-24 bg-orange-50 flex items-center justify-center mb-6 border-2 border-orange-500">
                            <FiUploadCloud className="w-12 h-12 text-orange-500" />
                          </div>
                          <h3 className="text-2xl font-bold text-gray-900 mb-3 uppercase tracking-wide">Drop Images Here</h3>
                          <p className="text-lg text-gray-600 mb-6 font-medium">or click to browse</p>
                          <div className="flex items-center gap-3 text-sm font-bold text-gray-700 uppercase">
                            <span className="px-6 py-3 bg-orange-500 text-white border-b-2 border-orange-700">Select 5 Images</span>
                            <span className="text-gray-500 font-semibold">JPG, PNG, JPEG</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="flex items-center justify-between mb-6 pb-4 border-b-2 border-gray-200">
                        <div className="flex items-center gap-3">
                          <FiImage className="w-6 h-6 text-orange-500" />
                          <span className="text-lg font-bold text-gray-900 uppercase tracking-wide">{images.length} Images Selected</span>
                        </div>
                        <button
                          type="button"
                          onClick={() => {
                            setImages([]);
                            setPreviews([]);
                          }}
                          className="px-6 py-2 bg-red-500 text-white font-bold uppercase text-sm hover:bg-red-600 transition-colors border-b-2 border-red-700"
                        >
                          Clear All
                        </button>
                      </div>
                      
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        {previews.map((preview, index) => (
                          <div key={index} className="relative group">
                            <div className="aspect-square bg-gray-200 border-2 border-gray-300 overflow-hidden relative">
                              <img
                                src={preview}
                                alt={`Upload ${index + 1}`}
                                className="w-full h-full object-cover"
                              />
                              <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                <button
                                  type="button"
                                  onClick={() => removeImage(index)}
                                  className="w-12 h-12 bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition-colors border-2 border-red-700"
                                >
                                  <FiX className="w-6 h-6" />
                                </button>
                              </div>
                            </div>
                            <div className="mt-2 text-center">
                              <span className="text-sm font-bold text-gray-700 uppercase">{imageLabels[index]}</span>
                            </div>
                          </div>
                        ))}
                      </div>

                      <div className="mt-6 text-center pt-6 border-t-2 border-gray-200">
                        <label className="inline-block cursor-pointer">
                          <input
                            type="file"
                            accept="image/*"
                            multiple
                            onChange={handleImageSelect}
                            className="hidden"
                          />
                          <span className="px-8 py-3 bg-gray-500 text-white font-bold uppercase text-sm hover:bg-gray-600 transition-colors inline-block border-b-2 border-gray-700">
                            Change Images
                          </span>
                        </label>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Camera Mode */}
            {inputMode === 'camera' && (
              <div className="bg-white border-2 border-gray-200 overflow-hidden">
                <div className="bg-slate-900 text-white px-8 py-6 border-b-4 border-orange-500">
                  <h2 className="text-xl font-bold uppercase tracking-wide">Capture Images</h2>
                  <p className="text-sm text-gray-300 mt-2 font-medium">
                    {images.length < 5 
                      ? `Capture ${imageLabels[currentImageIndex]} (${currentImageIndex + 1} of 5)`
                      : 'All 5 images captured successfully'}
                  </p>
                </div>

                <div className="p-8 space-y-6">
                  {/* Camera Selection */}
                  {availableCameras.length > 0 && (
                    <div>
                      <label className="block text-sm font-bold text-gray-700 uppercase mb-2">Select Camera</label>
                      <select
                        value={selectedCamera}
                        onChange={handleCameraChange}
                        className="w-full px-4 py-3 border-2 border-gray-300 bg-white font-medium text-sm"
                      >
                        {availableCameras.map((camera, index) => (
                          <option key={camera.deviceId} value={camera.deviceId}>
                            {camera.label || `Camera ${index + 1}`}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Camera Preview */}
                  {images.length < 5 && (
                    <div>
                      {/* Video element - always rendered but hidden when not active */}
                      <div className="relative">
                        <div className={`relative border-2 border-gray-300 bg-black overflow-hidden ${!isCameraActive ? 'hidden' : ''}`}>
                          <video
                            ref={setVideoRef}
                            autoPlay
                            playsInline
                            muted
                            className="w-full h-auto"
                            style={{ minHeight: '300px' }}
                          />
                          <div className="absolute top-4 left-4 px-4 py-2 bg-orange-500 text-white font-bold text-sm uppercase">
                            {imageLabels[currentImageIndex]}
                          </div>
                        </div>
                        <canvas ref={canvasRef} className="hidden" />
                        
                        {/* Start Camera Button - shown when camera is not active */}
                        {!isCameraActive && (
                          <div className="border-2 border-gray-300 bg-gray-100 p-16 text-center">
                            <FiCamera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-600 font-medium mb-6">Camera is not active</p>
                            <button
                              type="button"
                              onClick={startCamera}
                              className="px-8 py-3 bg-orange-500 text-white font-bold uppercase text-sm hover:bg-orange-600 transition-colors border-b-2 border-orange-700"
                            >
                              Start Camera
                            </button>
                          </div>
                        )}
                        
                        {/* Camera Controls - shown when camera is active */}
                        {isCameraActive && (
                          <div className="flex gap-4 mt-4">
                            <button
                              type="button"
                              onClick={captureImage}
                              className="flex-1 px-8 py-4 bg-green-500 text-white font-bold uppercase text-sm hover:bg-green-600 transition-colors border-b-2 border-green-700 flex items-center justify-center gap-2"
                            >
                              <FiCamera className="w-5 h-5" />
                              Capture Image
                            </button>
                            <button
                              type="button"
                              onClick={stopCamera}
                              className="px-8 py-4 bg-gray-500 text-white font-bold uppercase text-sm hover:bg-gray-600 transition-colors border-b-2 border-gray-700"
                            >
                              Stop Camera
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Captured Images Preview */}
                  {images.length > 0 && (
                    <div>
                      <div className="flex items-center justify-between mb-4 pb-4 border-b-2 border-gray-200">
                        <div className="flex items-center gap-3">
                          <FiImage className="w-6 h-6 text-orange-500" />
                          <span className="text-lg font-bold text-gray-900 uppercase tracking-wide">
                            {images.length} of 5 Images Captured
                          </span>
                        </div>
                        {images.length === 5 && (
                          <button
                            type="button"
                            onClick={() => {
                              setImages([]);
                              setPreviews([]);
                              setCurrentImageIndex(0);
                            }}
                            className="px-6 py-2 bg-red-500 text-white font-bold uppercase text-sm hover:bg-red-600 transition-colors border-b-2 border-red-700 flex items-center gap-2"
                          >
                            <FiRefreshCw className="w-4 h-4" />
                            Retake All
                          </button>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        {previews.map((preview, index) => (
                          <div key={index} className="relative group">
                            <div className="aspect-square bg-gray-200 border-2 border-gray-300 overflow-hidden relative">
                              <img
                                src={preview}
                                alt={imageLabels[index]}
                                className="w-full h-full object-cover"
                              />
                              <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                <button
                                  type="button"
                                  onClick={() => removeImage(index)}
                                  className="w-12 h-12 bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition-colors border-2 border-red-700"
                                >
                                  <FiX className="w-6 h-6" />
                                </button>
                              </div>
                            </div>
                            <div className="mt-2 text-center">
                              <span className="text-sm font-bold text-gray-700 uppercase">{imageLabels[index]}</span>
                            </div>
                          </div>
                        ))}
                      </div>

                      {images.length < 5 && (
                        <div className="mt-6 text-center pt-6 border-t-2 border-gray-200">
                          <button
                            type="button"
                            onClick={startCamera}
                            className="px-8 py-3 bg-orange-500 text-white font-bold uppercase text-sm hover:bg-orange-600 transition-colors inline-block border-b-2 border-orange-700"
                          >
                            {isCameraActive ? 'Continue Capturing' : 'Resume Camera'}
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 p-6 flex items-start gap-3">
                <FiAlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-bold text-red-900 mb-1 uppercase text-sm tracking-wide">Error</h3>
                  <p className="text-sm text-red-700 font-medium">{error}</p>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-center pt-4">
              <button
                type="submit"
                disabled={loading}
                className={`px-16 py-5 bg-orange-500 text-white text-base font-bold tracking-widest uppercase border-b-4 border-orange-700 ${
                  loading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-orange-600'
                } transition-colors`}
              >
                {loading ? (
                  <span className="flex items-center gap-3">
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white animate-spin"></div>
                    Processing...
                  </span>
                ) : (
                  'Start Classification'
                )}
              </button>
            </div>
          </form>
        </div>
      </section>

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-white/95 backdrop-blur-md z-50 flex flex-col items-center justify-center">
          <div className="w-20 h-20 border-4 border-gray-300 border-t-orange-500 animate-spin mb-6"></div>
          <h3 className="text-2xl font-bold text-black tracking-wide mb-2 uppercase">Processing Classification</h3>
          <p className="text-gray-600 text-sm uppercase tracking-wider font-semibold">Analyzing images and computing trait scores...</p>
        </div>
      )}
    </div>
  );
};

export default ClassifyPage;
