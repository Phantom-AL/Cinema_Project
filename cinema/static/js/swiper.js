new Swiper('.cinema-slider', {
    slidesPerView: 2,
    slidesPerGroup: 2,
    spaceBetween: 20,
    freeMode: true,


    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
    grabCursor: {
        boolean: true,
    },
    keyboard: {
        enabled: true,
        onlyInViewport: true,
        pageUpDown: true,

    },
    breakpoints: {
        // when window width is >= 320px
        320: {
            slidesPerView: 3.5,
            spaceBetween: 5,
            slidesPerGroup: 1,

        },
        500: {
            slidesPerView: 4.2,
            spaceBetween: 10,
            slidesPerGroup: 4,
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            }
        },
        768: {
            slidesPerView: 5.3,
            spaceBetween: 10,
            slidesPerGroup: 5,
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            }
        },
        1280: {
            slidesPerView: 6.4,
            spaceBetween: 14,
            slidesPerGroup: 6,



        },
        1500: {
            slidesPerView: 7.5,
            spaceBetween: 16,
            slidesPerGroup: 7,



        },


    }
});



function initializeSwiper() {
    return new Swiper('.reviews-swiper', {
        freeMode: true,
        slidesPerGroup: 1,
        grid: {
            fill: 'rows',
            rows: 2
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
            type: 'bullets',
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        grabCursor: true,
        keyboard: {
            enabled: true,
            onlyInViewport: true,
            pageUpDown: true,
        },
        breakpoints: {
            320: {
                slidesPerView: 1.4,
                /*spaceBetween: 3,*/
                slidesPerGroup: 1,
                grid: {
                    fill: 'rows',
                    rows: 2
                },
            },
            575: {
                slidesPerView: 1.6,
                /*spaceBetween: 3,*/
                slidesPerGroup: 1,
                grid: {
                    fill: 'rows',
                    rows: 2
                },
            },
            720: {
                slidesPerView: 2,
                /*spaceBetween: 5,*/
                slidesPerGroup: 1,
                grid: {
                    fill: 'rows',
                    rows: 2
                },
            },
            815: {
                slidesPerView: 2.2,

                grid: {
                    fill: 'rows',
                    rows: 2
                },
            },
            1065: {
                slidesPerView: 3,
                spaceBetween: 0,
                grid: {
                    fill: 'rows',
                    rows: 2
                },
            },
        },
        on: {
            slideChange: function () {
                currentSlideIndex = swiper.activeIndex; // Обновляем индекс при изменении слайда
            },
        },
    });
}


