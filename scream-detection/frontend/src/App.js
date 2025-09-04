import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import WaveSurfer from 'wavesurfer.js';
import RecordRTC from 'recordrtc';

const App = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [result, setResult] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const waveformRef = useRef(null);
  const wavesurferRef = useRef(null);
  const recorderRef = useRef(null);
  const audioContextRef = useRef(null);

  useEffect(() => {
    // Initialize WaveSurfer
    if (waveformRef.current && !wavesurferRef.current) {
      wavesurferRef.current = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: '#4F46E5',
        progressColor: '#4338CA',
        cursorColor: '#FFFFFF',
        barWidth: 2,
        barRadius: 3,
        cursorWidth: 1,
        height: 80,
        barGap: 2
      });
      
      wavesurferRef.current.on('ready', () => {
        console.log('WaveSurfer is ready');
      });
    }
    
    return () => {
      if (wavesurferRef.current) {
        wavesurferRef.current.destroy();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      setError(null);
      setResult(null);
      setAudioUrl(null);
      
      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Create audio context
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      
      // Initialize recorder
      recorderRef.current = RecordRTC(stream, {
        type: 'audio',
        mimeType: 'audio/wav',
        recorderType: RecordRTC.StereoAudioRecorder,
        desiredSampRate: 16000,
        numberOfAudioChannels: 1,
        timeSlice: 1000, // Process every second
        ondataavailable: async (blob) => {
          // For real-time processing, we could send chunks here
        }
      });
      
      // Start recording
      recorderRef.current.startRecording();
      setIsRecording(true);
      
    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Error accessing microphone. Please check permissions.');
    }
  };

  const stopRecording = async () => {
    if (!recorderRef.current) return;
    
    setIsRecording(false);
    
    return new Promise((resolve) => {
      recorderRef.current.stopRecording(async () => {
        const blob = recorderRef.current.getBlob();
        
        // Create URL for playback
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        
        // Load audio in WaveSurfer
        if (wavesurferRef.current) {
          wavesurferRef.current.load(url);
        }
        
        // Prepare form data for upload
        const formData = new FormData();
        formData.append('file', blob, 'recording.wav');
        
        // Send to backend
        try {
          setIsLoading(true);
          const response = await axios.post('http://localhost:5000/predict', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          });
          
          setResult(response.data);
          setError(null);
        } catch (err) {
          console.error('Error analyzing audio:', err);
          setError('Error analyzing audio. Please try again.');
        } finally {
          setIsLoading(false);
          resolve();
        }
      });
    });
  };

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl">
        <div className="p-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Scream Detection System</h1>
            <p className="text-gray-600 mb-6">
              Record audio or upload a file to detect screams
            </p>
          </div>
          
          <div className="mb-6">
            <div ref={waveformRef} className="mb-4"></div>
            
            <div className="flex justify-center space-x-4">
              {!isRecording ? (
                <button
                  onClick={startRecording}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  Start Recording
                </button>
              ) : (
                <button
                  onClick={stopRecording}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                >
                  Stop Recording
                </button>
              )}
            </div>
          </div>
          
          {isLoading && (
            <div className="text-center py-4">
              <p className="text-indigo-600">Analyzing audio...</p>
            </div>
          )}
          
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}
          
          {result && (
            <div className={`p-4 rounded-md ${result.is_scream ? 'bg-red-50 border-l-4 border-red-400' : 'bg-green-50 border-l-4 border-green-400'}`}>
              <div className="flex">
                <div className="flex-shrink-0">
                  {result.is_scream ? (
                    <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
                <div className="ml-3">
                  <h3 className={`text-sm font-medium ${result.is_scream ? 'text-red-800' : 'text-green-800'}`}>
                    {result.is_scream ? 'Scream detected!' : 'No scream detected'}
                  </h3>
                  <div className="mt-2 text-sm text-gray-700">
                    <p>Confidence: {(result.probability * 100).toFixed(2)}%</p>
                    <p>Threshold: {(result.threshold * 100).toFixed(2)}%</p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {audioUrl && (
            <div className="mt-6">
              <audio controls src={audioUrl} className="w-full" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;