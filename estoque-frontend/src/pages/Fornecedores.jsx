import { useState, useEffect } from 'react';

export function Fornecedores({ usuario, irParaPedidos }) {
  const [fornecedores, setFornecedores] = useState([]);
  const [pedidosFornecedor, setPedidosFornecedor] = useState([]); // <-- AQUI
  
  const [fornecedorSelecionado, setFornecedorSelecionado] = useState(null);
  const [formAberto, setFormAberto] = useState(false);
  const [modoEdicao, setModoEdicao] = useState(false);
  const [erro, setErro] = useState('');
  const [mensagemSucesso, setMensagemSucesso] = useState('');
  
  const [categorias, setCategorias] = useState([]);
  const [mostrarSugestoes, setMostrarSugestoes] = useState(false);

  const [formData, setFormData] = useState({
    nome: '', nome_contato: '', categoria_produtos: '', pedidos: []
  });

  const buscarFornecedores = () => {
    fetch('http://127.0.0.1:8000/fornecedores')
      .then(res => res.json())
      .then(data => {
        setFornecedores(data);
        if (fornecedorSelecionado) {
          const atualizado = data.find(f => f.id === fornecedorSelecionado.id);
          if (atualizado) setFornecedorSelecionado(atualizado);
        }
      })
      .catch(err => console.error(err));
  };

  const buscarCategorias = () => {
    fetch('http://127.0.0.1:8000/categorias')
      .then(res => res.json())
      .then(data => setCategorias(data))
      .catch(err => console.error(err));
  };

  useEffect(() => { 
    buscarFornecedores(); 
    buscarCategorias(); 
    fetch('http://127.0.0.1:8000/pedidos').then(res => res.json()).then(data => setPedidosFornecedor(data)); // <-- AQUI
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSalvar = async (e) => {
    e.preventDefault();
    setErro('');
    
    const payload = { ...formData };
    const url = modoEdicao 
      ? `http://127.0.0.1:8000/fornecedores/${fornecedorSelecionado.id}` 
      : 'http://127.0.0.1:8000/fornecedores';
    const method = modoEdicao ? 'PUT' : 'POST';

    try {
      const res = await fetch(url, {
        method,
        headers: { 
          'Content-Type': 'application/json',
          'x-usuario-id': usuario.id
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setMensagemSucesso(modoEdicao ? "Fornecedor atualizado com sucesso!" : "Fornecedor criado com sucesso!");
        setTimeout(() => setMensagemSucesso(''), 3000);
        
        setFormAberto(false);
        setModoEdicao(false);
        
        buscarFornecedores();
        buscarCategorias();

        if (modoEdicao && fornecedorSelecionado) {
          const atualizado = { ...fornecedorSelecionado, ...formData };
          setFornecedorSelecionado(atualizado);
        } else {
          resetarFormulario(); 
        }
      } else {
        const data = await res.json();
        setErro(data.detail || "Erro ao salvar fornecedor.");
      }
    } catch (err) {
      setErro("Erro de conexão com o servidor.");
    }
  };

  const prepararEdicao = () => {
    setFormData({
      nome: fornecedorSelecionado.nome,
      nome_contato: fornecedorSelecionado.nome_contato,
      categoria_produtos: fornecedorSelecionado.categoria_produtos || '',
      pedidos: fornecedorSelecionado.pedidos || []
    });
    setModoEdicao(true);
  };

  const resetarFormulario = () => {
    setFormData({ nome: '', nome_contato: '', categoria_produtos: '', pedidos: [] });
    setErro('');
    setMostrarSugestoes(false);
  };

  // TELA 1: DETALHES DO FORNECEDOR
  if (fornecedorSelecionado && !modoEdicao) {
    const podeEditar = fornecedorSelecionado.usuario_responsavel_id === usuario.id || usuario.papel === 'admin';

    return (
      <div className="relative"> 
        {mensagemSucesso && (
          <div className="fixed top-8 right-8 bg-green-600 text-white px-6 py-3 rounded shadow-lg z-50 animate-bounce">
            ✅ {mensagemSucesso}
          </div>
        )}

        <div className="bg-gray-800 p-8 rounded-lg border border-gray-700 shadow-lg max-w-4xl mx-auto">
          <button onClick={() => setFornecedorSelecionado(null)} className="text-blue-400 hover:text-blue-300 mb-6 flex items-center gap-2 font-semibold">
            <span>&larr;</span> Voltar para lista
          </button>

          <div className="flex justify-between items-start mb-6 border-b border-gray-700 pb-4">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">{fornecedorSelecionado.nome}</h1>
              <p className="text-gray-400">Contato: {fornecedorSelecionado.nome_contato}</p>
              <p className="text-gray-400">Categoria: {fornecedorSelecionado.categoria_produtos || 'Não informada'}</p>
            </div>
            <div className="text-right">
              {podeEditar && (
                <button onClick={prepararEdicao} className="block bg-yellow-600 hover:bg-yellow-500 text-white px-4 py-2 rounded transition-colors font-bold w-full">
                  ✏️ Editar Fornecedor
                </button>
              )}
            </div>
          </div>

          {/* PEDIDOS DO FORNECEDOR AGRUPADOS */}
          <div className="border-t border-gray-700 pt-6">
            <h3 className="text-blue-400 font-bold mb-4 text-lg">Pedidos deste Fornecedor</h3>
            
            {pedidosFornecedor.filter(p => p.fornecedor_id === fornecedorSelecionado.id).length === 0 ? (
              <p className="text-gray-500">Nenhum pedido para este fornecedor.</p>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Array.from(new Set(pedidosFornecedor.filter(p => p.fornecedor_id === fornecedorSelecionado.id).map(p => p.sigla_produto))).map(sigla => (
                  <div key={sigla} onClick={() => irParaPedidos(sigla)} className="bg-gray-900 p-4 rounded-lg border border-gray-700 flex items-center gap-3 cursor-pointer hover:border-blue-500 transition-colors">
                    <span className="text-2xl">📁</span>
                    <div>
                      <p className="font-bold text-white">{sigla}</p>
                      <p className="text-xs text-gray-400">
                        {pedidosFornecedor.filter(p => p.fornecedor_id === fornecedorSelecionado.id && p.sigla_produto === sigla).length} pedidos
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // TELA 2: FORMULÁRIO
  if (formAberto || modoEdicao) {
    const categoriasFiltradas = categorias.filter(cat => 
      cat.toLowerCase().includes(formData.categoria_produtos.toLowerCase())
    );

    return (
      <div>
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">{modoEdicao ? 'Editar Fornecedor' : 'Novo Fornecedor'}</h1>
          <button onClick={() => { setFormAberto(false); setModoEdicao(false); resetarFormulario(); }} className="text-gray-400 hover:text-white bg-gray-800 px-4 py-2 rounded">
            Cancelar
          </button>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-lg max-w-2xl">
          {erro && <p className="text-red-400 mb-4 bg-red-900/30 p-2 rounded">{erro}</p>}
          
          <form onSubmit={handleSalvar} className="flex flex-col gap-6">
            <div>
              <h3 className="text-blue-400 font-bold mb-2 border-b border-gray-700 pb-1">Dados do Fornecedor</h3>
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Nome (Empresa/Fornecedor):</label>
                  <input type="text" name="nome" value={formData.nome} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-blue-500" required />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Nome do Contato:</label>
                  <input type="text" name="nome_contato" value={formData.nome_contato} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-blue-500" required />
                </div>
                
                <div className="relative">
                  <label className="text-sm text-gray-400 block mb-1">Categoria dos Produtos:</label>
                  <input 
                    type="text" 
                    name="categoria_produtos" 
                    value={formData.categoria_produtos} 
                    onChange={(e) => {
                      handleInputChange(e);
                      setMostrarSugestoes(true);
                    }}
                    onFocus={() => setMostrarSugestoes(true)} 
                    onBlur={() => setTimeout(() => setMostrarSugestoes(false), 200)}
                    className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-blue-500" 
                    placeholder="Ex: Embalagens (digite para buscar ou criar)" 
                  />

                  {mostrarSugestoes && (
                    <ul className="absolute z-10 w-full bg-gray-700 border border-gray-600 rounded mt-1 max-h-48 overflow-y-auto shadow-lg">
                      {categoriasFiltradas.map((cat, index) => (
                        <li 
                          key={index} 
                          onClick={() => {
                            setFormData(prev => ({ ...prev, categoria_produtos: cat }));
                            setMostrarSugestoes(false);
                          }}
                          className="p-2 hover:bg-gray-600 cursor-pointer text-white text-sm"
                        >
                          {cat}
                        </li>
                      ))}
                      
                      {formData.categoria_produtos.length > 0 && 
                       !categorias.some(cat => cat.toLowerCase() === formData.categoria_produtos.toLowerCase()) && (
                        <li 
                          onClick={() => setMostrarSugestoes(false)}
                          className="p-2 text-blue-300 hover:bg-gray-600 cursor-pointer text-sm italic"
                        >
                          + Criar nova categoria: "{formData.categoria_produtos}"
                        </li>
                      )}
                    </ul>
                  )}
                </div>
              </div>
            </div>

            <button type="submit" className="bg-green-600 hover:bg-green-500 text-white font-bold py-3 px-4 rounded mt-4 transition-colors">
              {modoEdicao ? 'Salvar Alterações' : 'Cadastrar Fornecedor'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // TELA 3: LISTAGEM
  return (
    <div className="relative">
      {mensagemSucesso && (
        <div className="fixed top-8 right-8 bg-green-600 text-white px-6 py-3 rounded shadow-lg z-50 animate-bounce">
          ✅ {mensagemSucesso}
        </div>
      )}

      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">Meus Fornecedores</h1>
        <button onClick={() => { resetarFormulario(); setFormAberto(true); }} className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded font-medium transition-colors">
          + Novo Fornecedor
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {fornecedores.map(f => (
          <div 
            key={f.id} 
            onClick={() => setFornecedorSelecionado(f)}
            className="bg-gray-800 p-5 rounded-lg border border-gray-700 shadow hover:border-blue-500 hover:bg-gray-750 cursor-pointer transition-all transform hover:-translate-y-1"
          >
            <h3 className="text-xl font-bold text-blue-400 mb-2">{f.nome}</h3>
            <p className="text-gray-300 text-sm mb-1">Contato: {f.nome_contato}</p>
            <p className="text-gray-300 text-sm mb-3">Cat: {f.categoria_produtos || 'N/A'}</p>
            
            <div className="border-t border-gray-700 pt-2">
              <p className="text-xs text-gray-500">Pedidos vinculados: {f.pedidos?.length || 0}</p>
            </div>
          </div>
        ))}
        {fornecedores.length === 0 && <p className="text-gray-500 col-span-3">Nenhum fornecedor cadastrado ainda.</p>}
      </div>
    </div>
  );
}