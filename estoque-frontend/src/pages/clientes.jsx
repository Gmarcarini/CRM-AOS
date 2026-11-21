import { useState, useEffect } from 'react';

export function Clientes({ usuario, irParaPedidos }) {
  const [clientes, setClientes] = useState([]);
  const [pedidosCliente, setPedidosCliente] = useState([]); // <-- AQUI DENTRO
  
  const [clienteSelecionado, setClienteSelecionado] = useState(null);
  const [formAberto, setFormAberto] = useState(false);
  const [modoEdicao, setModoEdicao] = useState(false);
  const [erro, setErro] = useState('');
  const [mensagemSucesso, setMensagemSucesso] = useState('');

  const [formData, setFormData] = useState({
    razao_social: '', codigo: '', cnpj: '', status: 'ativo',
    rua: '', numero: '', sala: '', bairro: '', cidade: '', estado: '', pais: 'Brasil'
  });
  const [contatos, setContatos] = useState([{ nome: '', telefone: '', email: '' }]);

  const buscarClientes = () => {
    fetch('http://127.0.0.1:8000/clientes')
      .then(res => res.json())
      .then(data => {
        setClientes(data);
        if (clienteSelecionado) {
          const atualizado = data.find(c => c.id === clienteSelecionado.id);
          if (atualizado) setClienteSelecionado(atualizado);
        }
      })
      .catch(err => console.error(err));
  };

  useEffect(() => { 
    buscarClientes(); 
    fetch('http://127.0.0.1:8000/pedidos').then(res => res.json()).then(data => setPedidosCliente(data));
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleContatoChange = (index, field, value) => {
    const novosContatos = [...contatos];
    novosContatos[index][field] = value;
    setContatos(novosContatos);
  };

  const adicionarContato = () => setContatos([...contatos, { nome: '', telefone: '', email: '' }]);
  const removerContato = (index) => setContatos(contatos.filter((_, i) => i !== index));

  const handleSalvar = async (e) => {
    e.preventDefault();
    setErro('');
    
    const payload = { ...formData, contatos };
    const url = modoEdicao 
      ? `http://127.0.0.1:8000/clientes/${clienteSelecionado.id}` 
      : 'http://127.0.0.1:8000/clientes';
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
        setMensagemSucesso(modoEdicao ? "Alterações salvas com sucesso!" : "Cliente criado com sucesso!");
        setTimeout(() => setMensagemSucesso(''), 3000);

        setFormAberto(false);
        setModoEdicao(false);
        buscarClientes();

        if (modoEdicao && clienteSelecionado) {
          const clienteAtualizado = { ...clienteSelecionado, ...formData };
          setClienteSelecionado(clienteAtualizado);
        } else {
          resetarFormulario(); 
        }
      } else {
        const data = await res.json();
        setErro(data.detail || "Erro ao salvar cliente.");
      }
    } catch (err) {
      setErro("Erro de conexão com o servidor.");
    }
  };

  const prepararEdicao = () => {
    setFormData({
      razao_social: clienteSelecionado.razao_social,
      codigo: clienteSelecionado.codigo,
      cnpj: clienteSelecionado.cnpj,
      status: clienteSelecionado.status,
      rua: clienteSelecionado.rua || '',
      numero: clienteSelecionado.numero || '',
      sala: clienteSelecionado.sala || '',
      bairro: clienteSelecionado.bairro || '',
      cidade: clienteSelecionado.cidade || '',
      estado: clienteSelecionado.estado || '',
      pais: clienteSelecionado.pais || 'Brasil'
    });
    setContatos(clienteSelecionado.contatos.map(c => ({
      nome: c.nome, telefone: c.telefone, email: c.email || ''
    })));
    setModoEdicao(true);
  };

  const resetarFormulario = () => {
    setFormData({ razao_social: '', codigo: '', cnpj: '', status: 'ativo', rua: '', numero: '', sala: '', bairro: '', cidade: '', estado: '', pais: 'Brasil' });
    setContatos([{ nome: '', telefone: '', email: '' }]);
    setErro('');
  };

  // TELA 1: DETALHES DO CLIENTE (LEITURA)
  if (clienteSelecionado && !modoEdicao) {
    const podeEditar = clienteSelecionado.usuario_responsavel_id === usuario.id || usuario.papel === 'admin';

    return (
      <div className="relative"> 
        {mensagemSucesso && (
          <div className="fixed top-8 right-8 bg-green-600 text-white px-6 py-3 rounded shadow-lg z-50 animate-bounce">
            ✅ {mensagemSucesso}
          </div>
        )}

        <div className="bg-gray-800 p-8 rounded-lg border border-gray-700 shadow-lg max-w-4xl mx-auto">
          <button onClick={() => setClienteSelecionado(null)} className="text-blue-400 hover:text-blue-300 mb-6 flex items-center gap-2 font-semibold">
            <span>&larr;</span> Voltar para lista
          </button>

          <div className="flex justify-between items-start mb-6 border-b border-gray-700 pb-4">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">{clienteSelecionado.razao_social}</h1>
              <p className="text-gray-400">CNPJ: {clienteSelecionado.cnpj} | Código: {clienteSelecionado.codigo}</p>
            </div>
            <div className="text-right">
              <span className={`inline-block px-3 py-1 rounded text-sm font-bold mb-4 ${clienteSelecionado.status === 'ativo' ? 'bg-green-900 text-green-300' : clienteSelecionado.status === 'standby' ? 'bg-yellow-900 text-yellow-300' : 'bg-red-900 text-red-300'}`}>
                {clienteSelecionado.status.toUpperCase()}
              </span>
              {podeEditar && (
                <button onClick={prepararEdicao} className="block bg-yellow-600 hover:bg-yellow-500 text-white px-4 py-2 rounded transition-colors font-bold w-full">
                  ✏️ Editar Cliente
                </button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div>
              <h3 className="text-blue-400 font-bold mb-2 text-lg">Endereço</h3>
              <p className="text-gray-300">Rua: {clienteSelecionado.rua}, {clienteSelecionado.numero}</p>
              {clienteSelecionado.sala && <p className="text-gray-300">Sala: {clienteSelecionado.sala}</p>}
              <p className="text-gray-300">Bairro: {clienteSelecionado.bairro}</p>
              <p className="text-gray-300">{clienteSelecionado.cidade} - {clienteSelecionado.estado}</p>
              <p className="text-gray-300">{clienteSelecionado.pais}</p>
            </div>

            <div>
              <h3 className="text-blue-400 font-bold mb-2 text-lg">Contatos</h3>
              {clienteSelecionado.contatos.map((c, i) => (
                <div key={i} className="bg-gray-900 p-3 rounded mb-2 border border-gray-700">
                  <p className="font-bold text-white">{c.nome}</p>
                  <p className="text-sm text-gray-400">{c.telefone}</p>
                  <p className="text-sm text-gray-400">{c.email}</p>
                </div>
              ))}
            </div>
          </div>

          {/* PEDIDOS DO CLIENTE AGRUPADOS */}
          <div className="border-t border-gray-700 pt-6">
            <h3 className="text-blue-400 font-bold mb-4 text-lg">Pedidos deste Cliente</h3>
            {pedidosCliente.filter(p => p.cliente_id === clienteSelecionado.id).length === 0 ? (
              <p className="text-gray-500">Nenhum pedido para este cliente.</p>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Array.from(new Set(pedidosCliente.filter(p => p.cliente_id === clienteSelecionado.id).map(p => p.sigla_produto))).map(sigla => (
                  <div key={sigla} onClick={() => irParaPedidos(sigla)} className="bg-gray-900 p-4 rounded-lg border border-gray-700 flex items-center gap-3 cursor-pointer hover:border-blue-500 transition-colors">
                    <span className="text-2xl">📁</span>
                    <div>
                      <p className="font-bold text-white">{sigla}</p>
                      <p className="text-xs text-gray-400">
                        {pedidosCliente.filter(p => p.cliente_id === clienteSelecionado.id && p.sigla_produto === sigla).length} pedidos
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

  // TELA 2: FORMULÁRIO (CRIAR / EDITAR)
  if (formAberto || modoEdicao) {
    return (
      <div>
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">{modoEdicao ? 'Editar Cliente' : 'Novo Cliente'}</h1>
          <button onClick={() => { setFormAberto(false); setModoEdicao(false); resetarFormulario(); }} className="text-gray-400 hover:text-white bg-gray-800 px-4 py-2 rounded">
            Cancelar
          </button>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-lg">
          {erro && <p className="text-red-400 mb-4 bg-red-900/30 p-2 rounded">{erro}</p>}
          
          <form onSubmit={handleSalvar} className="flex flex-col gap-6">
            <div>
              <h3 className="text-blue-400 font-bold mb-2 border-b border-gray-700 pb-1">Dados Principais</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="text-sm text-gray-400 block mb-1">Razão Social:</label>
                  <input type="text" name="razao_social" value={formData.razao_social} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-blue-500" required />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Código (ex: 001):</label>
                  <input type="text" name="codigo" value={formData.codigo} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-blue-500" required />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">CNPJ:</label>
                  <input type="text" name="cnpj" value={formData.cnpj} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-blue-500" required />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Status:</label>
                  <select name="status" value={formData.status} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-blue-500">
                    <option value="ativo">Ativo</option>
                    <option value="standby">Standby</option>
                    <option value="inativo">Inativo</option>
                  </select>
                </div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center border-b border-gray-700 pb-1 mb-2">
                <h3 className="text-blue-400 font-bold">Contatos</h3>
                <button type="button" onClick={adicionarContato} className="text-sm bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded">
                  + Adicionar outro contato
                </button>
              </div>
              {contatos.map((contato, index) => (
                <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-2 mb-2 items-end">
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Nome:</label>
                    <input type="text" value={contato.nome} onChange={(e) => handleContatoChange(index, 'nome', e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" required />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Telefone:</label>
                    <input type="text" value={contato.telefone} onChange={(e) => handleContatoChange(index, 'telefone', e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" placeholder="(+55) 51 99153-1100" required />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">E-mail:</label>
                    <input type="email" value={contato.email} onChange={(e) => handleContatoChange(index, 'email', e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" required />
                  </div>
                  {contatos.length > 1 && (
                    <button type="button" onClick={() => removerContato(index)} className="bg-red-900/50 text-red-400 p-2 rounded hover:bg-red-900">Remover</button>
                  )}
                </div>
              ))}
            </div>

            <div>
              <h3 className="text-blue-400 font-bold mb-2 border-b border-gray-700 pb-1">Endereço</h3>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div className="md:col-span-2">
                  <label className="text-sm text-gray-400 block mb-1">Rua:</label>
                  <input type="text" name="rua" value={formData.rua} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Número:</label>
                  <input type="text" name="numero" value={formData.numero} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Sala (Opcional):</label>
                  <input type="text" name="sala" value={formData.sala || ''} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" placeholder="Ex: Sala 402" />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Bairro:</label>
                  <input type="text" name="bairro" value={formData.bairro} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" />
                </div>
                <div className="md:col-span-2">
                  <label className="text-sm text-gray-400 block mb-1">Cidade:</label>
                  <input type="text" name="cidade" value={formData.cidade} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Estado:</label>
                  <input type="text" name="estado" value={formData.estado} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">País:</label>
                  <input type="text" name="pais" value={formData.pais} onChange={handleInputChange} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" />
                </div>
              </div>
            </div>

            <button type="submit" className="bg-green-600 hover:bg-green-500 text-white font-bold py-3 px-4 rounded mt-4 transition-colors">
              {modoEdicao ? 'Salvar Alterações' : 'Salvar Cliente'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // TELA 3: LISTAGEM DE CARDS (PADRÃO)
  return (
    <div className="relative">
      {mensagemSucesso && (
        <div className="fixed top-8 right-8 bg-green-600 text-white px-6 py-3 rounded shadow-lg z-50 animate-bounce">
          ✅ {mensagemSucesso}
        </div>
      )}

      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">Meus Clientes</h1>
        <button onClick={() => { resetarFormulario(); setFormAberto(true); }} className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded font-medium transition-colors">
          + Novo Cliente
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {clientes.map(cliente => (
          <div 
            key={cliente.id} 
            onClick={() => setClienteSelecionado(cliente)}
            className="bg-gray-800 p-5 rounded-lg border border-gray-700 shadow hover:border-blue-500 hover:bg-gray-750 cursor-pointer transition-all transform hover:-translate-y-1"
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-xl font-bold text-blue-400">{cliente.razao_social}</h3>
              <span className={`text-xs px-2 py-1 rounded ${cliente.status === 'ativo' ? 'bg-green-900 text-green-300' : cliente.status === 'standby' ? 'bg-yellow-900 text-yellow-300' : 'bg-red-900 text-red-300'}`}>
                {cliente.status.toUpperCase()}
              </span>
            </div>
            <p className="text-gray-300 text-sm mb-1">CNPJ: {cliente.cnpj}</p>
            <p className="text-gray-300 text-sm mb-1">Cidade: {cliente.cidade}</p>
            <span className="bg-gray-700 text-xs px-2 py-1 rounded text-gray-300">Cód: {cliente.codigo}</span>
            
            <div className="mt-4 border-t border-gray-700 pt-2">
              <p className="text-xs text-gray-500 mb-1">Contatos:</p>
              {cliente.contatos.map((c, i) => (
                <p key={i} className="text-xs text-gray-400">• {c.nome} ({c.telefone})</p>
              ))}
            </div>
          </div>
        ))}
        {clientes.length === 0 && <p className="text-gray-500 col-span-3">Nenhum cliente cadastrado ainda.</p>}
      </div>
    </div>
  );
}