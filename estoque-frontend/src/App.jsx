import { useState, useEffect } from 'react';
import { SetupNotebook } from './pages/Setup';
import { Dashboard } from './pages/Dashboard';
import { Clientes } from './pages/Clientes';
import { Fornecedores } from './pages/Fornecedores';
import { Pedidos } from './pages/Pedidos';

export default function App() {
  const [usuarioLogado, setUsuarioLogado] = useState(null);
  const [menuAberto, setMenuAberto] = useState(true);
  const [paginaAtual, setPaginaAtual] = useState('dashboard');
  const [pastaInicial, setPastaInicial] = useState(null);

  useEffect(() => {
    const usuarioSalvo = localStorage.getItem('@estoque:usuario');
    if (usuarioSalvo) {
      setUsuarioLogado(JSON.parse(usuarioSalvo));
    }
  }, []);

  if (!usuarioLogado) {
    return <SetupNotebook onVincular={setUsuarioLogado} />;
  }

  return (
    <div className="flex h-screen bg-gray-900 text-white font-sans">
      <aside className={`bg-gray-800 transition-all duration-300 ${menuAberto ? 'w-64' : 'w-20'} flex flex-col justify-between p-4 shadow-lg shrink-0`}>
        <div>
          <button onClick={() => setMenuAberto(!menuAberto)} className="mb-8 p-2 bg-gray-700 rounded hover:bg-gray-600 text-sm w-full transition-colors">
            {menuAberto ? '<< Fechar' : '>>'}
          </button>
          
          <nav className="flex flex-col gap-2">
            <button onClick={() => setPaginaAtual('dashboard')} className={`text-left p-2 rounded transition-colors ${paginaAtual === 'dashboard' ? 'bg-gray-700' : 'hover:bg-gray-700'}`}>
              Dashboard
            </button>
            <button onClick={() => setPaginaAtual('clientes')} className={`text-left p-2 rounded transition-colors ${paginaAtual === 'clientes' ? 'bg-gray-700' : 'hover:bg-gray-700'}`}>
              Meus Clientes
            </button>
            <button onClick={() => setPaginaAtual('fornecedores')} className={`text-left p-2 rounded transition-colors ${paginaAtual === 'fornecedores' ? 'bg-gray-700' : 'hover:bg-gray-700'}`}>
              Fornecedores
            </button>
            <button onClick={() => {setPastaInicial(null); setPaginaAtual('pedidos');}} className={`text-left p-2 rounded transition-colors ${paginaAtual === 'pedidos' ? 'bg-gray-700' : 'hover:bg-gray-700'}`}>
              Pedidos
            </button>
            <button className="text-left p-2 rounded hover:bg-gray-700 transition-colors opacity-50 cursor-not-allowed">Movimentar Estoque (Breve)</button>
          </nav>
        </div>
        
        <div className="border-t border-gray-700 pt-4">
          <p className="text-sm font-bold text-white">{usuarioLogado.nome}</p>
          <p className="text-xs text-gray-400 mb-2">{usuarioLogado.papel.toUpperCase()}</p>
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-y-auto">
        {paginaAtual === 'dashboard' && <Dashboard usuario={usuarioLogado} />}
        {paginaAtual === 'clientes' && <Clientes usuario={usuarioLogado} irParaPedidos={(pasta) => { setPastaInicial(pasta); setPaginaAtual('pedidos'); }} />}
        {paginaAtual === 'fornecedores' && <Fornecedores usuario={usuarioLogado} irParaPedidos={(pasta) => { setPastaInicial(pasta); setPaginaAtual('pedidos'); }} />}
        {paginaAtual === 'pedidos' && <Pedidos usuario={usuarioLogado} pastaInicial={pastaInicial} limparPastaInicial={() => setPastaInicial(null)} />}
      </main>
    </div>
  );
}
