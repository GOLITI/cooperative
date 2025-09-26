const inventory = [
  { id: 'PR-001', name: 'Maïs jaune', stock: 1250, unit: 'kg', reorderPoint: 400 },
  { id: 'PR-017', name: 'Beurre de karité', stock: 85, unit: 'kg', reorderPoint: 60 },
  { id: 'PR-204', name: 'Café robusta', stock: 370, unit: 'kg', reorderPoint: 120 },
];

function InventoryPage() {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h1 className="mb-4 text-xl font-semibold text-slate-700">Stock actuel</h1>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-2 text-left font-semibold text-slate-600">Code</th>
              <th className="px-4 py-2 text-left font-semibold text-slate-600">Produit</th>
              <th className="px-4 py-2 text-left font-semibold text-slate-600">Stock</th>
              <th className="px-4 py-2 text-left font-semibold text-slate-600">Unité</th>
              <th className="px-4 py-2 text-left font-semibold text-slate-600">Seuil</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {inventory.map((item) => (
              <tr key={item.id} className="hover:bg-slate-50">
                <td className="px-4 py-2 font-medium text-slate-700">{item.id}</td>
                <td className="px-4 py-2 text-slate-600">{item.name}</td>
                <td className="px-4 py-2 text-slate-600">{item.stock.toLocaleString('fr-FR')}</td>
                <td className="px-4 py-2 text-slate-600">{item.unit}</td>
                <td className="px-4 py-2 text-slate-600">{item.reorderPoint.toLocaleString('fr-FR')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default InventoryPage;
