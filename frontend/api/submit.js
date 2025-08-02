
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Apenas o método POST é permitido.' });
  }

  try {
    const apiKey = process.env.API_KEY;
    const apiUrl = 'https://movimento-transporte-ja-production.up.railway.app/relatos/';

    if (!apiKey || !apiUrl) {
      throw new Error('Variáveis de ambiente não configuradas no servidor.');
    }

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': req.headers['content-type'],
        'token': apiKey,
      },
      body: req,
    });


    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json(data);
    }
    
    return res.status(200).json(data);

  } catch (error) {
    console.error('Erro no proxy da API:', error);
    return res.status(500).json({ message: 'Erro interno no servidor.' });
  }
}