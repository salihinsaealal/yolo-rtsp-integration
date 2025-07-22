import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Button, Grid, TextField,
  Select, MenuItem, FormControl, InputLabel, Tabs, Tab,
  Snackbar, Alert, LinearProgress, Chip, Paper, Divider
} from '@mui/material';
import {
  Psychology, CloudUpload, Videocam, Download, Refresh,
  Image as ImageIcon, Analytics, Timer
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_BASE = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5000';

function InferenceTester() {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [inputMode, setInputMode] = useState(0); // 0: Image Upload, 1: RTSP
  const [rtspUrl, setRtspUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [uploadedImage, setUploadedImage] = useState(null);

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const fetchModels = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/models`);
      const modelList = response.data.models || [];
      setModels(modelList);
      if (modelList.length > 0 && !selectedModel) {
        setSelectedModel(modelList[0].name);
      }
    } catch (error) {
      showSnackbar('Failed to fetch models', 'error');
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      showSnackbar('Please upload an image file', 'error');
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setUploadedImage({
        file,
        preview: reader.result
      });
    };
    reader.readAsDataURL(file);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.tiff']
    },
    multiple: false
  });

  const runInference = async () => {
    if (!selectedModel) {
      showSnackbar('Please select a model', 'error');
      return;
    }

    if (inputMode === 0 && !uploadedImage) {
      showSnackbar('Please upload an image', 'error');
      return;
    }

    if (inputMode === 1 && !rtspUrl) {
      showSnackbar('Please enter an RTSP URL', 'error');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('model', selectedModel);

      if (inputMode === 0) {
        formData.append('image', uploadedImage.file);
      } else {
        formData.append('rtsp_url', rtspUrl);
      }

      const response = await axios.post(`${API_BASE}/api/inference`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000 // 60 second timeout
      });

      setResult(response.data);
      showSnackbar('Inference completed successfully!', 'success');
    } catch (error) {
      showSnackbar(error.response?.data?.error || 'Inference failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const downloadResult = (type) => {
    if (!result) return;

    if (type === 'image') {
      const link = document.createElement('a');
      link.href = `data:image/jpeg;base64,${result.image_base64}`;
      link.download = `result_${result.result_id}.jpg`;
      link.click();
    } else if (type === 'json') {
      const dataStr = JSON.stringify({
        result_id: result.result_id,
        model: selectedModel,
        detections: result.detections,
        timestamp: new Date().toISOString()
      }, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `result_${result.result_id}.json`;
      link.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" gutterBottom sx={{ color: 'text.primary', mb: 3 }}>
          Inference Tester
        </Typography>
      </motion.div>

      <Grid container spacing={4}>
        {/* Input Section */}
        <Grid item xs={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Input Configuration
                </Typography>

                {/* Model Selection */}
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel>Select Model</InputLabel>
                  <Select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    label="Select Model"
                  >
                    {models.map((model) => (
                      <MenuItem key={model.name} value={model.name}>
                        {model.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {/* Input Mode Tabs */}
                <Tabs
                  value={inputMode}
                  onChange={(e, newValue) => setInputMode(newValue)}
                  sx={{ mb: 3 }}
                >
                  <Tab icon={<ImageIcon />} label="Image Upload" />
                  <Tab icon={<Videocam />} label="RTSP Stream" />
                </Tabs>

                {/* Image Upload */}
                {inputMode === 0 && (
                  <Box>
                    <Box
                      {...getRootProps()}
                      sx={{
                        border: '2px dashed',
                        borderColor: isDragActive ? 'primary.main' : 'grey.600',
                        borderRadius: 2,
                        p: 3,
                        textAlign: 'center',
                        cursor: 'pointer',
                        bgcolor: isDragActive ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          borderColor: 'primary.main',
                          bgcolor: 'rgba(99, 102, 241, 0.05)'
                        }
                      }}
                    >
                      <input {...getInputProps()} />
                      <CloudUpload sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                      <Typography variant="body1" gutterBottom>
                        {isDragActive ? 'Drop image here' : 'Upload Test Image'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Drag & drop or click to browse
                      </Typography>
                    </Box>

                    {uploadedImage && (
                      <Box sx={{ mt: 2, textAlign: 'center' }}>
                        <img
                          src={uploadedImage.preview}
                          alt="Preview"
                          style={{
                            maxWidth: '100%',
                            maxHeight: 200,
                            borderRadius: 8,
                            border: '1px solid #334155'
                          }}
                        />
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          {uploadedImage.file.name}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                )}

                {/* RTSP Input */}
                {inputMode === 1 && (
                  <TextField
                    fullWidth
                    label="RTSP URL"
                    value={rtspUrl}
                    onChange={(e) => setRtspUrl(e.target.value)}
                    placeholder="rtsp://username:password@ip:port/stream"
                    helperText="Enter your RTSP camera stream URL"
                  />
                )}

                {/* Run Inference Button */}
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={runInference}
                  disabled={loading || !selectedModel || (inputMode === 0 && !uploadedImage) || (inputMode === 1 && !rtspUrl)}
                  startIcon={<Psychology />}
                  sx={{ mt: 3 }}
                >
                  {loading ? 'Running Inference...' : 'Run Inference'}
                </Button>

                {loading && <LinearProgress sx={{ mt: 2 }} />}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Results
                  </Typography>
                  {result && (
                    <Box>
                      <Button
                        size="small"
                        startIcon={<Download />}
                        onClick={() => downloadResult('image')}
                        sx={{ mr: 1 }}
                      >
                        Image
                      </Button>
                      <Button
                        size="small"
                        startIcon={<Download />}
                        onClick={() => downloadResult('json')}
                      >
                        JSON
                      </Button>
                    </Box>
                  )}
                </Box>

                {result ? (
                  <AnimatePresence>
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5 }}
                    >
                      {/* Result Image */}
                      <Box sx={{ mb: 3, textAlign: 'center' }}>
                        <img
                          src={`data:image/jpeg;base64,${result.image_base64}`}
                          alt="Detection Result"
                          style={{
                            maxWidth: '100%',
                            maxHeight: 400,
                            borderRadius: 8,
                            border: '1px solid #334155'
                          }}
                        />
                      </Box>

                      {/* Detection Summary */}
                      <Paper sx={{ p: 2, mb: 2, bgcolor: 'background.paper' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Analytics sx={{ mr: 1, color: 'primary.main' }} />
                          <Typography variant="subtitle1">
                            Detection Summary
                          </Typography>
                        </Box>
                        <Chip
                          label={`${result.detections.length} objects detected`}
                          color="primary"
                          size="small"
                        />
                      </Paper>

                      {/* Detections List */}
                      {result.detections.length > 0 && (
                        <Box>
                          <Typography variant="subtitle2" gutterBottom>
                            Detected Objects:
                          </Typography>
                          {result.detections.map((detection, index) => (
                            <Paper key={index} sx={{ p: 2, mb: 1, bgcolor: 'background.default' }}>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="body1" fontWeight="medium">
                                  {detection.class}
                                </Typography>
                                <Chip
                                  label={`${(detection.confidence * 100).toFixed(1)}%`}
                                  size="small"
                                  color={detection.confidence > 0.8 ? 'success' : detection.confidence > 0.5 ? 'warning' : 'default'}
                                />
                              </Box>
                              <Typography variant="body2" color="text.secondary">
                                Area: {(detection.area * 100).toFixed(2)}%
                              </Typography>
                            </Paper>
                          ))}
                        </Box>
                      )}
                    </motion.div>
                  </AnimatePresence>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 6 }}>
                    <Psychology sx={{ fontSize: 64, color: 'grey.600', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      No results yet
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Configure your input and run inference to see results
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default InferenceTester;
