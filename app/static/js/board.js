// Drag and drop between pipeline columns. The server stays the source of truth:
// a move is only kept if the API accepts it, otherwise the card goes back.
(() => {
  const board = document.getElementById('board');
  const msg = document.getElementById('msg');
  let dragged = null;
  let origin = null;

  const say = (text, bad = false) => { msg.textContent = text; msg.classList.toggle('bad', bad); };
  const updateCounts = () => board.querySelectorAll('.col').forEach(col => {
    col.querySelector('.count').textContent = col.querySelectorAll('.cand').length;
  });

  board.addEventListener('dragstart', e => {
    const card = e.target.closest('.cand');
    if (!card) return;
    dragged = card;
    origin = card.parentElement;
    card.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', card.dataset.id);
  });
  board.addEventListener('dragend', () => {
    if (dragged) dragged.classList.remove('dragging');
    board.querySelectorAll('.col').forEach(c => c.classList.remove('over'));
  });
  board.addEventListener('dragover', e => {
    const col = e.target.closest('.col');
    if (!col) return;
    e.preventDefault();
    board.querySelectorAll('.col').forEach(c => c.classList.toggle('over', c === col));
  });
  board.addEventListener('drop', async e => {
    const col = e.target.closest('.col');
    if (!col || !dragged) return;
    e.preventDefault();
    const drop = col.querySelector('.drop');
    if (drop === origin) return;
    drop.prepend(dragged);
    updateCounts();
    try {
      const res = await fetch(`/api/candidates/${dragged.dataset.id}/stage`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stage: col.dataset.stage }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Déplacement refusé');
      say('Candidat déplacé.');
    } catch (err) {
      origin.prepend(dragged);
      updateCounts();
      say(err.message, true);
    }
  });
})();
