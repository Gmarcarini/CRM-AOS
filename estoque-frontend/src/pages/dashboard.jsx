import { useState, useEffect } from 'react';

export function Dashboard({ usuario }) {
  const [amostras, setAmostras] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/amostras')
      .then(res => res.json())
      .then(data => setAmostras(data))
      .catch(err => console.error(err));
  }, []);

  const corFundo = usuario.localizacao === 'brasil' 
    ? 'from-green-600 to-yellow-500' 
    : 'from-red-700 to-yellow-500';

  return (
    <div>
      <header className={`bg-gradient-to-r ${corFundo} p-6 rounded-lg shadow-md flex justify-between items-center mb-8`}>
        <h1 className="text-3xl font-bold text-white">Olá, {usuario.nome}</h1>
        <span className="bg-white/20 px-4 py-2 rounded font-semibold text-white">📍 {usuario.localizacao.toUpperCase()}</span>
      </header>

      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-white">Minhas Amostras:</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {amostras.map((amostra) => (
          <div key={amostra.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700 shadow hover:border-gray-500 transition-colors">
            <h3 className="text-blue-400 font-bold mb-2 truncate">{amostra.id}</h3>
            <p className="text-gray-300 text-sm mb-1"><span className="text-gray-500">Desc:</span> {amostra.descricao}</p>
            <p className="text-gray-300 text-sm mb-1"><span className="text-gray-500">Cliente:</span> {amostra.cliente}</p>
            <p className="text-gray-300 text-sm"><span className="text-gray-500">Status:</span> <span className="bg-gray-700 px-2 py-0.5 rounded text-xs">{amostra.status}</span></p>
          </div>
        ))}
        {amostras.length === 0 && <p className="text-gray-500">Nenhuma amostra cadastrada.</p>}
      </div>
    </div>
  );
}