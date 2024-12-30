document.addEventListener('DOMContentLoaded', function() {
    // Form submissions
    document.querySelectorAll('.attempt-form form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            showButtonFeedback(form);
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form)
                });
                if (response.ok) window.location.reload();
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });

    // Load more functionality
    const loadMoreButton = document.getElementById('load-more');
    let currentPage = 1;

    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', async function() {
            currentPage += 1;
            const searchParams = new URLSearchParams(window.location.search);
            searchParams.set('page', currentPage);

            const response = await fetch(`/?${searchParams.toString()}`, {
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            });

            if (response.ok) {
                const html = await response.text();
                const problemsGrid = document.querySelector('.all-problems .problems-grid');
                problemsGrid.insertAdjacentHTML('beforeend', html);

                if (currentPage >= parseInt(loadMoreButton.dataset.totalPages)) {
                    loadMoreButton.style.display = 'none';
                }
            }
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === '/') {
            e.preventDefault();
            document.querySelector('.search input').focus();
        }
    });
});

function showButtonFeedback(form) {
    const button = form.querySelector('.log-button');
    const originalText = button.textContent;
    button.classList.add('success');
    button.textContent = 'Logged!';
    setTimeout(() => {
        button.classList.remove('success');
        button.textContent = originalText;
    }, 2000);
}

function toggleList(problemId, slot) {
    fetch(`/toggle_list/${problemId}/${slot}`, {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            window.location.reload();
        }
    }).catch(error => console.error('Error:', error));
}

// Touch handling
let touchStartX = 0;
let touchEndX = 0;
let touchTimer;
const LONG_PRESS_DURATION = 500;

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
        if (diff > 0) {
            // Swipe right - previous list
        } else {
            // Swipe left - next list
        }
    }
}

function handleTouchStart(event, slot, name) {
    touchTimer = setTimeout(() => {
        renameList(slot, name);
    }, LONG_PRESS_DURATION);
}

function handleTouchEnd(event) {
    clearTimeout(touchTimer);
}

function toggleSection(sectionId) {
    const content = document.getElementById(sectionId);
    const icon = content.parentElement.querySelector('.collapse-icon');
    content.classList.toggle('collapsed');
    icon.textContent = content.classList.contains('collapsed') ? '▶' : '▼';
}

function renameList(slot, currentName) {
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


function updateSort(direction) {
    const searchParams = new URLSearchParams(window.location.search);
    const currentSort = searchParams.get('difficulty_sort');

    if (currentSort === direction) {
        searchParams.delete('difficulty_sort');
    } else {
        searchParams.set('difficulty_sort', direction);
    }

    window.location.href = `/?${searchParams.toString()}`;
}