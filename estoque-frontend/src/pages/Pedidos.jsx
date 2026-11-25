import { useState, useEffect } from 'react';
import { DetalhesPedido } from './DetalhesPedido';
import { ModalSelecao } from './ModalSelecao'; 

export function Pedidos({ usuario, pastaInicial, limparPastaInicial }) {
  const [pedidos, setPedidos] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [fornecedores, setFornecedores] = useState([]);
  const [pedidoSelecionado, setPedidoSelecionado] = useState(null);
  
  const [formAberto, setFormAberto] = useState(false);
  const [erro, setErro] = useState('');
  const [mensagemSucesso, setMensagemSucesso] = useState('');
  
  const [siglaCliente, setSiglaCliente] = useState('');
  const [siglaProduto, setSiglaProduto] = useState('');
  const [hscode, setHscode] = useState('');
  const [incoterm, setIncoterm] = useState('FOB');
  const [portoCarregamento, setPortoCarregamento] = useState('Shenzhen, China');
  const [portoDestino, setPortoDestino] = useState('Paranaguá, PR');
  const [tempoProducao, setTempoProducao] = useState('45 dias');
  const [pagamentos, setPagamentos] = useState('30% / 70%');
  
  const [modalAberto, setModalAberto] = useState(null);
  const [clienteSelecionado, setClienteSelecionado] = useState(null);
  const [fornecedorSelecionado, setFornecedorSelecionado] = useState(null);

  const [pastaAberta, setPastaAberta] = useState(null);
  const [busca, setBusca] = useState('');
  const [clienteFiltro, setClienteFiltro] = useState(null);

  // Função para limpar todos os campos do formulário
  const resetForm = () => {
    setClienteSelecionado(null);
    setFornecedorSelecionado(null);
    setSiglaCliente('');
    setSiglaProduto('');
    setHscode('');
    setIncoterm('FOB');
    setPortoCarregamento('Shenzhen, China');
    setPortoDestino('Paranaguá, PR');
    setTempoProducao('45 dias');
    setPagamentos('30% / 70%');
    setErro('');
    setModalAberto(null);
  };

  const buscarDados = () => {
    fetch('http://127.0.0.1:8000/pedidos').then(res => res.json()).then(data => setPedidos(data));
    fetch('http://127.0.0.1:8000/clientes').then(res => res.json()).then(data => setClientes(data));
    fetch('http://127.0.0.1:8000/fornecedores').then(res => res.json()).then(data => setFornecedores(data));
  };

  useEffect(() => { buscarDados(); }, []);

  useEffect(() => {
    if (pastaInicial) {
      setPastaAberta(pastaInicial);
      limparPastaInicial(); 
    }
  }, [pastaInicial]);

  const handleSalvar = async (e) => {
    e.preventDefault();
    setErro('');
    
    if (!clienteSelecionado || !fornecedorSelecionado) {
      setErro("Por favor, selecione um cliente e um fornecedor.");
      return;
    }

    const payload = { 
      cliente_id: clienteSelecionado.id, 
      fornecedor_id: fornecedorSelecionado.id, 
      sigla_cliente: siglaCliente, 
      sigla_produto: siglaProduto,
      hscode, incoterm, porto_carregamento: portoCarregamento,
      porto_destino: portoDestino, tempo_producao: tempoProducao, pagamentos
    };

    try {
      const res = await fetch('http://127.0.0.1:8000/pedidos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-usuario-id': usuario.id },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        setMensagemSucesso(`Pedido ${data.codigo_gerado} criado com sucesso!`);
        setTimeout(() => setMensagemSucesso(''), 4000);
        
        setFormAberto(false);
        resetForm(); // Limpa o form após salvar com sucesso
        buscarDados();
      } else {
        const data = await res.json();
        const mensagemErro = typeof data.detail === 'string' ? data.detail : data.detail[0]?.msg || "Erro ao criar pedido.";
        setErro(mensagemErro);
      }
    } catch (err) {
      setErro("Erro de conexão com o servidor.");
    }
  };

  const getNomeCliente = (id) => clientes.find(c => c.id === id)?.razao_social || "Carregando...";
  const getNomeFornecedor = (id) => fornecedores.find(f => f.id === id)?.nome || "Carregando...";

  const pedidosFiltradosPorCliente = clienteFiltro ? pedidos.filter(p => p.cliente_id === clienteFiltro) : pedidos;
  const pedidosAgrupados = pedidosFiltradosPorCliente.reduce((acc, pedido) => {
    const sigla = pedido.sigla_produto || "OUTROS";
    if (!acc[sigla]) acc[sigla] = [];
    acc[sigla].push(pedido);
    return acc;
  }, {});

  const siglasFiltradas = Object.keys(pedidosAgrupados).filter(sigla => 
    sigla.toLowerCase().includes(busca.toLowerCase())
  );

  // Função para abrir o formulário sempre limpo
  const abrirFormulario = () => {
    resetForm();
    setFormAberto(true);
  };

  // Função para fechar o formulário e limpar
  const fecharFormulario = () => {
    resetForm();
    setFormAberto(false);
  };

  return (
    <div className="relative">
      {mensagemSucesso && (
        <div className="fixed top-8 right-8 bg-green-600 text-white px-6 py-3 rounded shadow-lg z-50 animate-bounce">
          ✅ {mensagemSucesso}
        </div>
      )}

      {/* 1. VERIFICA SE UM PEDIDO FOI SELECIONADO */}
      {pedidoSelecionado ? (
        <DetalhesPedido 
          pedido={pedidoSelecionado} clientes={clientes} fornecedores={fornecedores} aoVoltar={() => setPedidoSelecionado(null)} 
        />
      ) : formAberto ? (
        
        /* 2. TELA DO FORMULÁRIO (TELA CHEIA) */
        <div className="bg-gray-800 p-8 rounded-lg border border-gray-700 shadow-lg max-w-4xl mx-auto">
          <div className="flex justify-between items-center mb-6 border-b border-gray-700 pb-4">
            <h2 className="text-2xl font-bold text-white">Criar Novo Pedido</h2>
            <button onClick={fecharFormulario} className="bg-red-600 text-white px-6 py-2 rounded hover:bg-red-500 font-bold w-full md:w-auto">
              Cancelar
            </button>
          </div>
          
          {erro && <p className="text-red-400 mb-4 bg-red-900/30 p-2 rounded">{erro}</p>}
          
          <form onSubmit={handleSalvar} className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex flex-col gap-4">
              <div>
                <label className="text-sm text-gray-400 block mb-1">Cliente:</label>
                <button type="button" onClick={() => setModalAberto('cliente')} className="w-full bg-blue-600 hover:bg-blue-500 text-white p-2 rounded text-left transition-colors">
                  {clienteSelecionado ? clienteSelecionado.razao_social : 'Selecionar Cliente'}
                </button>
                {clienteSelecionado && (
                  <div className="mt-2 text-sm text-gray-400 bg-gray-900 p-3 rounded border border-gray-700">
                    <p><strong>CNPJ:</strong> {clienteSelecionado.cnpj}</p>
                    <p><strong>Endereço:</strong> {clienteSelecionado.rua}, {clienteSelecionado.numero} - {clienteSelecionado.cidade}</p>
                    <p><strong>Contato:</strong> {clienteSelecionado.contatos[0]?.nome} - {clienteSelecionado.contatos[0]?.telefone}</p>
                  </div>
                )}
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-1">Fornecedor:</label>
                <button type="button" onClick={() => setModalAberto('fornecedor')} className="w-full bg-blue-600 hover:bg-blue-500 text-white p-2 rounded text-left transition-colors">
                  {fornecedorSelecionado ? fornecedorSelecionado.nome : 'Selecionar Fornecedor'}
                </button>
                {fornecedorSelecionado && (
                  <div className="mt-2 text-sm text-gray-400 bg-gray-900 p-3 rounded border border-gray-700">
                    <p><strong>Contato:</strong> {fornecedorSelecionado.nome_contato}</p>
                    <p><strong>Categoria:</strong> {fornecedorSelecionado.categoria_produtos}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="flex flex-col gap-4">
              <div>
                <label className="text-sm text-gray-400 block mb-1">HSCODE:</label>
                <input type="text" value={hscode} onChange={e => setHscode(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" required placeholder="7190" />
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-1">INCOTERM:</label>
                <select value={incoterm} onChange={e => setIncoterm(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white">
                  <option value="FOB">FOB</option><option value="EXW">EXW</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-1">Porto de Carregamento:</label>
                <input type="text" value={portoCarregamento} onChange={e => setPortoCarregamento(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" />
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-1">Porto de Destino:</label>
                <input type="text" value={portoDestino} onChange={e => setPortoDestino(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" />
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-1">Tempo de Produção:</label>
                <select value={tempoProducao} onChange={e => setTempoProducao(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white">
                  <option value="30 dias">30 dias</option><option value="45 dias">45 dias</option><option value="60 dias">60 dias</option><option value="90 dias">90 dias</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-1">Pagamentos:</label>
                <select value={pagamentos} onChange={e => setPagamentos(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white">
                  <option value="30% / 70%">30% / 70%</option><option value="50% / 50%">50% / 50%</option>
                </select>
              </div>
            </div>

            <div className="md:col-span-2 grid grid-cols-2 gap-4 mt-2 border-t border-gray-700 pt-4">
              <div>
                <label className="text-sm text-gray-400 block mb-1">Sigla do Cliente (ex: CB):</label>
                <input type="text" value={siglaCliente} onChange={e => setSiglaCliente(e.target.value.toUpperCase())} maxLength={2} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" required />
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-1">Sigla do Produto (ex: TC):</label>
                <input type="text" value={siglaProduto} onChange={e => setSiglaProduto(e.target.value.toUpperCase())} maxLength={2} className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white" required />
              </div>
            </div>

            <div className="md:col-span-2 mt-4">
              <button type="submit" className="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-3 px-4 rounded">Criar Pedido</button>
            </div>
          </form>
        </div>
      ) : (
        
        /* 3. TELA DA LISTA DE PASTAS */
        <>
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-white">Meus Pedidos</h1>
            {/* Alterado para usar a função abrirFormulario */}
            <button onClick={abrirFormulario} className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded font-medium">
              + Novo Pedido
            </button>
          </div>

          {!pastaAberta ? (
            <div>
              <div className="mb-8 space-y-4">
                <div className="relative">
                  <span className="absolute left-4 top-3 text-gray-400">🔍</span>
                  <input type="text" placeholder="Procurar projeto (sigla)..." value={busca} onChange={(e) => setBusca(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded-lg py-3 pl-12 pr-4 text-white focus:outline-none focus:border-blue-500 transition-colors" />
                </div>
                <div className="flex flex-wrap gap-2">
                  <button onClick={() => setClienteFiltro(null)} className={`px-4 py-1.5 rounded-full border text-sm ${clienteFiltro === null ? 'bg-blue-600 border-blue-500 text-white' : 'bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700'}`}>Todos os Clientes</button>
                  {clientes.map(c => (
                    <button key={c.id} onClick={() => setClienteFiltro(c.id)} className={`px-4 py-1.5 rounded-full border text-sm ${clienteFiltro === c.id ? 'bg-blue-600 border-blue-500 text-white' : 'bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700'}`}>{c.razao_social}</button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {siglasFiltradas.map(sigla => (
                  <div key={sigla} onClick={() => setPastaAberta(sigla)} className="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-lg hover:border-blue-500 cursor-pointer flex items-center gap-4 transition-transform hover:-translate-y-1">
                    <div className="text-4xl text-yellow-500">📁</div>
                    <div>
                      <h3 className="text-2xl font-bold text-white">{sigla}</h3>
                      <p className="text-gray-400 text-sm">{pedidosAgrupados[sigla].length} pedidos</p>
                    </div>
                  </div>
                ))}
                {siglasFiltradas.length === 0 && <p className="text-gray-500 col-span-4">Nenhum projeto encontrado com estes filtros.</p>}
              </div>
            </div>
          ) : (
            <div>
              <button onClick={() => setPastaAberta(null)} className="text-blue-400 hover:text-blue-300 mb-6 flex items-center gap-2 font-semibold bg-gray-800 px-4 py-2 rounded">
                <span>&larr;</span> Voltar para pastas
              </button>
              <h2 className="text-2xl font-bold mb-4 text-white flex items-center gap-2"><span className="text-yellow-500">📁</span> Pasta: {pastaAberta}</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {(pedidosAgrupados[pastaAberta] || []).sort((a,b) => b.numero_sequencial - a.numero_sequencial).map(p => (
                  <div key={p.id} onClick={() => setPedidoSelecionado(p)} className="bg-gray-800 p-5 rounded-lg border border-gray-700 shadow cursor-pointer hover:border-blue-500 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-xl font-bold text-blue-400">{p.codigo}</h3>
                      <span className="bg-gray-700 text-xs px-2 py-1 rounded text-gray-300">{p.status.toUpperCase()}</span>
                    </div>
                    <p className="text-gray-300 text-sm mb-1"><span className="text-gray-500">Cliente:</span> {getNomeCliente(p.cliente_id)}</p>
                    <p className="text-gray-300 text-sm mb-1"><span className="text-gray-500">Fornecedor:</span> {getNomeFornecedor(p.fornecedor_id)}</p>
                    <p className="text-gray-300 text-sm mt-3"><span className="text-gray-500">Etapa:</span> <span className="bg-gray-900 px-2 py-0.5 rounded text-xs">{p.processo_atual.replace(/_/g, ' ').toUpperCase()}</span></p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {modalAberto === 'cliente' && (
        <ModalSelecao titulo="Selecione um Cliente" lista={clientes} tipo="cliente" aoSelecionar={(c) => { setClienteSelecionado(c); setModalAberto(null); }} aoFechar={() => setModalAberto(null)} />
      )}
      {modalAberto === 'fornecedor' && (
        <ModalSelecao titulo="Selecione um Fornecedor" lista={fornecedores} tipo="fornecedor" aoSelecionar={(f) => { setFornecedorSelecionado(f); setModalAberto(null); }} aoFechar={() => setModalAberto(null)} />
      )}
    </div>
  );
}