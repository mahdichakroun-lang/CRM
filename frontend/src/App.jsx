import { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

// Internal CRM
const AppLayout = lazy(() => import('./components/AppLayout'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const AccountsPage = lazy(() => import('./pages/AccountsPage'));
const ContactsPage = lazy(() => import('./pages/ContactsPage'));
const LeadsPage = lazy(() => import('./pages/LeadsPage'));
const DealsPage = lazy(() => import('./pages/DealsPage'));
const QuotesPage = lazy(() => import('./pages/QuotesPage'));
const TicketsPage = lazy(() => import('./pages/TicketsPage'));
const ActivitiesPage = lazy(() => import('./pages/ActivitiesPage'));
const AuditPage = lazy(() => import('./pages/AuditPage'));
const UsersPage = lazy(() => import('./pages/UsersPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const LeadScoringPage = lazy(() => import('./pages/LeadScoringPage'));

// Client Portal
const ClientLayout = lazy(() => import('./components/ClientLayout'));
const ClientDashboard = lazy(() => import('./pages/client/ClientDashboard'));
const ClientTicketsPage = lazy(() => import('./pages/client/ClientTicketsPage'));
const ClientQuotesPage = lazy(() => import('./pages/client/ClientQuotesPage'));

const PageLoader = () => (
  <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    Chargement...
  </div>
);

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public */}
            <Route path="/login" element={<LoginPage />} />

            {/* Internal CRM */}
            <Route path="/" element={<AppLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="accounts" element={<AccountsPage />} />
              <Route path="contacts" element={<ContactsPage />} />
              <Route path="leads" element={<LeadsPage />} />
              <Route path="deals" element={<DealsPage />} />
              <Route path="quotes" element={<QuotesPage />} />
              <Route path="tickets" element={<TicketsPage />} />
              <Route path="activities" element={<ActivitiesPage />} />
              <Route path="audit" element={<AuditPage />} />
              <Route path="users" element={<UsersPage />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route path="lead-scoring" element={<LeadScoringPage />} />
            </Route>

            {/* Client Portal */}
            <Route path="/portal" element={<ClientLayout />}>
              <Route index element={<ClientDashboard />} />
              <Route path="tickets" element={<ClientTicketsPage />} />
              <Route path="quotes" element={<ClientQuotesPage />} />
              <Route path="profile" element={<ProfilePage />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
