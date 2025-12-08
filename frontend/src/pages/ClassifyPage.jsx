import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiUploadCloud, FiX, FiAlertCircle, FiCamera, FiImage } from 'react-icons/fi';
import axios from 'axios';

const ClassifyPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Image State - store as array
  const [images, setImages] = useState([]);
  const [previews, setPreviews] = useState([]);

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files);
    
    if (files.length !== 4) {
      setError("Please select exactly 4 images (Top View, Rear View, Side View, Bottom View)");
      return;
    }
    
    setImages(files);
    
    // Create previews
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
      // Step 1: Create Classification Record (with no animalInfo - backend will use defaults)
      const createResponse = await axios.post('http://127.0.0.1:8000/api/v1/classification/create', {});

      if (!createResponse.data.success) throw new Error("Failed to create record");
      
      const classificationId = createResponse.data.data.id;

      // Step 2: Upload Images
      const imageFormData = new FormData();
      images.forEach(image => {
        imageFormData.append('images', image);
      });

      const uploadResponse = await axios.post(
        `http://127.0.0.1:8000/api/v1/classification/${classificationId}/upload-images`,
        imageFormData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );

      if (!uploadResponse.data.success) throw new Error("Failed to upload images");

      // Step 3: Process Classification
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
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-green-900 via-emerald-800 to-teal-900 text-white pt-32 pb-20 px-6 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <motion.div 
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3], 
            }}
            transition={{ 
              duration: 8, 
              repeat: Infinity,
              ease: "easeInOut" 
            }}
            className="absolute top-20 left-10 w-72 h-72 bg-orange-500 rounded-full blur-3xl"
          ></motion.div>
          <motion.div 
            animate={{ 
              scale: [1, 1.5, 1],
              opacity: [0.3, 0.6, 0.3], 
            }}
            transition={{ 
              duration: 10, 
              repeat: Infinity, 
              ease: "easeInOut",
              delay: 1
            }}
            className="absolute bottom-20 right-10 w-96 h-96 bg-green-500 blur-3xl"
          ></motion.div>
        </div>

        <div className="max-w-7xl mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
              className="inline-flex items-center gap-2 px-5 py-2 bg-green-50 text-green-700 text-sm font-semibold tracking-widest uppercase mb-8 border-2 border-green-200"
            >
              <FiCamera className="w-4 h-4" />
              Official Type Evaluation
            </motion.div>

            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="text-5xl md:text-6xl lg:text-7xl font-light mb-6 leading-tight"
            >
              Classify Your Livestock
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="text-lg md:text-xl text-gray-300 leading-relaxed max-w-3xl mx-auto"
            >
              Upload 4 standardized images for comprehensive type score analysis following the official Annex II format with 20 traits across 5 sections.
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* Form Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            onSubmit={handleSubmit}
            className="space-y-8"
          >
            {/* Image Upload Card */}
            <div className="bg-white shadow-2xl overflow-hidden border-l-8 border-green-600">
              <div className="bg-gradient-to-r from-green-600 to-green-700 px-8 py-6 border-b-4 border-green-800">
                <h2 className="text-2xl font-bold text-white uppercase tracking-wide">Upload Images</h2>
                <p className="text-sm text-gray-300 mt-1">Select 4 images at once: Top View, Rear View, Side View, and Bottom View</p>
              </div>

              <div className="p-8 bg-gray-50">
                {images.length === 0 ? (
                  <div className="relative">
                    <input
                      type="file"
                      accept="image/*"
                      multiple
                      onChange={handleImageSelect}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    />
                    <div className="border-4 border-dashed border-gray-400 hover:border-green-600 transition-all bg-white p-16 text-center cursor-pointer group">
                      <div className="flex flex-col items-center">
                        <div className="w-24 h-24 bg-green-100 flex items-center justify-center mb-6 border-2 border-green-600">
                          <FiUploadCloud className="w-12 h-12 text-green-600" />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 mb-3 uppercase tracking-wide">Drop Images Here</h3>
                        <p className="text-lg text-gray-600 mb-6">or click to browse</p>
                        <div className="flex items-center gap-3 text-sm font-bold text-gray-700 uppercase">
                          <span className="px-4 py-2 bg-green-600 text-white border-2 border-green-600">Select 4 Images</span>
                          <span className="text-gray-500">JPG, PNG, JPEG</span>
                        </div>
                        <div className="mt-6 text-xs text-gray-500 uppercase tracking-wider">
                          Required: Top View • Rear View • Side View • Bottom View
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center gap-3">
                        <FiImage className="w-6 h-6 text-green-600" />
                        <span className="text-lg font-bold text-gray-900 uppercase">{images.length} Images Selected</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          setImages([]);
                          setPreviews([]);
                        }}
                        className="px-4 py-2 bg-red-600 text-white font-bold uppercase text-sm hover:bg-red-700 transition-colors"
                      >
                        Clear All
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                      {previews.map((preview, index) => (
                        <div key={index} className="relative group">
                          <div className="aspect-square bg-gray-200 border-4 border-gray-300 overflow-hidden relative">
                            <img
                              src={preview}
                              alt={`Upload ${index + 1}`}
                              className="w-full h-full object-cover"
                            />
                            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                              <button
                                type="button"
                                onClick={() => removeImage(index)}
                                className="w-12 h-12 bg-red-600 text-white flex items-center justify-center hover:bg-red-700 transition-colors"
                              >
                                <FiX className="w-6 h-6" />
                              </button>
                            </div>
                          </div>
                          <div className="mt-2 text-center">
                            <span className="text-sm font-bold text-gray-700 uppercase">Image {index + 1}</span>
                            <p className="text-xs text-gray-500 mt-1">{images[index].name}</p>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="mt-6 text-center">
                      <label className="inline-block cursor-pointer">
                        <input
                          type="file"
                          accept="image/*"
                          multiple
                          onChange={handleImageSelect}
                          className="hidden"
                        />
                        <span className="px-6 py-3 bg-green-600 text-white font-bold uppercase text-sm hover:bg-green-700 transition-colors inline-block">
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
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-50 border-l-4 border-red-600 p-5 flex items-start gap-3"
              >
                <FiAlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-bold text-red-900 mb-1 uppercase text-sm">Error</h3>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </motion.div>
            )}

            {/* Submit Button */}
            <div className="flex justify-center pt-4">
              <motion.button
                type="submit"
                disabled={loading}
                whileHover={{ scale: loading ? 1 : 1.02 }}
                whileTap={{ scale: loading ? 1 : 0.98 }}
                className={`px-16 py-5 bg-gradient-to-r from-green-600 to-emerald-600 text-white text-base font-bold tracking-[0.3em] uppercase shadow-2xl border-b-4 border-green-800 ${
                  loading ? 'opacity-50 cursor-not-allowed' : 'hover:from-green-700 hover:to-emerald-700'
                }`}
              >
                {loading ? (
                  <span className="flex items-center gap-3">
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white animate-spin"></div>
                    Processing...
                  </span>
                ) : (
                  'Start Classification'
                )}
              </motion.button>
            </div>
          </motion.form>
        </div>
      </section>

      {/* Loading Overlay */}
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-white/95 backdrop-blur-md z-50 flex flex-col items-center justify-center"
        >
          <div className="w-20 h-20 border-4 border-gray-300 border-t-green-600 animate-spin mb-6"></div>
          <h3 className="text-2xl font-bold text-black tracking-wide mb-2 uppercase">Processing Classification</h3>
          <p className="text-gray-600 text-sm uppercase tracking-wider">Analyzing images and computing trait scores...</p>
        </motion.div>
      )}
    </div>
  );
};

export default ClassifyPage;
