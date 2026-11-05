const slides = [].slice.call(
	fragmentElement.querySelectorAll('.tm-home-slider__slide')
);
const tabs = [].slice.call(
	fragmentElement.querySelectorAll('.tm-home-slider__tab')
);

let current = 0;
let intervalId = null;

function show(index) {
	current = index;

	slides.forEach((slide, slideIndex) => {
		slide.classList.toggle('is-active', slideIndex === index);
	});

	tabs.forEach((tab, tabIndex) => {
		tab.classList.toggle('is-active', tabIndex === index);
		tab.setAttribute('aria-selected', String(tabIndex === index));
	});
}

tabs.forEach((tab, index) => {
	tab.addEventListener('click', () => {
		clearInterval(intervalId);

		show(index);
	});
});

if (slides.length > 1 && layoutMode !== 'edit') {
	intervalId = setInterval(() => {
		if (!document.contains(fragmentElement)) {
			clearInterval(intervalId);

			return;
		}

		show((current + 1) % slides.length);
	}, 6000);
}
