import { useState } from 'react';

export function DetalhesPedido({ pedido, clientes, fornecedores, aoVoltar }) {
  const [pedidoAtual, setPedidoAtual] = useState(pedido);
  const [novoItem, setNovoItem] = useState({ nome_produto: '', quantidade: 1, unidade_medida: 'PC', preco_unitario: 0 });
  const [mostrarFormItem, setMostrarFormItem] = useState(false);
  
  // Novos estados para controle de edição e exclusão
  const [itemEmEdicao, setItemEmEdicao] = useState(null);
  
  const [mostrarFormCancelar, setMostrarFormCancelar] = useState(false);
  const [motivoCancelamento, setMotivoCancelamento] = useState('');
  const [erro, setErro] = useState('');

  const nomeCliente = clientes.find(c => c.id === pedidoAtual.cliente_id)?.razao_social || 'Carregando...';
  const nomeFornecedor = fornecedores.find(f => f.id === pedidoAtual.fornecedor_id)?.nome || 'Carregando...';

  const formatarMoeda = (valor) => {
    if (valor === undefined || valor === null) return 'US $ 0,00';
    const valorStr = valor.toString();
    if (valorStr.includes('.')) {
      const [inteiro, decimal] = valorStr.split('.');
      const decimalCortado = decimal.substring(0, 3);
      return `US $ ${inteiro},${decimalCortado}`;
    }
    return `US $ ${valorStr},00`;
  };

  const recarregarPedido = async () => {
    const resPedidos = await fetch('http://127.0.0.1:8000/pedidos');
    const data = await resPedidos.json();
    const pedidoAtualizado = data.find(p => p.id === pedidoAtual.id);
    setPedidoAtual(pedidoAtualizado);
  };

  const handleAdicionarItem = async (e) => {
    e.preventDefault();
    const res = await fetch(`http://127.0.0.1:8000/pedidos/${pedidoAtual.id}/itens`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(novoItem)
    });

    if (res.ok) {
      await recarregarPedido();
      setMostrarFormItem(false);
      setNovoItem({ nome_produto: '', quantidade: 1, unidade_medida: 'PC', preco_unitario: 0 });
    }
  };

  // NOVO: Função para salvar a edição da linha
  const handleSalvarEdicao = async (itemId) => {
    try {
      // AJUSTE A URL ABAIXO CONFORME SUA API (pode ser PATCH em vez de PUT)
      const res = await fetch(`http://127.0.0.1:8000/pedidos/${pedidoAtual.id}/itens/${itemId}`, {
        method: 'PUT', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          quantidade: itemEmEdicao.quantidade,
          unidade_medida: itemEmEdicao.unidade_medida,
          preco_unitario: itemEmEdicao.preco_unitario
        })
      });

      if (res.ok) {
        await recarregarPedido();
        setItemEmEdicao(null); // Fecha o modo de edição
      } else {
        alert("Erro ao editar o item.");
      }
    } catch (err) {
      alert("Erro de conexão.");
    }
  };

  // NOVO: Função para excluir o item diretamente
  const handleExcluirItem = async (itemId) => {
    try {
      // AJUSTE A URL ABAIXO CONFORME SUA API
      const res = await fetch(`http://127.0.0.1:8000/pedidos/${pedidoAtual.id}/itens/${itemId}`, {
        method: 'DELETE'
      });

      if (res.ok) {
        await recarregarPedido();
      } else {
        alert("Erro ao excluir o item.");
      }
    } catch (err) {
      alert("Erro de conexão.");
    }
  };

  const handleCancelarPedido = async (e) => {
    e.preventDefault();
    setErro('');
    
    if (!motivoCancelamento.trim()) {
      setErro("Por favor, escreva o motivo do cancelamento.");
      return;
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/pedidos/${pedidoAtual.id}/cancelar`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'x-usuario-id': "u1"
        },
        body: JSON.stringify({ motivo: motivoCancelamento })
      });

      if (res.ok) {
        await recarregarPedido();
        setMostrarFormCancelar(false);
        setMotivoCancelamento('');
      } else {
        const errorData = await res.json();
        setErro(errorData.detail || "Erro ao cancelar pedido.");
      }
    } catch (err) {
      setErro("Erro de conexão com o servidor.");
    }
  };

  const totalQtd = pedidoAtual.itens?.reduce((acc, item) => acc + item.quantidade, 0) || 0;
  const totalValor = pedidoAtual.itens?.reduce((acc, item) => acc + (item.valor_total || 0), 0) || 0;

  return (
    <div className="bg-[#1e2532] p-8 rounded-lg border border-gray-700 shadow-lg w-full max-w-7xl mx-auto h-[calc(100vh-120px)] overflow-y-auto custom-scrollbar">
      
      <button onClick={aoVoltar} className="text-white hover:text-gray-300 font-semibold text-left mb-6 flex items-center gap-2">
        <span>←</span> Voltar para a pasta
      </button>

      {/* CABEÇALHO */}
      <div className="flex justify-between items-start border-b border-gray-700 pb-6 mb-6">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-3xl font-bold text-white">{pedidoAtual.codigo}</h1>
            <span className="bg-green-600 text-white text-xs px-2 py-1 rounded font-bold uppercase">
              {pedidoAtual.status}
            </span>
          </div>
          <p className="text-gray-400 text-sm">18/11/2026 - Em andamento</p>
          <p className="text-gray-400 text-sm">Responsável: Giovanni</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-400">Etapa Atual:</p>
          <p className="text-lg font-bold text-white">{pedidoAtual.processo_atual.replace(/_/g, ' ').toUpperCase()}</p>
        </div>
      </div>

      {/* ÁREA SUPERIOR: INFORMAÇÕES (ESQUERDA) E DOCUMENTOS (DIREITA) */}
      <div className="flex flex-col xl:flex-row gap-8 mb-8">
        <div className="flex-1 space-y-6">
          <div>
            <h2 className="text-lg font-bold text-white mb-2">Cliente: {nomeCliente}</h2>
            <div className="text-sm text-gray-300 space-y-1">
              <p>CNPJ: 24.057.284/0001-10</p>
              <p>Endereço: Rua Caramuru 11 loja 2, Centro, Canoas, RS, Brasil</p>
              <p>CEP: 92.210-160</p>
              <p>Telefone: +55 (51) 9720-4636</p>
            </div>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">Fornecedor: {nomeFornecedor}</h2>
            <div className="text-sm text-gray-300 space-y-1">
              <p>Endereço: Dongguan, Guangdong, China</p>
              <p>Contato: Vivien</p>
              <p>Responsável: Giovanni</p>
            </div>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">Remarks</h2>
            <div className="text-sm text-gray-300 space-y-1">
              <p>HSCODE: {pedidoAtual.hscode || '719'}</p>
              <p>INCOTERM: {pedidoAtual.incoterm} {pedidoAtual.porto_carregamento?.split(',')[0]}</p>
              <p>Porto de Carregamento: {pedidoAtual.porto_carregamento}</p>
              <p>Porto de Destino: {pedidoAtual.porto_destino}</p>
              <p>País de Produção: P. R. China</p>
              <p>País de Aquisição: Hong Kong</p>
              <p>Prazo de Frete: {pedidoAtual.tempo_producao}</p>
              <p>Pagamentos: {pedidoAtual.pagamentos}</p>
            </div>
          </div>
        </div>

        <div className="w-full xl:w-[350px] flex-shrink-0">
          <div className="bg-[#161b22] p-6 rounded-lg border border-gray-700 flex flex-col min-h-[350px]">
            <h2 className="text-lg font-bold text-white text-center mb-8 uppercase tracking-widest">Documentos</h2>
            <div className="flex flex-col space-y-4 flex-1 pr-6 text-right">
              <a href="#" className="text-blue-400 hover:text-blue-300 underline underline-offset-4 text-sm transition-colors">{pedidoAtual.codigo} - PI</a>
              <a href="#" className="text-blue-400 hover:text-blue-300 underline underline-offset-4 text-sm transition-colors">{pedidoAtual.codigo} - CI</a>
              <a href="#" className="text-blue-400 hover:text-blue-300 underline underline-offset-4 text-sm transition-colors">{pedidoAtual.codigo} - PL</a>
              <a href="#" className="text-blue-400 hover:text-blue-300 underline underline-offset-4 text-sm transition-colors">Cotação</a>
            </div>
            <button className="mt-8 bg-blue-600 text-white w-full py-3 rounded hover:bg-blue-500 font-medium transition-colors">Adicionar Novos Documentos</button>
          </div>
        </div>
      </div>

      {/* ÁREA INFERIOR: TABELA E BOTÕES */}
      <div className="w-full">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold text-white">Produtos</h2>
          <button onClick={() => setMostrarFormItem(!mostrarFormItem)} className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-500 transition-colors">
            + Adicionar Produto
          </button>
        </div>

        {mostrarFormItem && (
          <form onSubmit={handleAdicionarItem} className="bg-gray-900 p-4 rounded border border-gray-700 mb-4 grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
            <div className="md:col-span-2"><label className="text-xs text-gray-400">Produto</label><input type="text" required className="w-full bg-gray-800 border border-gray-700 p-2 rounded text-white" onChange={e => setNovoItem({...novoItem, nome_produto: e.target.value})} /></div>
            <div><label className="text-xs text-gray-400">Qtd</label><input type="number" required className="w-full bg-gray-800 border border-gray-700 p-2 rounded text-white" onChange={e => setNovoItem({...novoItem, quantidade: Number(e.target.value)})} /></div>
            <div><label className="text-xs text-gray-400">U.M</label><input type="text" required placeholder="PC" className="w-full bg-gray-800 border border-gray-700 p-2 rounded text-white" onChange={e => setNovoItem({...novoItem, unidade_medida: e.target.value})} /></div>
            <div><label className="text-xs text-gray-400">Preço Unit.</label><input type="number" step="0.001" required className="w-full bg-gray-800 border border-gray-700 p-2 rounded text-white" onChange={e => setNovoItem({...novoItem, preco_unitario: Number(e.target.value)})} /></div>
            <button type="submit" className="col-span-1 md:col-span-5 bg-green-600 text-white py-2 rounded hover:bg-green-500 font-bold">Adicionar na Tabela</button>
          </form>
        )}

        <div className="bg-[#161b22] rounded-lg overflow-hidden border border-gray-700 w-full">
          <table className="w-full text-left text-gray-300">
            <thead className="bg-[#1a202c] text-gray-400 text-xs uppercase tracking-wider border-b border-gray-700">
              <tr>
                <th className="p-4 font-semibold">Nome</th>
                <th className="p-4 font-semibold">Qtd</th>
                <th className="p-4 font-semibold">U.M</th>
                <th className="p-4 font-semibold">Preço Unit.</th>
                {/* Nova coluna de ações adicionada aqui */}
                <th className="p-4 font-semibold text-center w-24">Ações</th>
                <th className="p-4 font-semibold text-right">Total</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {pedidoAtual.itens?.length === 0 ? (
                <tr><td colSpan="6" className="p-8 text-center text-gray-500">Nenhum produto adicionado ainda.</td></tr>
              ) : (
                pedidoAtual.itens?.map(item => (
                  <tr key={item.id} className="border-b border-gray-800 last:border-0 hover:bg-gray-800/30 transition-colors">
                    <td className="p-4">{item.nome_produto}</td>
                    
                    {/* Renderização condicional: se estiver em edição mostra inputs, senão mostra texto */}
                    {itemEmEdicao?.id === item.id ? (
                      <>
                        <td className="p-2">
                          <input type="number" className="w-20 bg-gray-800 border border-gray-600 p-1 rounded text-white" value={itemEmEdicao.quantidade} onChange={(e) => setItemEmEdicao({...itemEmEdicao, quantidade: Number(e.target.value)})} />
                        </td>
                        <td className="p-2">
                          <input type="text" className="w-16 bg-gray-800 border border-gray-600 p-1 rounded text-white" value={itemEmEdicao.unidade_medida} onChange={(e) => setItemEmEdicao({...itemEmEdicao, unidade_medida: e.target.value})} />
                        </td>
                        <td className="p-2">
                          <input type="number" step="0.001" className="w-24 bg-gray-800 border border-gray-600 p-1 rounded text-white" value={itemEmEdicao.preco_unitario} onChange={(e) => setItemEmEdicao({...itemEmEdicao, preco_unitario: Number(e.target.value)})} />
                        </td>
                        <td className="p-2 text-center flex gap-2 justify-center">
                          <button onClick={() => handleSalvarEdicao(item.id)} className="text-green-500 hover:text-green-400 font-bold text-lg" title="Salvar">✓</button>
                          <button onClick={() => setItemEmEdicao(null)} className="text-gray-400 hover:text-gray-300 font-bold text-lg" title="Cancelar">✕</button>
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="p-4">{item.quantidade}</td>
                        <td className="p-4">{item.unidade_medida}</td>
                        <td className="p-4">{formatarMoeda(item.preco_unitario)}</td>
                        
                        {/* Botões de Lápis e X quando não está em edição */}
                        <td className="p-2 text-center flex gap-3 justify-center">
                          <button onClick={() => setItemEmEdicao(item)} className="text-blue-400 hover:text-blue-300" title="Editar item">
                            ✏️
                          </button>
                          <button onClick={() => handleExcluirItem(item.id)} className="text-red-500 hover:text-red-400 text-lg font-bold" title="Excluir item">
                            ✕
                          </button>
                        </td>
                      </>
                    )}

                    <td className="p-4 text-right">{formatarMoeda(item.valor_total)}</td>
                  </tr>
                ))
              )}
            </tbody>
            {pedidoAtual.itens?.length > 0 && (
              <tfoot className="bg-[#1a202c] border-t border-gray-700 font-bold text-white">
                <tr>
                  <td className="p-4">Total</td>
                  <td className="p-4">{totalQtd}</td>
                  <td className="p-4"></td>
                  <td className="p-4"></td>
                  <td className="p-4"></td>
                  <td className="p-4 text-right">{formatarMoeda(totalValor)}</td>
                </tr>
              </tfoot>
            )}
          </table>
        </div>

        {erro && <p className="text-red-400 bg-red-900/30 p-3 rounded text-sm mt-4">{erro}</p>}

        {mostrarFormCancelar && (
          <form onSubmit={handleCancelarPedido} className="bg-gray-900 p-4 rounded border border-gray-700 mt-6 flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1 w-full">
              <label className="text-sm text-gray-400 block mb-1">Motivo do Cancelamento (Obrigatório):</label>
              <input type="text" value={motivoCancelamento} onChange={e => setMotivoCancelamento(e.target.value)} className="w-full bg-gray-800 border border-gray-700 p-2 rounded text-white" required />
            </div>
            <button type="submit" className="bg-red-600 text-white px-6 py-2 rounded hover:bg-red-500 font-bold w-full md:w-auto">Confirmar</button>
          </form>
        )}

        <div className="flex flex-wrap justify-end gap-3 mt-8">
          <button className="bg-[#b47e1a] text-white px-6 py-2.5 rounded font-medium hover:bg-yellow-600 transition-colors">Adicionar Packing</button>
          <button className="bg-[#22c55e] text-white px-6 py-2.5 rounded font-medium hover:bg-green-500 transition-colors">Avançar Etapa</button>
          <button className="bg-[#2563eb] text-white px-6 py-2.5 rounded font-medium hover:bg-blue-500 transition-colors">Editar Pedido</button>
          <button onClick={() => setMostrarFormCancelar(!mostrarFormCancelar)} className="bg-[#991b1b] text-white px-6 py-2.5 rounded font-medium hover:bg-red-800 transition-colors border border-red-900">Cancelar Pedido</button>
        </div>
      </div>
    </div>
  );
}