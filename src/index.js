/**
 * Cloudflare Worker для Telegram бота Codev
 * Работает через webhook
 */

export default {
  async fetch(request, env) {
    // Проверяем метод запроса
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      // Получаем update от Telegram
      const update = await request.json();
      
      // Здесь будет обработка update
      console.log('Received update:', update);
      
      // Пока просто возвращаем OK
      return new Response('OK', { status: 200 });
      
    } catch (error) {
      console.error('Error processing update:', error);
      return new Response('Internal Server Error', { status: 500 });
    }
  }
};
