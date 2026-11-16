import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { DashboardPage } from '../pages/dashboard/DashboardPage';
import { SystemHealthPage } from '../pages/health/SystemHealthPage';
import { LoginPage } from '../pages/auth/LoginPage';
import { AssetListPage } from '../pages/assets/AssetListPage';
import { AssetDetailPage } from '../pages/assets/AssetDetailPage';
import { AssetHistoryPage } from '../pages/assets/AssetHistoryPage';
import { ProtectedRoute } from './ProtectedRoute';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: 'assets',
        element: <AssetListPage />,
      },
      {
        path: 'assets/:id',
        element: <AssetDetailPage />,
      },
      {
        path: 'assets/:id/history',
        element: <AssetHistoryPage />,
      },
      {
        path: 'health',
        element: <SystemHealthPage />,
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
]);
