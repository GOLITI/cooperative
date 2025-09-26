import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend);

const fetchMetrics = async () => {
  await new Promise((resolve) => setTimeout(resolve, 200));
  return {
    revenue: [4200, 5800, 6100, 7200, 6900, 8400],
    expenses: [3100, 3600, 2900, 5100, 4300, 5200],
    labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'],
    memberGrowth: [12, 18, 15, 25, 27, 32],
  };
};

function DashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ['dashboard-metrics'], queryFn: fetchMetrics, staleTime: 1000 * 60 });

  const barData = useMemo(() => {
    if (!data) return null;
    return {
      labels: data.labels,
      datasets: [
        {
          label: 'Chiffre d’affaires',
          data: data.revenue,
          backgroundColor: 'rgba(16, 185, 129, 0.7)',
          borderRadius: 6,
        },
        {
          label: 'Dépenses',
          data: data.expenses,
          backgroundColor: 'rgba(248, 113, 113, 0.7)',
          borderRadius: 6,
        },
      ],
    };
  }, [data]);

  const lineData = useMemo(() => {
    if (!data) return null;
    return {
      labels: data.labels,
      datasets: [
        {
          label: 'Nouveaux membres',
          data: data.memberGrowth,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.25)',
          fill: true,
          tension: 0.4,
        },
      ],
    };
  }, [data]);

  if (isLoading) {
    return <p className="text-sm text-slate-500">Chargement des indicateurs…</p>;
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-slate-700">Flux financiers</h2>
        {barData && <Bar data={barData} options={{ responsive: true, maintainAspectRatio: false }} height={280} />}
      </section>
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-slate-700">Croissance des membres</h2>
        {lineData && <Line data={lineData} options={{ responsive: true, maintainAspectRatio: false }} height={280} />}
      </section>
    </div>
  );
}

export default DashboardPage;
