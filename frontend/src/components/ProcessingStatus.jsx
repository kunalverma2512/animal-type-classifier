import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { FiLoader, FiCheckCircle, FiCircle, FiAlertCircle } from 'react-icons/fi';

const ProcessingStatus = ({ classificationId, onComplete, onError }) => {
    const [status, setStatus] = useState(null);
    const [isPolling, setIsPolling] = useState(true);

    useEffect(() => {
        if (!classificationId || !isPolling) return;

        const pollStatus = async () => {
            try {
                const response = await axios.get(
                    `/api/v1/classification/${classificationId}/status`
                );

                const statusData = response.data?.data;

                // Safely handle undefined or incomplete status data
                if (!statusData) {
                    console.log('No status data available');
                    return;
                }

                // Check if we have detailed processing status (from in-memory store)
                if (statusData.steps) {
                    setStatus(statusData);

                    if (statusData.status === 'completed' || statusData.status === 'error') {
                        setIsPolling(false);
                        if (statusData.status === 'completed' && onComplete) {
                            onComplete();
                        } else if (statusData.status === 'error' && onError) {
                            onError(statusData.error);
                        }
                    }
                } else if (statusData.status) {
                    // Fallback: processing completed before we could poll (basic DB status)
                    if (statusData.status === 'completed') {
                        setIsPolling(false);
                        if (onComplete) {
                            onComplete();
                        }
                    } else if (statusData.status === 'failed' || statusData.status === 'error') {
                        setIsPolling(false);
                        if (onError) {
                            onError(statusData.error || 'Processing failed');
                        }
                    }
                }
            } catch (error) {
                console.error('Status polling error:', error);
                // Continue polling even on error
            }
        };

        // Initial poll
        pollStatus();

        // Poll every 500ms
        const interval = setInterval(pollStatus, 500);

        return () => clearInterval(interval);
    }, [classificationId, isPolling, onComplete, onError]);

    if (!status) {
        return (
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
                <div className="flex items-center justify-center gap-3">
                    <FiLoader className="w-6 h-6 animate-spin text-orange-600" />
                    <p className="text-gray-700">Initializing...</p>
                </div>
            </div>
        );
    }

    const getStepIcon = (stepStatus) => {
        switch (stepStatus) {
            case 'completed':
                return <FiCheckCircle className="w-5 h-5 text-green-600" />;
            case 'processing':
                return <FiLoader className="w-5 h-5 animate-spin text-blue-600" />;
            case 'error':
                return <FiAlertCircle className="w-5 h-5 text-red-600" />;
            default:
                return <FiCircle className="w-5 h-5 text-gray-300" />;
        }
    };

    const progress = status.total_steps
        ? (status.current_step / status.total_steps) * 100
        : 0;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-orange-600 to-orange-500 p-6 text-white">
                    <div className="flex items-center gap-3 mb-2">
                        <FiLoader className="w-6 h-6 animate-spin" />
                        <h3 className="text-xl font-bold">Processing Classification</h3>
                    </div>
                    <p className="text-orange-100 text-sm">
                        Analyzing cattle images with AI models...
                    </p>
                </div>

                <div className="p-6">
                    {/* Progress Bar */}
                    {status.total_steps && (
                        <div className="mb-6">
                            <div className="flex justify-between text-sm mb-2">
                                <span className="font-medium text-gray-700">
                                    Progress: {status.current_step}/{status.total_steps} views
                                </span>
                                <span className="text-gray-600">{Math.round(progress)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                <div
                                    className="bg-gradient-to-r from-orange-600 to-orange-500 h-full transition-all duration-500 ease-out rounded-full"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                        </div>
                    )}

                    {/* Processing Steps */}
                    {status.steps && status.steps.length > 0 && (
                        <div className="space-y-3">
                            {status.steps.map((step, index) => (
                                <div
                                    key={index}
                                    className={`flex items-start gap-3 p-3 rounded-lg transition-all duration-300 ${step.status === 'processing'
                                            ? 'bg-blue-50 border border-blue-200'
                                            : step.status === 'completed'
                                                ? 'bg-green-50'
                                                : 'bg-gray-50'
                                        }`}
                                >
                                    <div className="mt-0.5">{getStepIcon(step.status)}</div>
                                    <div className="flex-1 min-w-0">
                                        <div className="font-medium text-gray-900 text-sm">
                                            {step.name}
                                        </div>
                                        <div
                                            className={`text-sm mt-0.5 ${step.status === 'processing'
                                                    ? 'text-blue-600'
                                                    : step.status === 'completed'
                                                        ? 'text-green-600'
                                                        : 'text-gray-500'
                                                }`}
                                        >
                                            {step.message}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Error Display */}
                    {status.error && (
                        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                            <div className="flex items-start gap-2">
                                <FiAlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                                <div>
                                    <p className="font-medium text-red-900 text-sm">
                                        Processing Error
                                    </p>
                                    <p className="text-red-700 text-sm mt-1">{status.error}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Completion Message */}
                    {status.status === 'completed' && (
                        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                            <div className="flex items-center gap-2">
                                <FiCheckCircle className="w-5 h-5 text-green-600" />
                                <p className="font-medium text-green-900 text-sm">
                                    Classification Complete!
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ProcessingStatus;
