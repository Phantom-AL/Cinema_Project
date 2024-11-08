let currentSlideIndex = 0; // Переменная для хранения текущего индекса слайда


let swiper = initializeSwiper();

// Модальное окно
const exampleModal = document.getElementById('exampleModal');

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
    swiper.destroy(true, true); // Уничтожаем текущий экземпляр Swiper
    swiper = initializeSwiper(); // Создаем новый экземпляр с тем же индексом
    swiper.slideTo(currentSlideIndex, 0, false); // Возвращаемся на сохраненный слайд
  });
}


