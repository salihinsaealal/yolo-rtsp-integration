import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Button, Grid, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Snackbar, Alert, LinearProgress, Chip, Tooltip
} from '@mui/material';
import {
  Upload, Delete, Download, Refresh, CloudUpload,
  Storage, Schedule, FilePresent
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_BASE = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5000';

function ModelManager() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [deleteDialog, setDeleteDialog] = useState({ open: false, model: null });

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const fetchModels = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/models`);
      setModels(response.data.models || []);
    } catch (error) {
      showSnackbar('Failed to fetch models', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (!file.name.match(/\.(pt|onnx|engine)$/i)) {
      showSnackbar('Invalid file type. Only .pt, .onnx, .engine files are allowed.', 'error');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('model', file);

    try {
      await axios.post(`${API_BASE}/api/models`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        }
      });
      
      showSnackbar('Model uploaded successfully!', 'success');
      fetchModels();
    } catch (error) {
      showSnackbar(error.response?.data?.error || 'Upload failed', 'error');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/octet-stream': ['.pt', '.onnx', '.engine']
    },
    multiple: false
  });

  const handleDelete = async () => {
    if (!deleteDialog.model) return;

    try {
      await axios.delete(`${API_BASE}/api/models/${deleteDialog.model.name}`);
      showSnackbar('Model deleted successfully!', 'success');
      fetchModels();
    } catch (error) {
      showSnackbar(error.response?.data?.error || 'Delete failed', 'error');
    } finally {
      setDeleteDialog({ open: false, model: null });
    }
  };

  const handleDownload = async (model) => {
    try {
      const response = await axios.get(`${API_BASE}/api/models/${model.name}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', model.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      showSnackbar('Download started!', 'success');
    } catch (error) {
      showSnackbar('Download failed', 'error');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" gutterBottom sx={{ color: 'text.primary', mb: 3 }}>
          Model Manager
        </Typography>
      </motion.div>

      {/* Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card sx={{ mb: 4, border: isDragActive ? '2px dashed #6366f1' : '1px solid #334155' }}>
          <CardContent>
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.600',
                borderRadius: 2,
                p: 4,
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
              <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {isDragActive ? 'Drop your model here' : 'Upload YOLO Model'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Drag & drop a .pt, .onnx, or .engine file here, or click to browse
              </Typography>
              {uploading && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress variant="determinate" value={uploadProgress} />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Uploading... {uploadProgress}%
                  </Typography>
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>
      </motion.div>

      {/* Models List */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ color: 'text.primary' }}>
          Available Models ({models.length})
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchModels}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {loading ? (
        <LinearProgress />
      ) : (
        <Grid container spacing={3}>
          <AnimatePresence>
            {models.map((model, index) => (
              <Grid item xs={12} md={6} lg={4} key={model.name}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  whileHover={{ y: -4 }}
                >
                  <Card sx={{ height: '100%', position: 'relative' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <FilePresent sx={{ color: 'primary.main', mr: 1 }} />
                        <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>
                          {model.name}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ mb: 2 }}>
                        <Chip
                          icon={<Storage />}
                          label={formatFileSize(model.size)}
                          size="small"
                          sx={{ mr: 1, mb: 1 }}
                        />
                        <Chip
                          icon={<Schedule />}
                          label={formatDate(model.modified)}
                          size="small"
                          sx={{ mb: 1 }}
                        />
                      </Box>

                      <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                        <Tooltip title="Download">
                          <IconButton
                            size="small"
                            onClick={() => handleDownload(model)}
                            sx={{ color: 'primary.main' }}
                          >
                            <Download />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            onClick={() => setDeleteDialog({ open: true, model })}
                            sx={{ color: 'error.main' }}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </AnimatePresence>
        </Grid>
      )}

      {models.length === 0 && !loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <Storage sx={{ fontSize: 64, color: 'grey.600', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No models uploaded yet
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upload your first YOLO model to get started
              </Typography>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, model: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Delete Model</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{deleteDialog.model?.name}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, model: null })}>
            Cancel
          </Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

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

export default ModelManager;
