import React, { useState, useCallback, useRef } from 'react';
import { Upload, Download, Camera, Sparkles, Eye, Wand2, X } from 'lucide-react';

// Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ProcessingStage {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
}

interface ProcessingResult {
  session_id: string;
  detected_object: string;
  caption: string;
  original_image_url: string;
  generated_image_url: string;
  download_url: string;
}

const processingStages: ProcessingStage[] = [
  {
    id: 'upload',
    name: 'Uploading Image',
    icon: <Eye className="w-5 h-5" />,
    description: 'Sending your cloud photo to server...'
  },
  {
    id: 'outline',
    name: 'AI Analysis',
    icon: <Camera className="w-5 h-5" />,
    description: 'Analyzing your cloud pattern...'
  },
  {
    id: 'classify',
    name: 'Recognizing Objects',
    icon: <Sparkles className="w-5 h-5" />,
    description: 'Identifying cloud shapes...'
  },
  {
    id: 'generate',
    name: 'Creating Cloud Art',
    icon: <Wand2 className="w-5 h-5" />,
    description: 'Generating your artwork...'
  }
];

const funnyCaptions = [
  "Nature's got jokes! 🌤️",
  "When clouds have better imagination than humans 🤭",
  "Sky doodles by Mother Nature 🎨"
];

function App() {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processCloudImage = useCallback(async (file: File) => {
    setIsProcessing(true);
    setCurrentStage(0);
    setError(null);
    
    try {
      // Simulate processing stages
      for (let i = 0; i < processingStages.length; i++) {
        setCurrentStage(i);
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${API_BASE_URL}/process-cloud`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data: ProcessingResult = await response.json();
      setResult(data);

    } catch (err) {
      console.error('Processing failed:', err);
      setError(err instanceof Error ? err.message : 'Processing failed');
      
      // Fallback to mock data
      setResult({
        session_id: 'mock-' + Math.random().toString(36).substring(2),
        detected_object: ['dragon', 'dog', 'castle'][Math.floor(Math.random() * 3)],
        caption: funnyCaptions[Math.floor(Math.random() * funnyCaptions.length)],
        original_image_url: '/mock/original.jpg',
        generated_image_url: '/mock/generated.jpg',
        download_url: '/mock/download.jpg'
      });
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const handleFileUpload = useCallback((file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file');
      return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
      setUploadedImage(e.target?.result as string);
      processCloudImage(file);
    };
    reader.readAsDataURL(file);
  }, [processCloudImage]);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, [handleFileUpload]);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, [handleFileUpload]);

  const handleDownload = useCallback(() => {
    if (result?.download_url) {
      const downloadUrl = `${API_BASE_URL}${result.download_url}`;
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `cloud-art-${result.session_id}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }, [result]);

  const resetApp = useCallback(() => {
    setUploadedImage(null);
    setIsProcessing(false);
    setCurrentStage(0);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-100 via-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-slate-800 mb-4">
            Skygram ✨
          </h1>
          <p className="text-xl text-slate-600">
            Transform your cloud photos into magical AI art
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 max-w-md mx-auto">
            <div className="flex items-center justify-between">
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="text-red-500 hover:text-red-700"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Upload Area */}
        {!uploadedImage && !isProcessing && !result && (
          <div className="max-w-2xl mx-auto">
            <div
              className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                isDragging
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-slate-300 hover:border-slate-400'
              }`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <Upload className="w-16 h-16 text-slate-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-700 mb-2">
                Drop your cloud photo here
              </h3>
              <p className="text-slate-500 mb-6">
                or click to browse files
              </p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Choose Image
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileInput}
                className="hidden"
              />
            </div>
          </div>
        )}

        {/* Processing Stages */}
        {isProcessing && (
          <div className="max-w-4xl mx-auto mb-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {processingStages.map((stage, index) => (
                <div
                  key={stage.id}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    index === currentStage
                      ? 'border-blue-500 bg-blue-50'
                      : index < currentStage
                      ? 'border-green-500 bg-green-50'
                      : 'border-slate-200 bg-white'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${
                      index === currentStage
                        ? 'bg-blue-500 text-white'
                        : index < currentStage
                        ? 'bg-green-500 text-white'
                        : 'bg-slate-200 text-slate-500'
                    }`}>
                      {stage.icon}
                    </div>
                    <div>
                      <h4 className="font-medium text-slate-700">{stage.name}</h4>
                      <p className="text-sm text-slate-500">{stage.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Uploaded Image Preview */}
        {uploadedImage && (
          <div className="max-w-md mx-auto mb-8">
            <div className="relative">
              <img
                src={uploadedImage}
                alt="Uploaded cloud"
                className="w-full h-64 object-cover rounded-lg shadow-lg"
              />
              {!isProcessing && !result && (
                <button
                  onClick={resetApp}
                  className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-2 rounded-full transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        )}

        {/* Results Display */}
        {result && (
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-slate-800 mb-6">
              Your Cloud Transformation! ✨
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div>
                <h3 className="text-lg font-semibold text-slate-700 mb-3">Original Cloud</h3>
                <img
                  src={uploadedImage || ''}
                  alt="Original cloud"
                  className="w-full h-48 object-cover rounded-lg shadow-md"
                />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-700 mb-3">AI Generated Art</h3>
                {result?.generated_image_url ? (
                  <img
                    src={`${API_BASE_URL}${result.generated_image_url}`}
                    alt="AI generated cloud art"
                    className="w-full h-48 object-cover rounded-lg shadow-md"
                  />
                ) : (
                  <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg shadow-md flex items-center justify-center">
                    <p className="text-slate-500">Generated image will appear here</p>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-md mb-6">
              <p className="text-lg text-slate-600 mb-2">
                We detected: <span className="font-semibold text-blue-600">{result.detected_object}</span>
              </p>
              <p className="text-slate-500 italic text-lg">{result.caption}</p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={handleDownload}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
              >
                <Download className="w-5 h-5" />
                <span>Download Art</span>
              </button>
              <button
                onClick={resetApp}
                className="bg-slate-600 hover:bg-slate-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Try Another Cloud
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;