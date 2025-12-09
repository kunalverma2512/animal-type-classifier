import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import axios from 'axios';

const ClassificationResultsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchResults();
  }, [id]);

  const fetchResults = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/v1/classification/${id}/results`);
      console.log('Results received:', response.data);

      if (response.data.success) {
        setResults(response.data.data);
      } else {
        setError('Failed to fetch results');
      }
    } catch (err) {
      console.error('Results fetch error:', err);
      setError(err.response?.data?.detail || 'Failed to load classification results');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center pt-20">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-gray-300 border-t-orange-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg font-bold uppercase text-gray-900">Loading Results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 pt-20 px-4">
        <div className="max-w-2xl mx-auto mt-20">
          <div className="bg-red-50 border-l-4 border-red-500 p-6">
            <div className="flex items-start">
              <FiAlertCircle className="w-6 h-6 text-red-500 mt-1 mr-3" />
              <div>
                <h3 className="font-bold text-red-900 mb-2 uppercase">Error Loading Results</h3>
                <p className="text-red-700">{error}</p>
              </div>
            </div>
            <div className="mt-6 flex gap-4">
              <button
                onClick={() => navigate('/archive')}
                className="px-6 py-3 bg-red-600 text-white hover:bg-red-700 transition-colors font-semibold uppercase text-sm"
              >
                Back to Archive
              </button>
              <button
                onClick={fetchResults}
                className="px-6 py-3 border-2 border-red-600 text-red-600 hover:bg-red-50 transition-colors font-semibold uppercase text-sm"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!results) return null;

  return (
    <div className="min-h-screen bg-gray-50 pt-20">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white py-12 border-b-4 border-orange-500">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-bold tracking-widest uppercase text-gray-400 mb-2">Classification Complete</p>
              <h1 className="text-4xl font-bold uppercase tracking-tight">View Classification Results</h1>
            </div>
            <FiCheckCircle className="w-16 h-16 text-green-400" />
          </div>
        </div>
      </div>

      {/* Results Content */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        
        {/* Classification Info */}
        <div className="bg-white border-2 border-gray-200 p-6 mb-8">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <p className="text-xs font-bold uppercase text-gray-500 mb-1">Classification ID</p>
              <p className="text-lg font-mono">{id}</p>
            </div>
            <div>
              <p className="text-xs font-bold uppercase text-gray-500 mb-1">Status</p>
              <p className="text-lg font-bold text-green-600 uppercase">{results.status || 'Completed'}</p>
            </div>
          </div>
        </div>

        {/* View Classifications */}
        {results.viewClassifications && (
          <div className="bg-white border-2 border-gray-200 overflow-hidden mb-8">
            <div className="bg-slate-900 text-white px-8 py-6 border-b-4 border-orange-500">
              <h2 className="text-2xl font-bold uppercase tracking-wide">View Classifications</h2>
              <p className="text-sm text-gray-300 mt-2">Model detected the following views for each uploaded image</p>
            </div>
            
            <div className="p-8">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.entries(results.viewClassifications).map(([key, view]) => (
                  <div key={key} className="bg-gray-50 border-2 border-gray-300 p-6 hover:border-orange-500 transition-colors">
                    <div className="text-xs font-bold uppercase text-gray-500 mb-3">
                      {key.replace('_', ' ').toUpperCase()}
                    </div>
                    <div className="text-3xl font-bold text-orange-600 uppercase">
                      {view}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Raw Model Output (Debug) */}
        {results.modelOutput && (
          <div className="bg-gray-100 border-2 border-gray-300 p-6 mb-8">
            <h3 className="text-sm font-bold uppercase text-gray-700 mb-4">Raw Model Output</h3>
            <pre className="bg-white border border-gray-300 p-4 rounded overflow-x-auto text-sm">
              {JSON.stringify(results.modelOutput, null, 2)}
            </pre>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-4 justify-center">
          <button
            onClick={() => navigate('/classify')}
            className="px-8 py-4 bg-orange-500 text-white font-bold uppercase hover:bg-orange-600 transition-colors border-b-4 border-orange-700"
          >
            New Classification
          </button>
          <button
            onClick={() => navigate('/archive')}
            className="px-8 py-4 bg-gray-500 text-white font-bold uppercase hover:bg-gray-600 transition-colors border-b-4 border-gray-700"
          >
            View Archive
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClassificationResultsPage;
