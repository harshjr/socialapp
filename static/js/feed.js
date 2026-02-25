/**
 * feed.js — Feed-specific JS: like toggle, follow, image preview, char counter
 * All API calls use Django's CSRF token for security.
 */

// ── CSRF helper ─────────────────────────────────────────────
function getCsrfToken() {
  return document.cookie.split(';')
    .find(c => c.trim().startsWith('csrftoken='))
    ?.split('=')[1] || '';
}

// ── LIKE TOGGLE ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const url = btn.dataset.url;
      if (!url) return;

      try {
        const resp = await fetch(url, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
          }
        });
        const data = await resp.json();

        // Update UI
        const countEl = btn.querySelector('.like-count');
        if (countEl) countEl.textContent = data.count;

        const heartPath = btn.querySelector('path');
        if (data.liked) {
          btn.classList.add('liked');
          if (heartPath) heartPath.setAttribute('fill', 'currentColor');
          btn.animate([
            { transform: 'scale(1)' },
            { transform: 'scale(1.3)' },
            { transform: 'scale(1)' }
          ], { duration: 300, easing: 'ease-out' });
        } else {
          btn.classList.remove('liked');
          if (heartPath) heartPath.setAttribute('fill', 'none');
        }
      } catch (err) {
        console.error('Like failed:', err);
      }
    });
  });

  // ── FOLLOW TOGGLE ──────────────────────────────────────────
  document.querySelectorAll('.follow-toggle-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const url = btn.dataset.url;
      if (!url) return;

      try {
        const resp = await fetch(url, {
          method: 'POST',
          headers: { 'X-CSRFToken': getCsrfToken() }
        });
        const data = await resp.json();
        if (data.error) return;

        btn.textContent = data.following ? 'Following' : 'Follow';
        btn.classList.toggle('btn-primary', !data.following);
        btn.classList.toggle('btn-outline', data.following);

        // Update follower count on profile page if present
        const followerEl = document.getElementById('follower-count');
        if (followerEl) followerEl.textContent = data.follower_count;
      } catch (err) {
        console.error('Follow failed:', err);
      }
    });
  });

  // ── IMAGE PREVIEW ──────────────────────────────────────────
  const imageInput = document.getElementById('post-image');
  const previewWrap = document.getElementById('image-preview-wrap');
  const preview = document.getElementById('image-preview');
  const removeBtn = document.getElementById('remove-image');

  if (imageInput) {
    imageInput.addEventListener('change', () => {
      const file = imageInput.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          preview.src = e.target.result;
          previewWrap.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
      }
    });
  }

  if (removeBtn) {
    removeBtn.addEventListener('click', () => {
      imageInput.value = '';
      preview.src = '';
      previewWrap.classList.add('hidden');
    });
  }

  // ── CHARACTER COUNTER ──────────────────────────────────────
  const textarea = document.getElementById('post-content');
  const counter = document.getElementById('char-count');
  const MAX = 280;

  if (textarea && counter) {
    textarea.addEventListener('input', () => {
      const remaining = MAX - textarea.value.length;
      counter.textContent = remaining;
      counter.classList.toggle('warning', remaining < 20);
    });
  }
});
