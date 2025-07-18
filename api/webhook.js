export const config = {
  runtime: 'edge',
};

export default async function handler(request) {
  // Always return 200 for webhook
  if (request.method === 'POST' && new URL(request.url).pathname === '/webhook') {
    return new Response('OK', {
      status: 200,
      headers: {
        'Content-Type': 'text/plain',
      },
    });
  }
  
  return new Response('Method not allowed', { status: 405 });
}
