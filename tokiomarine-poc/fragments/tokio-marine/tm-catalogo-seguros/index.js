const filters = [].slice.call(
	fragmentElement.querySelectorAll('.tm-catalogo__filter')
);

filters.forEach((filter) => {
	filter.addEventListener('click', () => {
		const segmento = filter.dataset.segmento;

		filters.forEach((button) => {
			button.classList.toggle('is-active', button === filter);
			button.setAttribute('aria-pressed', String(button === filter));
		});

		fragmentElement
			.querySelectorAll('.tm-catalogo__categoria')
			.forEach((categoria) => {
				let visible = 0;

				categoria
					.querySelectorAll('.tm-catalogo__produto')
					.forEach((produto) => {
						const match =
							!segmento ||
							produto.dataset.segmentos.split('|').includes(segmento);

						produto.classList.toggle('is-hidden', !match);

						if (match) {
							visible++;
						}
					});

				categoria.classList.toggle('is-hidden', !visible);
			});
	});
});
