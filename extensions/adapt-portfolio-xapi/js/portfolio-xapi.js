import Adapt from 'core/js/adapt';

// Only the loopback operational-test gateway exposes this route.
// No LRS credentials are shipped in the course package.
const session = fetch('/api/session', { method: 'POST' }).then(async response => {
  if (!response.ok) throw new Error('Tracking session unavailable');
  return response.json();
});
session.catch(() => {});
async function record(verb, activity) {
  const id = crypto.randomUUID();
  try {
    const { token } = await session;
    const response = await fetch('/api/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Session-Token': token },
      body: JSON.stringify({ id, verb, activity })
    });
    if (!response.ok) throw new Error(`Tracking rejected: ${response.status}`);
    window.dispatchEvent(new CustomEvent('portfolio:recorded', { detail: { id, verb, activity } }));
  } catch (error) {
    console.warn('Portfolio tracking unavailable. Completion has not been confirmed by the LRS.', error.message);
  }
}
Adapt.once('app:dataReady', () => {
  record('initialized', 'course');
  Adapt.course.on('change:_isComplete', model => {
    if (model.get('_isComplete')) record('completed', 'course');
  });
});
Adapt.on('pageView:ready', view => record('experienced', view.model.get('_id')));
