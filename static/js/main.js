/**
 * main.js — Base UI interactions for SocialApp
 */

// ── Flash message auto-dismiss ──────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.flash-message').forEach(msg => {
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transform = 'translateX(20px)';
      msg.style.transition = 'all 0.3s ease';
      setTimeout(() => msg.remove(), 300);
    }, 4000);
  });

  // ── Post dropdown menus ──
  document.querySelectorAll('.post-menu-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const menuId = btn.dataset.menu;
      const dropdown = document.getElementById(`menu-${menuId}`);
      if (dropdown) dropdown.classList.toggle('hidden');
    });
  });

  // Close dropdowns when clicking outside
  document.addEventListener('click', () => {
    document.querySelectorAll('.post-dropdown').forEach(d => d.classList.add('hidden'));
  });
});
