document.addEventListener('DOMContentLoaded', function() {
    
    const kartData = JSON.parse(document.getElementById('kart-data').textContent);
    let currentIndex = 0;
    let isFlipped = false;
    
    const flashcard = document.querySelector('.flashcard');
    
    function updateCard(index) {
        const kart = kartData[index];
        
        document.getElementById('on-yazi').textContent = kart.on_yazi;
        document.getElementById('arka-yazi').textContent = kart.arka_yazi;
        document.getElementById('cumle-text').textContent = kart.cumle || '';
        
        const favoriLink = document.getElementById('favori-link');
        if (favoriLink) {
            favoriLink.href = `/fav_ekle/${kart.id}`;
            favoriLink.innerHTML = kart.fav == 1 ? 'Favori Kaldır' : 'Favori Ekle';
        }
        
        document.getElementById('geribtn').disabled = index === 0;
        document.getElementById('ileribtn').disabled = index === kartData.length - 1;
        
        if (isFlipped) {
            flashcard.classList.remove('flipped');
            isFlipped = false;
        }
    }
    
    document.getElementById('ileribtn').addEventListener('click', function() {
        if (currentIndex < kartData.length - 1) {
            currentIndex++;
            updateCard(currentIndex);
        }
    });
    
    document.getElementById('geribtn').addEventListener('click', function() {
        if (currentIndex > 0) {
            currentIndex--;
            updateCard(currentIndex);
        }
    });

    if (flashcard) {
        flashcard.addEventListener('click', function() {
            this.classList.toggle('flipped');
            isFlipped = !isFlipped;
        });
    }
    
    updateCard(currentIndex);
});