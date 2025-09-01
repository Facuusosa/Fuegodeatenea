document.addEventListener('DOMContentLoaded', function(){
  const lb = document.getElementById('lightbox');
  const lbImg = document.getElementById('lightbox-img');
  const btnClose = document.getElementById('lightbox-close');

  function openLightbox(src){
    if(!lb || !lbImg) return;
    lbImg.src = src;
    lb.classList.add('is-open');
    lb.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox(){
    if(!lb || !lbImg) return;
    lb.classList.remove('is-open');
    lb.setAttribute('aria-hidden', 'true');
    lbImg.removeAttribute('src');
    document.body.style.overflow = '';
  }

  document.addEventListener('click', function(e){
    const trigger = e.target.closest('[data-zoom-src], .zoomable');
    if(trigger){
      const src = trigger.getAttribute('data-zoom-src') || trigger.getAttribute('src');
      if(src) openLightbox(src);
    }
  });

  if(btnClose) btnClose.addEventListener('click', closeLightbox);
  if(lb) lb.addEventListener('click', function(e){ if(e.target === lb) closeLightbox(); });
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') closeLightbox(); });
});
