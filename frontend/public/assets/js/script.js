
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

const formulario = document.getElementById('form-principal');
const errorMessageDiv = document.getElementById('error-message');

formulario.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorMessageDiv.textContent = '';

    // --- Constantes de Validação ---
    const MAX_FILES = 3;
    const MAX_SIZE_MB = 5;
    const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024; // Converte MB para Bytes

    // --- Coleto Dados do Formulário ---
    const nome = document.getElementById('nome').value;
    const contato = document.getElementById('contato').value;
    const relato = document.getElementById('relato').value;
    const instituicao = document.getElementById('instituicao').value;
    const anexoInput = document.getElementById('anexos');
    const dataOcorrido = document.getElementById('data_ocorrido').value;
    const anexos = anexoInput.files;

    // --- Executo as Validações ---

    // Regra 1: Limite de até 3 arquivos
    if (anexos.length > MAX_FILES) {
        errorMessageDiv.textContent = `Erro: Você só pode enviar no máximo ${MAX_FILES} arquivos.`;
        return;
    }

    // Loop para validar cada arquivo individualmente
    for (const anexo of anexos) {
        // Regra 2: Apenas imagens
        if (!anexo.type.startsWith('image/')) {
            errorMessageDiv.textContent = `Erro: O arquivo "${anexo.name}" não é uma imagem. Apenas imagens são permitidas.`;
            return;
        }

        // Regra 3: Limitação de tamanho
        if (anexo.size > MAX_SIZE_BYTES) {
            errorMessageDiv.textContent = `Erro: A imagem "${anexo.name}" é muito grande (${(anexo.size / 1024 / 1024).toFixed(2)}MB). O tamanho máximo é de ${MAX_SIZE_MB}MB.`;
            return;
        }
    }


    // --- CONVERTER ARQUIVOS PARA BASE64 ---
    console.log('Convertendo arquivos para Base64...');
    const anexosEmBase64 = [];
    for (const anexo of anexos) {
        try {
            const base64String = await fileToBase64(anexo);
            anexosEmBase64.push({
                filename: anexo.name,
                mimetype: anexo.type,
                dados_base64: base64String
            });
        } catch (error) {
            console.error('Erro ao converter arquivo:', error);
            errorMessageDiv.textContent = 'Ocorreu um erro ao processar os anexos.';
            return;
        }
    }

    const payload = {
        nome: nome,
        contato: contato,
        relato_texto: relato,
        instituicao: instituicao,
        data_ocorrido: dataOcorrido,
        anexos: anexosEmBase64
    };

    console.log('Enviando payload JSON para a API...');
    const apiUrl = 'https://movimento-transporte-ja-production.up.railway.app/relatos';
    const apiKey = 'x+!1/M*Q#81$b:%A?';

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'token': apiKey,
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erro ${response.status}`);
        }

        const result = await response.json();
        console.log('Sucesso:', result);
        alert('Relato enviado com sucesso! Obrigado por sua contribuição.');
        formulario.reset();

    } catch (error) {
        console.error('Erro ao enviar o formulário:', error);
        errorMessageDiv.textContent = `Erro ao enviar: ${error.message}`;
    }
});

// --- CÓDIGO PARA CARREGAR E EXIBIR OS RELATOS RECENTES ---

document.addEventListener('DOMContentLoaded', () => {
    carregarRelatosRecentes();
});


async function carregarRelatosRecentes() {
    const secaoRecenviadas = document.getElementById('recenviadas');
    
    // --- Definições da API ---
    const endpointRelatos = 'https://movimento-transporte-ja-production.up.railway.app/relatos/newest';
    const apiKey = 'x+!1/M*Q#81$b:%A?';

    try {
        // 1. Busca a lista de relatos (que agora já inclui os dados das imagens)
        const response = await fetch(endpointRelatos, {
            headers: {
                'token': apiKey
            }
        });

        if (!response.ok) {
            throw new Error('Não foi possível carregar os relatos.');
        }

        const relatos = await response.json();

        if (relatos.length === 0) {
            secaoRecenviadas.innerHTML += '<p>Ainda não há relatos para exibir.</p>';
            return;
        }

        // 2. Percorre cada relato para criar seu card no HTML
        for (const relato of relatos) {
            const card = document.createElement('div');
            card.className = 'card-rec';

            const titulo = document.createElement('h3');
            const dataFormatada = relato.data_ocorrido.split('-').reverse().join('/');
            titulo.textContent = `Ocorrido em: ${dataFormatada}`;
            
            const textoRelato = document.createElement('p');
            textoRelato.textContent = relato.relato_texto;
            
            card.appendChild(titulo);
            card.appendChild(textoRelato);

            // 3. Se houver anexos, cria as imagens DIRETAMENTE do Base64
            if (relato.anexos && relato.anexos.length > 0) {
                const anexosContainer = document.createElement('div');
                anexosContainer.className = 'anexos-container';

                for (const anexo of relato.anexos) {
                    const img = document.createElement('img');
                    img.src = anexo.dados_base64;
                    
                    img.alt = anexo.filename;
                    anexosContainer.appendChild(img);
                }
                card.appendChild(anexosContainer);
            }

            // 4. Adiciona o card completo à seção na página
            secaoRecenviadas.appendChild(card);
        }

    } catch (error) {
        console.error('Erro ao carregar relatos:', error);
        secaoRecenviadas.innerHTML += `<p style="color: red;">${error.message}</p>`;
    }
}