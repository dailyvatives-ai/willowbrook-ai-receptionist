function wireChat(bodyId, inputId, buttonId) {
  const body = document.getElementById(bodyId);
  const input = document.getElementById(inputId);
  const button = document.getElementById(buttonId);
  if (!body || !input || !button) return;

  let sessionId = null;

  function addBubble(text, who) {
    const b = document.createElement('div');
    b.className = 'bubble ' + (who === 'user' ? 'bubble-out' : 'bubble-in');
    b.textContent = text;
    body.appendChild(b);
    body.scrollTop = body.scrollHeight;
    return b;
  }

  function addTyping() {
    const b = document.createElement('div');
    b.className = 'bubble-typing';
    b.innerHTML = '<span></span><span></span><span></span>';
    body.appendChild(b);
    body.scrollTop = body.scrollHeight;
    return b;
  }

  async function send() {
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    addBubble(text, 'user');
    const typingEl = addTyping();
    button.disabled = true;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: text }),
      });
      const data = await res.json();
      typingEl.remove();

      if (!res.ok) {
        addBubble("Sorry, something went wrong on my end. Please try again in a moment.", 'ai');
        return;
      }

      sessionId = data.session_id;
      addBubble(data.reply, 'ai');
    } catch (err) {
      typingEl.remove();
      addBubble("I couldn't reach the server just now — please try again.", 'ai');
    } finally {
      button.disabled = false;
    }
  }

  button.addEventListener('click', send);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') send();
  });
}

wireChat('chatBody', 'chatInput', 'sendBtn');
wireChat('chatBody2', 'chatInput2', 'sendBtn2');
