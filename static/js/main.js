// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Handle form submissions with fetch API
    document.querySelectorAll('.attempt-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form)
                });
                
                if (response.ok) {
                    window.location.reload();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });
    
    // Optional: Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === '/') {
            e.preventDefault();
            document.querySelector('.search input').focus();
        }
    });
});



function showButtonFeedback(form) {
    const button = form.querySelector('.submit-btn');
    const originalText = button.textContent;

    // Add success class and change text
    button.classList.add('success');
    button.textContent = 'Logged!';

    // Reset after 2 seconds
    setTimeout(() => {
        button.classList.remove('success');
        button.textContent = originalText;
    }, 2000);
}

function renameList(slot, currentName) {
    const newName = prompt('Enter list name:', currentName);
    if (newName && newName.trim()) {
        fetch(`/rename_list/${slot}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `name=${encodeURIComponent(newName.trim())}`
        }).then(() => window.location.reload());
    }
}

function toggleList(problemId, slot) {
    fetch(`/toggle_list/${problemId}/${slot}`, {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            // Reload the page to reflect the accurate state
            window.location.reload();
        }
    }).catch(error => console.error('Error:', error));
}


// Add to main.js
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', e => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', e => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    const SWIPE_THRESHOLD = 50;
    const diff = touchEndX - touchStartX;

    if (Math.abs(diff) > SWIPE_THRESHOLD) {
        // Could implement swipe navigation between lists
        if (diff > 0) {
            // Swipe right - previous list
        } else {
            // Swipe left - next list
        }
    }
}

function toggleSection(sectionId) {
    const content = document.getElementById(sectionId);
    const header = content.previousElementSibling;
    const icon = header.querySelector('.collapse-icon');

    content.classList.toggle('collapsed');
    icon.textContent = content.classList.contains('collapsed') ? '▶' : '▼';
}