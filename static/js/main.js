// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Handle form submissions with fetch API
    document.querySelectorAll('.attempt-form form').forEach(form => {
        console.log('Found attempt form:', form);
        form.addEventListener('submit', async function(e) {
            console.log('Form submitted');
            e.preventDefault();
            showButtonFeedback(form);  // Add button feedback

            try {
                console.log('Sending to:', form.action);
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
    const button = form.querySelector('.log-button');  // Changed from .submit-btn to .log-button
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

// Touch handling for mobile
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

let touchTimer;
const LONG_PRESS_DURATION = 500; // ms

function handleTouchStart(event, slot, name) {
    touchTimer = setTimeout(() => {
        renameList(slot, name);
    }, LONG_PRESS_DURATION);
}

function handleTouchEnd(event) {
    clearTimeout(touchTimer);
}

// Modern rename list modal functionality
function renameList(slot, currentName) {
    // Create a modern-looking modal instead of using prompt()
    const modal = document.createElement('div');
    modal.className = 'rename-modal';
    modal.innerHTML = `
        <div class="rename-modal-content">
            <input type="text" value="${currentName}" class="rename-input" autofocus>
            <div class="rename-modal-footer">
                <button onclick="closeRenameModal()" class="cancel-btn">Cancel</button>
                <button onclick="saveNewName(${slot})" class="save-btn">Save</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    const input = modal.querySelector('input');
    input.select();

    // Handle Enter key
    input.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') saveNewName(slot);
        if (e.key === 'Escape') closeRenameModal();
    });
}

function closeRenameModal() {
    document.querySelector('.rename-modal').remove();
}

function saveNewName(slot) {
    const newName = document.querySelector('.rename-input').value.trim();
    if (newName) {
        fetch(`/rename_list/${slot}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `name=${encodeURIComponent(newName)}`
        }).then(() => window.location.reload());
    }
    closeRenameModal();
}