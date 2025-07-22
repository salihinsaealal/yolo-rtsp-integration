import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Box, Tabs, Tab, Container } from '@mui/material';
import { Storage, Psychology } from '@mui/icons-material';
import { motion } from 'framer-motion';

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleChange = (event, newValue) => {
    navigate(newValue);
  };

  const currentTab = location.pathname === '/inference' ? '/inference' : '/models';

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
      <Container maxWidth="xl">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Tabs 
            value={currentTab} 
            onChange={handleChange} 
            aria-label="navigation tabs"
            sx={{
              '& .MuiTabs-indicator': {
                backgroundColor: 'primary.main',
                height: 3,
              }
            }}
          >
            <Tab 
              label="Model Manager" 
              value="/models" 
              icon={<Storage />} 
              iconPosition="start"
              sx={{ 
                textTransform: 'none', 
                fontWeight: 500,
                '&.Mui-selected': {
                  color: 'primary.main'
                }
              }}
            />
            <Tab 
              label="Inference Tester" 
              value="/inference" 
              icon={<Psychology />} 
              iconPosition="start"
              sx={{ 
                textTransform: 'none', 
                fontWeight: 500,
                '&.Mui-selected': {
                  color: 'primary.main'
                }
              }}
            />
          </Tabs>
        </motion.div>
      </Container>
    </Box>
  );
}

export default Navigation;
