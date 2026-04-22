/**
 * TweetSentinel — Main JS
 * Handles form loading state & UX micro-interactions
 */

(function () {
  'use strict';

  /* ── Set today as default "to" date, yesterday as "from" ──── */
  const todayInput    = document.getElementById('todate');
  const fromInput     = document.getElementById('fromdate');

  if (todayInput && fromInput) {
    const today     = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 7);

    todayInput.value = formatDate(today);
    fromInput.value  = formatDate(yesterday);

    /* Prevent "to" being before "from" */
    fromInput.addEventListener('change', () => {
      if (todayInput.value && todayInput.value < fromInput.value) {
        todayInput.value = fromInput.value;
      }
    });

    todayInput.addEventListener('change', () => {
      if (fromInput.value && fromInput.value > todayInput.value) {
        fromInput.value = todayInput.value;
      }
    });
  }

  /* ── Form loading state ──────────────────────────────────── */
  const form      = document.getElementById('search-form');
  const submitBtn = document.getElementById('submit-btn');
  const btnText   = submitBtn ? submitBtn.querySelector('.btn-text')   : null;
  const btnArrow  = submitBtn ? submitBtn.querySelector('.btn-arrow')  : null;
  const spinner   = document.getElementById('btn-spinner');

  if (form && submitBtn) {
    form.addEventListener('submit', function (e) {
      /* Basic date validation */
      const from = fromInput ? fromInput.value : '';
      const to   = todayInput ? todayInput.value : '';

      if (from && to && from > to) {
        e.preventDefault();
        shakeField(fromInput);
        return;
      }

      /* Show loading state */
      submitBtn.disabled = true;
      if (btnText)  btnText.classList.add('hidden');
      if (btnArrow) btnArrow.style.display = 'none';
      if (spinner)  spinner.classList.add('active');
      submitBtn.style.pointerEvents = 'none';
    });
  }

  /* ── Input focus shimmer effect ─────────────────────────── */
  document.querySelectorAll('input').forEach(function (inp) {
    inp.addEventListener('focus', function () {
      this.closest('.form-field')?.classList.add('focused');
    });
    inp.addEventListener('blur', function () {
      this.closest('.form-field')?.classList.remove('focused');
    });
  });

  /* ── Hashtag input auto-strip the # ─────────────────────── */
  const tweetInput = document.getElementById('tweet-input');
  if (tweetInput) {
    tweetInput.addEventListener('input', function () {
      if (this.value.startsWith('#')) {
        this.value = this.value.slice(1);
      }
    });
  }

  /* ── Result page: keyboard shortcut (Esc → back) ──────── */
  const backBtn = document.getElementById('back-btn');
  if (backBtn) {
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') backBtn.click();
    });
  }

  /* ── Helpers ────────────────────────────────────────────── */
  function formatDate(d) {
    const y  = d.getFullYear();
    const m  = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${dd}`;
  }

  function shakeField(el) {
    if (!el) return;
    el.style.animation = 'none';
    el.offsetHeight; /* reflow */
    el.style.animation = 'shake 0.4s ease';
    el.addEventListener('animationend', () => {
      el.style.animation = '';
    }, { once: true });
  }

  /* Inject shake keyframe if not in CSS */
  if (!document.getElementById('ts-shake-style')) {
    const style = document.createElement('style');
    style.id = 'ts-shake-style';
    style.textContent = `
      @keyframes shake {
        0%,100% { transform: translateX(0); }
        20%      { transform: translateX(-6px); }
        40%      { transform: translateX(6px); }
        60%      { transform: translateX(-4px); }
        80%      { transform: translateX(4px); }
      }
    `;
    document.head.appendChild(style);
  }

})();
