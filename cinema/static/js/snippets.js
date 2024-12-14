
const localStorageKey = userId !== "null" ? `bookmarks_${userId}` : null;

// Функция для сохранения состояния закладок
function updateBookmarkState(id, isActive) {
    if (!localStorageKey) {
        alert("Войдите в аккаунт, чтобы добавлять закладки!");
        return;
    }

        /* Чтение текущих данных из localStorage*/
    const bookmarks = JSON.parse(localStorage.getItem(localStorageKey)) || {};

    /* Обновление данных */
    bookmarks[id] = isActive;

    /* Сохранение данных обратно в localStorage */
    localStorage.setItem(localStorageKey, JSON.stringify(bookmarks));
}


// Функция для загрузки закладок
function loadBookmarks() {
    if (!localStorageKey) return; // Ничего не делаем для неавторизованных пользователей

    const bookmarks = JSON.parse(localStorage.getItem(localStorageKey)) || {};
    document.querySelectorAll('.bookmark').forEach(bookmark => {
        const movieId = bookmark.dataset.id;
        const icon = bookmark.querySelector('i');

        if (bookmarks[movieId]) {
            icon.classList.add('fa-solid');
            icon.classList.remove('fa-regular');
        } else {
            icon.classList.add('fa-regular');
            icon.classList.remove('fa-solid');
        }
    });
}

// Обработчик для кликов на закладках
document.querySelectorAll('.bookmark').forEach(bookmark => {
    bookmark.addEventListener('click', function () {
        const movieId = this.dataset.id;
        const icon = this.querySelector('i');

        // Если пользователь не авторизован
        if (!localStorageKey) {
            alert("Войдите в аккаунт, чтобы добавлять закладки!");
            return;
        }

        // Переключаем состояние и сохраняем
        const isActive = icon.classList.toggle('fa-solid');
        icon.classList.toggle('fa-regular', !isActive);
        updateBookmarkState(movieId, isActive);
    });
});

// Загрузка состояния закладок при загрузке страницы
document.addEventListener('DOMContentLoaded', loadBookmarks);






swiper = initializeSwiper();
// Модальное окно
let exampleModal = document.getElementById('exampleModal');

if (exampleModal) {
    exampleModal.addEventListener('show.bs.modal', event => {
        const button = event.relatedTarget;
        const recipient = button.getAttribute('data-bs-whatever');
        const authorName = button.getAttribute('data-bs-name');

        const modalTitle = exampleModal.querySelector('.modal-title');
        const modalBody = exampleModal.querySelector('.modal-body');

        modalTitle.textContent = `Комментарий от ${authorName}`;
        modalBody.textContent = recipient;
    });

    exampleModal.addEventListener('hidden.bs.modal', () => {
        swiper.destroy(true, true); // Уничтожаем текущий экземпляр
        swiper = initializeSwiper(); // Создаем новый экземпляр
        if (typeof currentSlideIndex !== 'undefined') {
            swiper.slideTo(currentSlideIndex, 0, false); // Возвращаемся на сохранённый слайд
        }
    });
}

