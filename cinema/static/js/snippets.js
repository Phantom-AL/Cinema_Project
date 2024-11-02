function setActiveLink(selectedLink) {
        // Убираем класс 'active' со всех ссылок
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Добавляем класс 'active' только к выбранной ссылке
        selectedLink.classList.add('active');
    }


const exampleModal = document.getElementById('exampleModal');
if (exampleModal) {
  exampleModal.addEventListener('show.bs.modal', event => {
    // Получаем кнопку, вызвавшую модальное окно
    const button = event.relatedTarget;
    // Извлекаем текст из data-bs-whatever
    const recipient = button.getAttribute('data-bs-whatever');
    const authorName = button.getAttribute('data-bs-name');

    // Обновляем текст только внутри модального окна
    const modalTitle = exampleModal.querySelector('.modal-title');
    const modalBody = exampleModal.querySelector('.modal-body');

    modalTitle.textContent = `Комментарий от ${authorName}`;
    modalBody.textContent = recipient;
  });
}
