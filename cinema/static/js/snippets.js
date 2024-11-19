
 // Объявляем как глобальную переменную
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






function toggleBookmark(element) {
    const card = element.closest(".my-card");
    const cardId = card.getAttribute("data-id");
    let bookmarks = JSON.parse(localStorage.getItem("bookmarks")) || [];

    if (bookmarks.includes(cardId)) {
        // Удаляем из закладок
        bookmarks = bookmarks.filter(id => id !== cardId);
        element.classList.remove("active");
        element.querySelector("i").classList.remove("fa-solid");
        element.querySelector("i").classList.add("fa-regular");
    } else {
        // Добавляем в закладки
        bookmarks.push(cardId);
        element.classList.add("active");
        element.querySelector("i").classList.remove("fa-regular");
        element.querySelector("i").classList.add("fa-solid");
    }

    // Сохраняем обновленный массив
    localStorage.setItem("bookmarks", JSON.stringify(bookmarks));
}





document.addEventListener("DOMContentLoaded", function () {
    const bookmarks = JSON.parse(localStorage.getItem("bookmarks")) || [];
    bookmarks.forEach((id) => {
        const card = document.querySelector(`.my-card[data-id="${id}"]`);
        if (card) {
            const bookmark = card.querySelector(".bookmark");
            bookmark.classList.add("active");
            const icon = bookmark.querySelector("i");
            icon.classList.remove("fa-regular");
            icon.classList.add("fa-solid");
        }
    });
});


