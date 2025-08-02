
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Apenas o método POST é permitido.' });
  }

  try {
    // --- INÍCIO DO CÓDIGO DE DIAGNÓSTICO ---
    console.log("--- INICIANDO DEBUG DA REQUISIÇÃO ---");
    console.log("Método Recebido:", req.method);
    console.log("Cabeçalho Content-Type Recebido:", req.headers['content-type']); // LINHA MAIS IMPORTANTE
    console.log("API Key está carregada?", process.env.API_KEY ? 'Sim' : 'NÃO, FALHOU!');
    console.log("URL da API de destino:", 'https://movimento-transporte-ja-production.up.railway.app/relatos');
    console.log("-----------------------------------------");
    // --- FIM DO CÓDIGO DE DIAGNÓSTICO ---


    const apiKey = process.env.API_KEY;
    const apiUrl = 'https://movimento-transporte-ja-production.up.railway.app/relatos'; // É melhor usar a variável de ambiente

    if (!apiKey || !apiUrl) {
      // Este erro será pego pelo catch abaixo
      throw new Error('Variáveis de ambiente API_KEY ou RAILWAY_API_URL não configuradas no servidor.');
    }

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        // A FORMA CORRETA: Repassando o cabeçalho original com o boundary
        'Content-Type': req.headers['content-type'],
        'token': apiKey,
      },
      body: req,
      duplex: 'half',
    });


    const data = await response.json();

    if (!response.ok) {
      console.error("Erro recebido da API do Railway:", data);
      return res.status(response.status).json(data);
    }
    
    return res.status(200).json(data);

  } catch (error) {
    console.error('ERRO CRÍTICO no proxy da API:', error);
    return res.status(500).json({ message: 'Erro interno no servidor.', details: error.message });
  }

}

export const config = {
  api: {
    bodyParser: false,
  },
}