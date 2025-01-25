// Логика переключения сезонов и эпизодов
document.querySelectorAll('.season-btn').forEach(button => {
    button.addEventListener('click', () => {
        const seasonId = button.getAttribute('data-season');

        // Удалить класс active у всех кнопок сезонов
        document.querySelectorAll('.season-btn').forEach(btn => btn.classList.remove('active'));

        // Добавить класс active к выбранной кнопке
        button.classList.add('active');

        // Скрыть все эпизоды
        document.querySelectorAll('.episodes').forEach(epContainer => {
            epContainer.style.display = 'none';
        });

        // Показать эпизоды выбранного сезона
        document.getElementById(`season-episodes-${seasonId}`).style.display = 'flex';
    });
});

// Функция загрузки эпизода
function loadEpisode(season, episode) {
    const url = new URL(window.location.href);
    url.searchParams.set('season', season); // Добавляем параметр сезона
    url.searchParams.set('episode', episode); // Добавляем параметр эпизода
    window.location.href = url.toString(); // Перезагружаем страницу с обновленным URL
}

// Автоматическая активация сезона и эпизода при загрузке страницы
window.onload = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const season = urlParams.get('season');
    const episode = urlParams.get('episode');

    // Если в URL есть параметры для сезона и эпизода, восстанавливаем их
    if (season) {
        // Активируем правильный сезон
        const seasonButton = document.querySelector(`.season-btn[data-season="${season}"]`);
        if (seasonButton) {
            seasonButton.classList.add('active');
            document.querySelectorAll('.episodes').forEach(epContainer => {
                epContainer.style.display = 'none';
            });
            document.getElementById(`season-episodes-${season}`).style.display = 'flex';
        }
    }

    if (episode) {
        // Активируем правильный эпизод
        const seasonEpisodes = document.getElementById(`season-episodes-${season}`);
        if (seasonEpisodes) {
            const episodeButton = seasonEpisodes.querySelector(`.episode-btn:nth-child(${episode})`);
            if (episodeButton) {
                episodeButton.classList.add('active'); // Добавляем класс active к эпизоду
            }
        }
    }
};

document.getElementById("translators").addEventListener("change", function () {
            const translatorId = this.value;
            const searchParams = new URLSearchParams(window.location.search);

            // Обновляем translator_id в URL
            searchParams.set('translator_id', translatorId);

            // Перезагрузка страницы с обновленными параметрами
            window.location.search = searchParams.toString();
        });

// Работа с плеером
// Инициализация Video.js
const player = videojs('video-1', {});


const button_watch = document.querySelector('.btn-watch');
if (button_watch) {
    button_watch.addEventListener('click', () => {
        // Запуск плеера
        player.play();

        // Перевод плеера в полноэкранный режим
        player.requestFullscreen.call(player);

    });
} else {
    console.error('Кнопка .btn-watch не найдена.');
}


// Добавляем обработчик для нажатий клавиш
document.addEventListener('keydown', (event) => {
    // Доступ к текущему времени видео
    const currentTime = player.currentTime();
    const skipStep = 5; // Шаг перемотки в секундах

    switch (event.code) {
        case 'ArrowRight': // Перемотка вперед
            player.currentTime(currentTime + skipStep);
            break;
        case 'ArrowLeft': // Перемотка назад
            player.currentTime(Math.max(0, currentTime - skipStep)); // Не меньше 0
            break;
        case 'Space':
            if (player.paused()) {
                player.play();
            } else {
                player.pause();
            }
            break;
        default:
            break;
    }
})


