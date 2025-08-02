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

    // --- Monto o Pacote de Dados para Envio (FormData) ---
    // Se todas as validações passaram, chegamos aqui.
    console.log('Validação bem-sucedida! Preparando para enviar...');
    
    const formData = new FormData();
    formData.append('nome', nome);
    formData.append('contato', contato);
    formData.append('relato_texto', relato);
    formData.append('instituicao', instituicao);
    formData.append('data_ocorrido', dataOcorrido);
    
    for (const anexo of anexos) {
        formData.append('anexos', anexo);
    }
    
    // --- Envio os Dados para a API ---
    const apiUrl = '/api/submit';

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            body: formData
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