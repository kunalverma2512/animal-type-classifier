import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { FiCheckCircle, FiLoader, FiAlertCircle, FiArrowLeft, FiDownload, FiTrash2 } from 'react-icons/fi';
import { classificationService } from '../services/api';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

const ClassificationResultsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(false);

  useEffect(() => {
    fetchResults();
  }, [id]);

  const fetchResults = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await classificationService.getResults(id);
      if (response.data.status === 'completed') {
        setResults(response.data);
      } else {
        setError(`Classification status: ${response.data.status}`);
      }
    } catch (err) {
      setError(err.message || 'Failed to load classification results');
      console.error('Error loading results:', err);
    } finally {
      setLoading(false);
    }
  };

  // Delete classification
  const handleDelete = async () => {
    try {
      await classificationService.deleteClassification(id);
      navigate('/archive');
    } catch (err) {
      console.error('Delete failed:', err);
      alert('Failed to delete classification: ' + err.message);
    }
  };

  // Export results as Excel
  const exportResults = () => {
    if (!results) return;
    
    try {
      // Create detailed worksheet
      const worksheetData = [
        ['Classification Results'],
        [''],
        ['Classification Information'],
        ['Classification ID', id],
        ['Classification Date', new Date(results.createdAt).toLocaleDateString()],
        [''],
        ['Overall Information'],
        ['Overall Score', results.overallScore],
        ['Grade', results.grade],
        ['Total Traits', results.totalTraits],
        [''],
        ['Category Scores'],
      ];

      Object.entries(results.categoryScores).forEach(([category, score]) => {
        worksheetData.push([category, score]);
      });

      worksheetData.push(['']);
      worksheetData.push(['Detailed Trait Scores']);
      worksheetData.push(['Section', 'Trait', 'Score', 'Measurement']);

      Object.entries(results.officialFormat.sections).forEach(([section, traits]) => {
        traits.forEach((trait) => {
          worksheetData.push([
            section,
            trait.trait,
            `${trait.score}/9`,
            trait.measurement ? `${trait.measurement} cm` : ''
          ]);
        });
      });

      const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Classification');

      const filename = `classification_${id}_${new Date().toISOString().split('T')[0]}.xlsx`;
      
      const excelBuffer = XLSX.write(workbook, { 
        bookType: 'xlsx', 
        type: 'array' 
      });
      
      const blob = new Blob([excelBuffer], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      
      saveAs(blob, filename);
      
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export Excel file. Please try again.');
    }
  };


  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <FiLoader className="w-16 h-16 text-orange-500 animate-spin mx-auto mb-6" />
          <p className="text-gray-600 text-lg">Loading classification results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="max-w-md w-full">
          <div className="bg-red-50 border-l-4 border-red-500 p-8 text-center">
            <FiAlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-medium text-red-900 mb-2">Error</h2>
            <p className="text-red-700 mb-6">{error}</p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => navigate('/archive')}
                className="px-6 py-3 bg-red-600 text-white hover:bg-red-700 transition-colors"
              >
                Back to Archive
              </button>
              <button
                onClick={fetchResults}
                className="px-6 py-3 border-2 border-red-600 text-red-600 hover:bg-red-50 transition-colors"
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
    <div className="min-h-screen bg-white">
      {/* Header */}
      <section className="bg-gradient-to-br from-teal-900 via-cyan-800 to-blue-900 text-white py-16 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-96 h-96 bg-green-500 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-80 h-80 bg-purple-500 rounded-full blur-3xl animate-pulse"></div>
        </div>
        <div className="max-w-5xl mx-auto px-6 relative z-10">
          <Link
            to="/archive"
            className="inline-flex items-center gap-2 text-teal-200 hover:text-white mb-6 transition-colors"
          >
            <FiArrowLeft className="w-5 h-5" />
            Back to Archive
          </Link>
          <div className="text-center space-y-4">
            <div className="inline-flex items-center gap-3 mb-4">
              <FiCheckCircle className="w-8 h-8 text-green-400" />
              <h1 className="text-4xl md:text-5xl font-light">Classification Results</h1>
            </div>
            <p className="text-xl text-gray-200">Official Type Evaluation Format (Annex II)</p>
            <div className="mt-4 flex gap-4 justify-center">
              <button
                onClick={exportResults}
                className="inline-flex items-center gap-2 px-6 py-3 bg-green-500 text-white hover:bg-green-600 transition-all font-medium"
              >
                <FiDownload className="w-5 h-5" />
                Export to Excel
              </button>
              <button
                onClick={() => setDeleteConfirm(true)}
                className="inline-flex items-center gap-2 px-6 py-3 bg-red-500 text-white hover:bg-red-600 transition-all font-medium"
              >
                <FiTrash2 className="w-5 h-5" />
                Delete Classification
              </button>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Overall Score */}
        <div className="bg-black text-white p-12 mb-12">
          <div className="text-center space-y-4">
            <div className="text-sm font-medium tracking-widest uppercase text-gray-400">
              Overall Type Score
            </div>
            <div className="text-7xl font-light">{results.overallScore}</div>
            <div className="text-2xl tracking-wide">{results.grade}</div>
            <div className="text-gray-400">Based on {results.totalTraits} official traits</div>
          </div>
        </div>

        {/* Milk Yield Prediction */}
        {results.milkYieldPrediction && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-8 mb-12 border-l-2 border-blue-500">
            <div className="mb-6">
              <div className="text-sm font-medium tracking-widest uppercase mb-2 text-blue-700">
                Predicted Milk Yield
              </div>
              <div className="flex items-baseline gap-4">
                <div className="text-5xl font-light text-blue-900">
                  {results.milkYieldPrediction.dailyYield}
                </div>
                <div className="text-xl text-blue-700">{results.milkYieldPrediction.unit}</div>
              </div>
              <div className="text-sm text-blue-600 mt-2">
                Range: {results.milkYieldPrediction.minYield} - {results.milkYieldPrediction.maxYield} {results.milkYieldPrediction.unit}
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <div className="text-sm font-medium uppercase mb-2 text-blue-700">Lactation Yield</div>
                <div className="text-2xl font-light text-blue-900">
                  {results.milkYieldPrediction.lactationYield.toLocaleString()}
                </div>
                <div className="text-sm text-blue-600">{results.milkYieldPrediction.lactationUnit}</div>
              </div>
              <div>
                <div className="text-sm font-medium uppercase mb-2 text-blue-700">Confidence</div>
                <div className="text-2xl font-light text-blue-900">
                  {results.milkYieldPrediction.confidence}%
                </div>
                <div className="text-sm text-blue-600">Based on body & udder measurements</div>
              </div>
            </div>
          </div>
        )}

        {/* Category Scores */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {Object.entries(results.categoryScores).map(([category, score]) => (
            <div key={category} className="border-l-2 border-black pl-6 py-4">
              <div className="text-sm font-medium tracking-widest uppercase mb-2 text-gray-500">
                {category}
              </div>
              <div className="text-4xl font-light">{score}</div>
            </div>
          ))}
        </div>

        {/* Detailed Traits */}
        <div className="space-y-12">
          <h3 className="text-3xl font-light border-l-2 border-black pl-6">Trait Details</h3>
          {Object.entries(results.officialFormat.sections).map(([section, traits]) => (
            <div key={section} className="border-l-2 border-gray-200 pl-6">
              <h4 className="text-xl font-medium mb-6">{section}</h4>
              <div className="grid md:grid-cols-2 gap-4">
                {traits.map((trait, idx) => (
                  <div key={idx} className="flex justify-between items-center p-4 bg-gray-50">
                    <span className="text-gray-700">{trait.trait}</span>
                    <div className="flex items-center gap-4">
                      {trait.measurement && (
                        <span className="text-sm text-gray-500">
                          {trait.measurement} {trait.measurement && 'cm'}
                        </span>
                      )}
                      <span className="font-medium text-lg">{trait.score}/9</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Back Button */}
        <div className="mt-16 text-center">
          <Link
            to="/archive"
            className="inline-flex items-center gap-2 px-12 py-4 bg-orange-500 text-white font-medium tracking-wide hover:bg-orange-600 transition-colors"
          >
            <FiArrowLeft className="w-5 h-5" />
            Back to Archive
          </Link>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6">
          <div className="bg-white max-w-md w-full p-8 shadow-2xl">
            <h3 className="text-2xl font-medium text-gray-900 mb-4">Delete Classification?</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this classification? This action cannot be undone.
              You will be redirected to the archive page.
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => setDeleteConfirm(false)}
                className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 font-medium hover:bg-gray-100 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="flex-1 px-6 py-3 bg-red-500 text-white font-medium hover:bg-red-600 transition-colors inline-flex items-center justify-center gap-2"
              >
                <FiTrash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClassificationResultsPage;
