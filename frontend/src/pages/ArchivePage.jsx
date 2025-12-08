import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiSearch, FiFilter, FiDownload, FiClock, FiMapPin, FiAward, FiChevronLeft, FiChevronRight, FiTrash2 } from 'react-icons/fi';
import { classificationService } from '../services/api';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

const ArchivePage = () => {
  const [classifications, setClassifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalResults, setTotalResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [deleteConfirm, setDeleteConfirm] = useState(null); // ID of item to delete

  // Filter state
  const [filters, setFilters] = useState({
    search: '',
    animal_type: '',
    grade: '',
    skip: 0,
    limit: 20
  });

  // Fetch archive data
  useEffect(() => {
    fetchArchive();
  }, [filters]);

  const fetchArchive = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await classificationService.getArchive(filters);
      setClassifications(response.data.results);
      setTotalResults(response.data.total);
      setCurrentPage(response.data.page);
      setTotalPages(response.data.totalPages);
    } catch (err) {
      setError(err.message || 'Failed to load archive');
      console.error('Archive fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle search input
  const handleSearchChange = (e) => {
    setFilters(prev => ({
      ...prev,
      search: e.target.value,
      skip: 0
    }));
  };

  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      skip: 0
    }));
  };

  // Handle pagination
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setFilters(prev => ({
        ...prev,
        skip: (newPage - 1) * prev.limit
      }));
    }
  };

  // Delete classification
  const handleDelete = async (id) => {
    try {
      await classificationService.deleteClassification(id);
      setDeleteConfirm(null);
      // Refresh the list
      fetchArchive();
    } catch (err) {
      console.error('Delete failed:', err);
      alert('Failed to delete classification: ' + err.message);
    }
  };

  // Export to Excel
  const exportToExcel = () => {
    if (classifications.length === 0) return;

    try {
      // Prepare data for Excel
      const worksheetData = [
        ['Tag Number', 'Animal Type', 'Breed', 'Village', 'Farmer Name', 'Overall Score', 'Grade', 'Confidence', 'Date'],
        ...classifications.map(c => [
          c.tagNumber,
          c.animalType,
          c.breed,
          c.village,
          c.farmerName,
          c.overallScore,
          c.grade,
          c.confidenceLevel,
          new Date(c.createdAt).toLocaleDateString()
        ])
      ];

      const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Classifications');

      // Generate filename
      const filename = `classification_archive_${new Date().toISOString().split('T')[0]}.xlsx`;

      // Generate Excel file as array buffer
      const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
      
      // Create blob with proper MIME type
      const blob = new Blob([excelBuffer], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      
      saveAs(blob, filename);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export Excel file. Please try again.');
    }
  };

  // Get grade badge styling
  const getGradeBadge = (grade) => {
    const styles = {
      'Excellent': 'bg-green-100 text-green-700 border-green-200',
      'Good': 'bg-orange-100 text-orange-700 border-orange-200',
      'Fair': 'bg-yellow-100 text-yellow-700 border-yellow-200',
      'Poor': 'bg-red-100 text-red-700 border-red-200'
    };
    return styles[grade] || 'bg-gray-100 text-gray-700 border-gray-200';
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-slate-900 via-slate-800 to-gray-900 text-white py-24 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-orange-500 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue-500 rounded-full blur-3xl animate-pulse"></div>
        </div>
        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="text-center space-y-6">
            <div className="text-sm font-medium tracking-widest uppercase text-gray-300">
              Classification History
            </div>
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-light">
              Archive
            </h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Browse all past livestock classifications with detailed scores and assessments
            </p>
          </div>
        </div>
      </section>

      {/* Search and Filters Section */}
      <section className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="space-y-6">
            {/* Search Bar and Export Button */}
            <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
              <div className="relative flex-grow max-w-2xl w-full">
                <FiSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search by tag number, breed, village, or farmer name..."
                  value={filters.search}
                  onChange={handleSearchChange}
                  className="w-full pl-12 pr-4 py-3 border border-gray-300 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 outline-none transition-all"
                />
              </div>
              <button
                onClick={exportToExcel}
                disabled={classifications.length === 0}
                className="px-6 py-3 bg-green-500 text-white font-medium tracking-wide hover:bg-green-600 transition-colors inline-flex items-center gap-2 disabled:bg-gray-300 disabled:cursor-not-allowed whitespace-nowrap"
              >
                <FiDownload className="w-5 h-5" />
                Export to Excel
              </button>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex items-center gap-2">
                <FiFilter className="text-gray-500 w-5 h-5" />
                <span className="text-sm font-medium text-gray-600">Filters:</span>
              </div>

              <select
                value={filters.animal_type}
                onChange={(e) => handleFilterChange('animal_type', e.target.value)}
                className="px-4 py-2 border border-gray-300 bg-white focus:border-orange-500 focus:ring-2 focus:ring-orange-200 outline-none transition-all text-sm"
              >
                <option value="">All Animal Types</option>
                <option value="cattle">Cattle 🐄</option>
                <option value="buffalo">Buffalo 🐃</option>
              </select>

              <select
                value={filters.grade}
                onChange={(e) => handleFilterChange('grade', e.target.value)}
                className="px-4 py-2 border border-gray-300 bg-white focus:border-orange-500 focus:ring-2 focus:ring-orange-200 outline-none transition-all text-sm"
              >
                <option value="">All Grades</option>
                <option value="Excellent">Excellent</option>
                <option value="Good">Good</option>
                <option value="Fair">Fair</option>
                <option value="Poor">Poor</option>
              </select>

              {(filters.search || filters.animal_type || filters.grade) && (
                <button
                  onClick={() => setFilters({ search: '', animal_type: '', grade: '', skip: 0, limit: 20 })}
                  className="px-4 py-2 text-sm text-orange-600 hover:text-orange-700 font-medium"
                >
                  Clear Filters
                </button>
              )}
            </div>

            {/* Results Count */}
            <div className="text-sm text-gray-600">
              Showing {classifications.length} of {totalResults} results
            </div>
          </div>
        </div>
      </section>

      {/* Results Section */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-6">
          {loading ? (
            <div className="text-center py-24">
              <div className="inline-block w-16 h-16 border-4 border-gray-300 border-t-orange-500 rounded-full animate-spin"></div>
              <p className="mt-6 text-gray-600">Loading classifications...</p>
            </div>
          ) : error ? (
            <div className="bg-red-50 border-l-4 border-red-500 p-8 text-center">
              <p className="text-red-700 font-medium">{error}</p>
              <button
                onClick={fetchArchive}
                className="mt-4 px-6 py-2 bg-red-600 text-white hover:bg-red-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : classifications.length === 0 ? (
            <div className="text-center py-24">
              <div className="text-6xl mb-6">📁</div>
              <h3 className="text-2xl font-light text-gray-700 mb-2">No Classifications Found</h3>
              <p className="text-gray-500">Try adjusting your search or filters</p>
            </div>
          ) : (
            <>
              {/* Results Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {classifications.map((classification) => (
                  <div
                    key={classification.id}
                    className="bg-white border border-gray-200 hover:shadow-lg transition-all duration-300 overflow-hidden group"
                  >
                    {/* Card Header */}
                    <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-4 text-white">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="text-3xl mb-2">
                            {classification.animalType === 'cattle' ? '🐄' : '🐃'}
                          </div>
                          <div className="text-sm font-medium tracking-wide">
                            {classification.tagNumber}
                          </div>
                        </div>
                        <div className={`px-3 py-1 border ${getGradeBadge(classification.grade)} text-xs font-bold tracking-wide`}>
                          {classification.grade}
                        </div>
                      </div>
                    </div>

                    {/* Card Body */}
                    <div className="p-6 space-y-4">
                      <div>
                        <h3 className="text-xl font-medium text-gray-900 mb-1">
                          {classification.breed}
                        </h3>
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <FiMapPin className="w-4 h-4" />
                          {classification.village}
                        </div>
                      </div>

                      <div className="border-t border-gray-200 pt-4 space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Overall Score</span>
                          <span className="text-2xl font-light text-gray-900">
                            {classification.overallScore}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <FiClock className="w-3 h-3" />
                          {formatDate(classification.createdAt)}
                        </div>
                      </div>

                      <div className="pt-2">
                        <div className="text-xs text-gray-500 mb-1">Farmer</div>
                        <div className="text-sm font-medium text-gray-700">
                          {classification.farmerName}
                        </div>
                      </div>
                    </div>

                    {/* Card Footer */}
                    <div className="px-6 pb-6 space-y-3">
                      <Link
                        to={`/classification/${classification.id}`}
                        className="block w-full px-4 py-3 bg-orange-500 text-white text-center font-medium tracking-wide hover:bg-orange-600 transition-colors"
                      >
                        View Full Details
                      </Link>
                      <button
                        onClick={() => setDeleteConfirm(classification.id)}
                        className="block w-full px-4 py-3 border-2 border-red-500 text-red-500 text-center font-medium tracking-wide hover:bg-red-500 hover:text-white transition-colors inline-flex items-center justify-center gap-2"
                      >
                        <FiTrash2 className="w-4 h-4" />
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="p-2 border border-gray-300 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <FiChevronLeft className="w-5 h-5" />
                  </button>

                  {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 7) {
                      pageNum = i + 1;
                    } else if (currentPage <= 4) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 3) {
                      pageNum = totalPages - 6 + i;
                    } else {
                      pageNum = currentPage - 3 + i;
                    }

                    return (
                      <button
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        className={`px-4 py-2 border font-medium transition-colors ${
                          currentPage === pageNum
                            ? 'bg-orange-500 text-white border-orange-500'
                            : 'border-gray-300 hover:bg-gray-100'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}

                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="p-2 border border-gray-300 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <FiChevronRight className="w-5 h-5" />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </section>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6">
          <div className="bg-white max-w-md w-full p-8 shadow-2xl">
            <h3 className="text-2xl font-medium text-gray-900 mb-4">Delete Classification?</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this classification? This action cannot be undone.
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 font-medium hover:bg-gray-100 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
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

export default ArchivePage;
