import { useEffect, useRef } from 'react';
import $ from 'jquery';
import 'datatables.net-dt';
import 'datatables.net-dt/css/dataTables.dataTables.css';

const members = [
  { name: 'Amina Koné', role: 'Productrice de cacao', status: 'Active', dues: 'Payé', joinDate: '2020-03-12' },
  { name: 'Jean-Baptiste Ouedraogo', role: 'Cultivateur de sésame', status: 'Active', dues: 'Retard', joinDate: '2019-07-30' },
  { name: 'Fatou Diarra', role: 'Transform. beur', status: 'Active', dues: 'Payé', joinDate: '2021-11-08' },
  { name: 'Issa Traoré', role: 'Collecteur', status: 'Suspendu', dues: 'N/A', joinDate: '2018-05-21' },
];

function MembersPage() {
  const tableRef = useRef(null);

  useEffect(() => {
    const table = $(tableRef.current).DataTable({
      data: members,
      columns: [
        { title: 'Nom', data: 'name' },
        { title: 'Rôle', data: 'role' },
        { title: 'Statut', data: 'status' },
        { title: 'Cotisations', data: 'dues' },
        { title: 'Date d’adhésion', data: 'joinDate' },
      ],
      paging: true,
      searching: true,
      language: {
        url: 'https://cdn.datatables.net/plug-ins/1.13.7/i18n/fr-FR.json',
      },
    });

    return () => {
      table.destroy(true);
    };
  }, []);

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h1 className="mb-4 text-xl font-semibold text-slate-700">Gestion des membres</h1>
      <div className="overflow-x-auto">
        <table ref={tableRef} className="display w-full text-sm" />
      </div>
    </section>
  );
}

export default MembersPage;
