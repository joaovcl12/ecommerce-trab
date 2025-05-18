let carrinho = JSON.parse(localStorage.getItem("carrinho") || "[]");

function salvarCarrinho() {
    localStorage.setItem("carrinho", JSON.stringify(carrinho));
}

function adicionarCarrinho(id, nome, preco) {
    const item = carrinho.find(p => p.produto_id === id);
    if (item) {
        item.quantidade += 1;
    } else {
        carrinho.push({ produto_id: id, nome, preco, quantidade: 1 });
    }
    salvarCarrinho();
    alert("Produto adicionado ao carrinho!");
}

// Função para alterar a quantidade no carrinho (usada pelos botões + e −)
function alterarQuantidade(produto_id, delta) {
    const item = carrinho.find(p => p.produto_id === produto_id);
    if (item) {
        item.quantidade += delta;
        if (item.quantidade <= 0) {
            carrinho = carrinho.filter(p => p.produto_id !== produto_id);
        }
        salvarCarrinho();
        if (typeof renderCarrinho === "function") {
            renderCarrinho(); // Atualiza a interface, se disponível
        }
    }
}

// Evento para botões que usam data-*
document.addEventListener("DOMContentLoaded", () => {
    const botoes = document.querySelectorAll(".adicionar-btn");
    botoes.forEach(btn => {
        btn.addEventListener("click", () => {
            const id = parseInt(btn.getAttribute("data-id"));
            const nome = btn.getAttribute("data-nome");
            const preco = parseFloat(btn.getAttribute("data-preco"));
            adicionarCarrinho(id, nome, preco);
        });
    });
});

// Tornar as funções acessíveis globalmente para uso inline
window.adicionarCarrinho = adicionarCarrinho;
window.alterarQuantidade = alterarQuantidade;
