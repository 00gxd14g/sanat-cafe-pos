import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import DashboardScreen from './components/DashboardScreen';
import OrderScreen from './components/OrderScreen';
import DailyReportScreen from './components/DailyReportScreen';
import AdminOrdersScreen from './components/AdminOrdersScreen';
import AdminProductsScreen from './components/AdminProductsScreen';
import AdminSettingsScreen from './components/AdminSettingsScreen';
import AdminDebugScreen from './components/AdminDebugScreen';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DashboardScreen />} />
        <Route path="/pos" element={<OrderScreen />} />
        <Route path="/pos/:tableId" element={<OrderScreen />} />
        <Route path="/admin/orders" element={<AdminOrdersScreen />} />
        <Route path="/admin/products" element={<AdminProductsScreen />} />
        <Route path="/admin/settings" element={<AdminSettingsScreen />} />
        <Route path="/admin/debug" element={<AdminDebugScreen />} />
        <Route path="/admin/reports" element={<DailyReportScreen />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
