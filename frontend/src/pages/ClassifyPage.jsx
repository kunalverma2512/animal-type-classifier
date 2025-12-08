import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUploadCloud, FiX, FiAlertCircle, FiImage } from 'react-icons/fi';
import axios from 'axios';

const ClassifyPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [images, setImages] = useState([]);
  const [previews, setPreviews] = useState([]);

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files);
    
    if (files.length !== 4) {
      setError("Please select exactly 4 images (Top View, Rear View, Side View, Bottom View)");
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
  };

  const validateForm = () => {
    if (images.length !== 4) {
      setError("Please upload exactly 4 images.");
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
              Upload 4 standardized images for comprehensive type score analysis following the official Annex II format with 20 traits across 5 sections.
            </p>
          </div>
        </div>
      </section>

      {/* Form Section */}
      <section className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Image Upload Card */}
            <div className="bg-white border-2 border-gray-200 overflow-hidden">
              <div className="bg-slate-900 text-white px-8 py-6 border-b-4 border-orange-500">
                <h2 className="text-xl font-bold uppercase tracking-wide">Upload Images</h2>
                <p className="text-sm text-gray-300 mt-2 font-medium">Select 4 images at once: Top View, Rear View, Side View, and Bottom View</p>
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
                          <span className="px-6 py-3 bg-orange-500 text-white border-b-2 border-orange-700">Select 4 Images</span>
                          <span className="text-gray-500 font-semibold">JPG, PNG, JPEG</span>
                        </div>
                        <div className="mt-6 text-xs text-gray-500 uppercase tracking-wider font-bold">
                          Required: Top View • Rear View • Side View • Bottom View
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
                            <span className="text-sm font-bold text-gray-700 uppercase">Image {index + 1}</span>
                            <p className="text-xs text-gray-500 mt-1 truncate">{images[index].name}</p>
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
