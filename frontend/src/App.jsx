import { useMemo } from 'react';
import { NavLink, Outlet, Route, Routes } from 'react-router-dom';

import DashboardPage from './pages/DashboardPage.jsx';
import MembersPage from './pages/MembersPage.jsx';
import InventoryPage from './pages/InventoryPage.jsx';

const navItems = [
  { to: '/', label: 'Tableau de bord', exact: true },
  { to: '/members', label: 'Membres' },
  { to: '/inventory', label: 'Stocks' },
];

function App() {
  const navLinks = useMemo(
    () =>
      navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.exact}
          className={({ isActive }) =>
            `px-4 py-2 rounded-md text-sm font-semibold transition-colors ${
              isActive ? 'bg-emerald-500 text-white' : 'text-slate-600 hover:bg-emerald-100'
            }`
          }
        >
          {item.label}
        </NavLink>
      )),
    [],
  );

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <span className="text-lg font-bold text-emerald-600">Coopérative+</span>
          <nav className="flex items-center gap-3">{navLinks}</nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/members" element={<MembersPage />} />
          <Route path="/inventory" element={<InventoryPage />} />
        </Routes>
        <Outlet />
      </main>
    </div>
  );
}

export default App;
