const toggle = fragmentElement.querySelector('.tm-header__toggle');
const nav = fragmentElement.querySelector('.tm-header__nav');
const dropdownToggles = [].slice.call(
	fragmentElement.querySelectorAll('.tm-header__dropdown-toggle')
);

function closePanels(except) {
	dropdownToggles.forEach((button) => {
		if (button !== except) {
			button.setAttribute('aria-expanded', 'false');

			fragmentElement
				.querySelector(`[data-panel="${button.dataset.target}"]`)
				.classList.remove('is-open');
		}
	});
}

dropdownToggles.forEach((button) => {
	button.addEventListener('click', (event) => {
		event.stopPropagation();

		const panel = fragmentElement.querySelector(
			`[data-panel="${button.dataset.target}"]`
		);
		const open = !panel.classList.contains('is-open');

		closePanels(button);

		panel.classList.toggle('is-open', open);
		button.setAttribute('aria-expanded', String(open));
	});
});

if (toggle) {
	toggle.addEventListener('click', () => {
		const open = !nav.classList.contains('is-open');

		nav.classList.toggle('is-open', open);
		toggle.setAttribute('aria-expanded', String(open));
	});
}

document.addEventListener('click', (event) => {
	if (!fragmentElement.contains(event.target)) {
		closePanels();
	}
});

document.addEventListener('keydown', (event) => {
	if (event.key === 'Escape') {
		closePanels();
	}
});
