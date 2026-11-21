import { useState } from 'react';

export function ModalSelecao({ titulo, lista, aoSelecionar, aoFechar, tipo }) {
  const [busca, setBusca] = useState('');

  const itensFiltrados = lista.filter(item => {
    const nome = tipo === 'cliente' ? item.razao_social : item.nome;
    return nome.toLowerCase().includes(busca.toLowerCase());
  });

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl border border-gray-700 flex flex-col max-h-[80vh]">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4">{titulo}</h2>
          <input 
            type="text" 
            placeholder="Pesquisar..."
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="p-6 overflow-y-auto flex-1 flex flex-col gap-3">
          {itensFiltrados.map(item => {
            const nome = tipo === 'cliente' ? item.razao_social : item.nome;
            const subtitulo = tipo === 'cliente' ? `CNPJ: ${item.cnpj}` : `Contato: ${item.nome_contato}`;
            
            return (
              <div 
                key={item.id} 
                onClick={() => aoSelecionar(item)}
                className="bg-gray-900 p-4 rounded-lg border border-gray-700 cursor-pointer hover:border-blue-500 transition-colors"
              >
                <h3 className="font-bold text-blue-400">{nome}</h3>
                <p className="text-sm text-gray-400">{subtitulo}</p>
              </div>
            );
          })}
          {itensFiltrados.length === 0 && <p className="text-gray-500 text-center">Nenhum resultado encontrado.</p>}
        </div>

        <div className="p-6 border-t border-gray-700 flex justify-end">
          <button onClick={aoFechar} className="bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-600">Fechar</button>
        </div>
      </div>
    </div>
  );
}