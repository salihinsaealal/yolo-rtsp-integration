import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, AppBar, Toolbar, Typography, Container } from '@mui/material';
import { motion } from 'framer-motion';
import ModelManager from './components/ModelManager';
import InferenceTester from './components/InferenceTester';
import Navigation from './components/Navigation';

// Dark theme configuration
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1', // Indigo
      light: '#818cf8',
      dark: '#4f46e5',
    },
    secondary: {
      main: '#8b5cf6', // Purple
      light: '#a78bfa',
      dark: '#7c3aed',
    },
    background: {
      default: '#0f172a', // Slate 900
      paper: '#1e293b', // Slate 800
    },
    surface: {
      main: '#334155', // Slate 700
    }
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    }
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#1e293b',
          border: '1px solid #334155',
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        }
      }
    }
  }
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
          <AppBar position="static" elevation={0} sx={{ bgcolor: 'background.paper', borderBottom: '1px solid #334155' }}>
            <Toolbar>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: 'primary.main', fontWeight: 600 }}>
                  YOLO Inference Platform
                </Typography>
              </motion.div>
            </Toolbar>
          </AppBar>
          
          <Navigation />
          
          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Routes>
                <Route path="/" element={<ModelManager />} />
                <Route path="/models" element={<ModelManager />} />
                <Route path="/inference" element={<InferenceTester />} />
              </Routes>
            </motion.div>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
