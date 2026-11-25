import { useState, useEffect } from 'react';

export function SetupNotebook({ onVincular }) {
  const [usuarios, setUsuarios] = useState([]);
  const [erro, setErro] = useState('');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/usuarios')
      .then(res => res.json())
      .then(data => setUsuarios(data))
      .catch(() => setErro("Erro ao conectar com o servidor Python. Ele está rodando?"));
  }, []);

  const handleVincular = (usuario) => {
    localStorage.setItem('@estoque:usuario', JSON.stringify(usuario));
    onVincular(usuario);
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-900 text-white">
      <div className="bg-gray-800 p-8 rounded-lg shadow-xl border border-gray-700 max-w-md w-full">
        <h1 className="text-2xl font-bold mb-2 text-center text-blue-400">Bem-vindo ao Estoque</h1>
        <p className="text-gray-400 text-center mb-6 text-sm">Vincule este computador a um funcionário para começar.</p>
        
        {erro && <p className="text-red-400 text-sm mb-4 text-center">{erro}</p>}

        <div className="flex flex-col gap-3">
          {usuarios.map(u => (
            <button key={u.id} onClick={() => handleVincular(u)} className="bg-gray-700 hover:bg-gray-600 p-4 rounded text-left transition-colors border border-gray-600">
              <p className="font-bold">{u.nome}</p>
              <p className="text-xs text-gray-400">Papel: {u.papel} | Local: {u.localizacao}</p>
            </button>
          ))}
          {usuarios.length === 0 && !erro && <p className="text-center text-gray-500">Carregando usuários...</p>}
        </div>
      </div>
    </div>
  );
}