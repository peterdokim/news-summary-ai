export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { jobId } = req.query;
  if (!jobId) {
    return res.status(400).json({ error: 'jobId is required' });
  }

  try {
    const pythonApiUrl = process.env.PYTHON_API_URL || (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5000');
    const response = await fetch(`${pythonApiUrl}/api/progress/${jobId}`);
    const data = await response.json();
    return res.status(response.status).json(data);
  } catch (error) {
    return res.status(500).json({ error: 'Failed to get progress', details: error.message });
  }
}
