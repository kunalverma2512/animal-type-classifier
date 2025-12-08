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

  const handleDelete = async () => {
    try {
      await classificationService.deleteClassification(id);
      navigate('/archive');
    } catch (err) {
      console.error('Delete failed:', err);
      alert('Failed to delete classification: ' + err.message);
    }
  };

  const exportResults = () => {
    if (!results) return;
    
    try {
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
          <p className="text-gray-600 text-lg font-semibold uppercase tracking-wide">Loading Results...</p>
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
            <h2 className="text-2xl font-bold text-red-900 mb-2 uppercase tracking-wide">Error</h2>
            <p className="text-red-700 mb-6 font-medium">{error}</p>
            <div className="flex gap-4 justify-center">
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

  const getGradeColor = (grade) => {
    const colors = {
      'Excellent': 'bg-green-500 border-green-700',
      'Good': 'bg-blue-500 border-blue-700',
      'Fair': 'bg-yellow-500 border-yellow-700',
      'Poor': 'bg-red-500 border-red-700'
    };
    return colors[grade] || 'bg-gray-500 border-gray-700';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <section className="bg-gradient-to-r from-slate-900 to-slate-800 text-white py-12 border-b-4 border-orange-500">
        <div className="max-w-6xl mx-auto px-6">
          <Link
            to="/archive"
            className="inline-flex items-center gap-2 text-gray-300 hover:text-white mb-6 transition-colors font-semibold uppercase text-sm"
          >
            <FiArrowLeft className="w-5 h-5" />
            Back to Archive
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <div className="inline-flex items-center gap-3 mb-4">
                <FiCheckCircle className="w-8 h-8 text-green-400" />
                <h1 className="text-4xl font-bold tracking-tight">Classification Results</h1>
              </div>
              <p className="text-gray-300 font-medium uppercase text-sm tracking-wider">Official Type Evaluation Format (Annex II)</p>
            </div>
          </div>
          <div className="mt-6 flex gap-4">
            <button
              onClick={exportResults}
              className="inline-flex items-center gap-2 px-6 py-3 bg-orange-500 text-white hover:bg-orange-600 transition-all font-semibold uppercase text-sm tracking-wide border-b-2 border-orange-700"
            >
              <FiDownload className="w-5 h-5" />
              Export Excel
            </button>
            <button
              onClick={() => setDeleteConfirm(true)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-red-500 text-white hover:bg-red-600 transition-all font-semibold uppercase text-sm tracking-wide border-b-2 border-red-700"
            >
              <FiTrash2 className="w-5 h-5" />
              Delete
            </button>
          </div>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Classification Info */}
        <div className="bg-white border-2 border-gray-200 p-8 mb-8">
          <h3 className="text-xs font-bold uppercase tracking-widest text-gray-500 mb-4">Classification Details</h3>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Classification ID</p>
              <p className="text-sm font-mono text-gray-800 break-all">{id}</p>
            </div>
            <div>
              <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Date</p>
              <p className="text-sm font-semibold text-gray-800">{new Date(results.createdAt).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        {/* Overall Score */}
        <div className="bg-slate-900 text-white p-12 mb-8 border-b-4 border-orange-500">
          <div className="text-center space-y-4">
            <div className="text-xs font-bold tracking-widest uppercase text-gray-400">
              Overall Type Score
            </div>
            <div className="text-8xl font-bold tracking-tight">{results.overallScore}</div>
            <div className={`inline-block px-8 py-3 text-white text-xl font-bold uppercase tracking-wider border-b-4 ${getGradeColor(results.grade)}`}>
              {results.grade}
            </div>
            <div className="text-gray-400 font-medium">Based on {results.totalTraits} official traits</div>
          </div>
        </div>

        {/* Category Scores */}
        <div className="mb-8">
          <h3 className="text-xl font-bold uppercase tracking-wide mb-6 border-l-4 border-orange-500 pl-4">Section Scores</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(results.categoryScores).map(([category, score]) => (
              <div key={category} className="bg-white border-2 border-gray-200 p-6 hover:border-orange-500 transition-colors">
                <div className="text-xs font-bold tracking-widest uppercase mb-2 text-gray-500">
                  {category}
                </div>
                <div className="text-5xl font-bold text-gray-900">{score}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Detailed Traits */}
        <div className="space-y-8">
          <h3 className="text-xl font-bold uppercase tracking-wide border-l-4 border-orange-500 pl-4">Trait Details</h3>
          {Object.entries(results.officialFormat.sections).map(([section, traits]) => (
            <div key={section} className="bg-white border-2 border-gray-200 overflow-hidden">
              <div className="bg-slate-900 text-white px-6 py-4 border-b-2 border-orange-500">
                <h4 className="text-sm font-bold uppercase tracking-wider">{section}</h4>
              </div>
              <div className="divide-y-2 divide-gray-200">
                {traits.map((trait, idx) => (
                  <div key={idx} className="flex justify-between items-center p-4 hover:bg-gray-50 transition-colors">
                    <span className="text-gray-700 font-medium">{trait.trait}</span>
                    <div className="flex items-center gap-6">
                      {trait.measurement && (
                        <span className="text-sm text-gray-500 font-semibold">
                          {trait.measurement} cm
                        </span>
                      )}
                      <span className="font-bold text-xl text-gray-900 min-w-[60px] text-right">{trait.score}/9</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Back Button */}
        <div className="mt-12 text-center">
          <Link
            to="/archive"
            className="inline-flex items-center gap-2 px-12 py-4 bg-orange-500 text-white font-bold tracking-wide hover:bg-orange-600 transition-colors uppercase text-sm border-b-4 border-orange-700"
          >
            <FiArrowLeft className="w-5 h-5" />
            Back to Archive
          </Link>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6">
          <div className="bg-white max-w-md w-full p-8 border-4 border-gray-200">
            <h3 className="text-2xl font-bold text-gray-900 mb-4 uppercase tracking-wide">Delete Classification?</h3>
            <p className="text-gray-600 mb-6 font-medium">
              Are you sure you want to delete this classification? This action cannot be undone.
              You will be redirected to the archive page.
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => setDeleteConfirm(false)}
                className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 font-bold hover:bg-gray-100 transition-colors uppercase text-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="flex-1 px-6 py-3 bg-red-500 text-white font-bold hover:bg-red-600 transition-colors inline-flex items-center justify-center gap-2 uppercase text-sm"
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
