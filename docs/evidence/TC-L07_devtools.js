const i=[...document.querySelectorAll('article.card')].find(a=>a.querySelector('h3').textContent==='Double Cheese').querySelector('input.qty'); i.removeAttribute('max'); i.value='500';
