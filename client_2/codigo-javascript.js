import { redirecionarBotaoHeader, redirecionarSubHeaderBotoes, criarSubHeaderHTML } from './header.js';
import { adicionarEventoBotaoMenuMobile, adicionarEventoBotoesOpcoesMobile, criarMenuMobileHTML } from './menu-mobile.js';
import { filtrarTabela, adicionarEventoIconeOrdemFiltro } from './filtro.js';
import { adicionarEventoBotaoDescricao, fecharDescricao } from './botao-descricao.js';

// FUNÇÕES //

// Função para pegar todos os pedidos e criar a tabela
async function fetchPedidos(categoria = null, ordem= null) {

  let url = '/pedidos';
  // Adiciona os campos de categoria e ordem ao fetch caso seja requisitado pelo filtro
  if(categoria && ordem) {
    url += `?categoria=${categoria}&ordem=${ordem}`;
  }
  console.log(url)

  const resposta =  await fetch(url);
  const pedidos = await resposta.json();
  const tabelaPedidos = document.getElementById('tabela-pedidos');

  tabelaPedidos.innerHTML = '';

  pedidos.forEach(pedido => {
    const row = document.createElement('tr');
    row.classList.add('tabela-pedido');

    row.innerHTML = `
      <td data-label="Id">${pedido.id}</td>
      <td data-label="Item">${pedido.item}</td>
      <td data-label="Cliente">${pedido.cliente}</td>
      <td data-label="Telefone">${pedido.telefone}</td>
      <td data-label="Dia Recebido">${new Date(pedido.dia_recebido).toLocaleDateString('pt-BR')}</td>
      <td data-label="Valor">${pedido.valor.toFixed(2)}</td>
      <td data-label="Ações">
        <button class="btn btn-outline-dark botao-descricao" title="Descrição" data-descricao="${pedido.descricao}"><i class="fa-solid fa-list"></i></button>
        <button class="btn btn-outline-danger botao-deletar" title="Deletar" data-id="${pedido.id}"><i class="fa-solid fa-trash"></i></button>
        <button class="btn btn-outline-primary botao-editar" title="Editar" data-id="${pedido.id}"><i class="fa-solid fa-pencil"></i></button>
        <button class="btn btn-outline-success botao-finalizar" title="Finalizar" data-id="${pedido.id}"><i class="fa-solid fa-check"></i></button>
      </td>
    `;

    tabelaPedidos.appendChild(row);
  });

  adicionarEventoBotaoDescricao(); // Depois de atualizar a tabela adiciona a função de descrição
  adicionarEventoBotaoDeletar();   // Depois de atualizar a tabela adiciona a função de deletar
  adicionarEventoBotaoEditar();    // Depois de atualizar a tabela adiciona a função de editar
  adicionarEventoBotaoFinalizar(); // Depois de atualizar a tabela adiciona a função de finalizar
}


// Ordena a tabela de acordo com os parâmetros
async function ordenarTabela(){
  document.querySelector('.filtro-ordem').addEventListener('submit', async (event) => {
    event.preventDefault();

    const categoria = document.getElementById('categoria').value;
    const ordem = document.getElementById('ordem').getAttribute('data-ordem');

    // Busca a tabela de acordo com os parâmetros
    fetchPedidos(categoria, ordem);
  });
}


// Função para deletar um pedido da tabela
async function deletarPedido(id) {
  await fetch(`/pedidos/${id}`, { method: 'DELETE' });
  fetchPedidos();
}


// Adiciona a função de deletar o pedido ao clicar o botão
function adicionarEventoBotaoDeletar() {
  const botoesDeletar = document.querySelectorAll('.botao-deletar');

  botoesDeletar.forEach((button) => {
    button.addEventListener('click', async () => {
      const id = button.getAttribute('data-id');
      await deletarPedido(id);
    });
  });
}


// Adiciona a função de editar o pedido
function adicionarEventoBotaoEditar() {
  const botoesEditar = document.querySelectorAll('.botao-editar');

  botoesEditar.forEach((button) => {
    button.addEventListener('click', async () => {
      const id = button.getAttribute('data-id');
      
      // Redireciona a página de editar o pedido daquele id
      window.location.href = `/editar-pedido?id=${id}`;
    });
  });
}


// Adiciona a função de finalizar o pedido
async function finalizarPedido(id) {
  // Primeiro cria o pedido
  const resposta = await fetch(`/pedidos/${id}`);
  const pedido = await resposta.json();

  // Calcula o dia finalizado
  const diaFinalizado = new Date().toISOString().slice(0, 10);
  // Transformar no mesmo formato de data (Por algum motivo da este bug)
  pedido.dia_recebido = new Date(pedido.dia_recebido).toISOString().slice(0, 10);

  // Calcula a diferença de dias entre dia_finalizado e dia_recebido
  const diaRecebido = new Date(pedido.dia_recebido);
  const diaFinal = new Date(diaFinalizado);
  const diffTime = Math.abs(diaFinal - diaRecebido);
  const diasTotais = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  console.log('dia: ', pedido.dia_recebido);

  // Cria um novo objeto com os campos necessários para a tabela 'concluidos'
  const pedidoConcluido = {
    ...pedido,
    dia_finalizado: diaFinalizado,
    dias_totais: diasTotais
  };

  console.log(pedidoConcluido);

  // Adiciona o pedido a concluidos
  const respostaConclusao = await fetch('/concluidos', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(pedidoConcluido)
  });

  // Depois deleta o pedido de pedidos
  if (respostaConclusao.ok) {
    // Deleta o pedido de 'pedidos'
    await fetch(`/pedidos/${id}`, { method: 'DELETE' });
    fetchPedidos();
  } else {
    console.error('Erro ao mover pedido para concluidos');
  }
}


// Adiciona a função de deletar o pedido ao clicar o botão
function adicionarEventoBotaoFinalizar() {
  const botoesFinalizar = document.querySelectorAll('.botao-finalizar');

  botoesFinalizar.forEach((button) => {
    button.addEventListener('click', async () => {
      const id = button.getAttribute('data-id');
      await finalizarPedido(id);
    });
  });
}

///////////////////////////////////////////////////////////////////////////


// SCRIPT DA PÁGINA //


document.addEventListener('DOMContentLoaded', () => {
  criarSubHeaderHTML();
  criarMenuMobileHTML();
  redirecionarBotaoHeader();
  redirecionarSubHeaderBotoes();
  adicionarEventoBotaoMenuMobile();
  adicionarEventoBotoesOpcoesMobile();
  adicionarEventoIconeOrdemFiltro();
  fecharDescricao();
  ordenarTabela();
  filtrarTabela();
  fetchPedidos();
});