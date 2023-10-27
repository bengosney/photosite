interface GridItem {
    _el: HTMLElement;
    gap: number;
    items: HTMLElement[];
}

(() => {
    const grids: HTMLElement[] = [...document.querySelectorAll<HTMLElement>('.masonry')];

    if (grids.length && getComputedStyle(grids[0]).gridTemplateRows !== 'masonry') {
        const mappedGrids: GridItem[] = grids.map(grid => ({
            _el: grid,
            gap: parseFloat(getComputedStyle(grid).rowGap),
            items: ([...grid.children] as HTMLElement[])
                .filter(c => c.nodeType === 1)
                .map(e => e.tagName === "PICTURE" ? e.querySelector<HTMLElement>("img") || e : e),
        }));

        function layout() {
            mappedGrids.forEach(grid => {
                const columnCount = getComputedStyle(grid._el).gridTemplateColumns.split(' ').length;
                grid.items.forEach(c => c.style.removeProperty('margin-top'));

                if (columnCount > 1) {
                    requestAnimationFrame(() => {
                        grid.items.slice(columnCount).forEach((c, i) => {
                            const previous = grid.items[i].getBoundingClientRect().bottom;
                            const current = c.getBoundingClientRect().top;

                            c.style.marginTop = `${previous + grid.gap - current}px`;
                        });
                    })
                }
            });
        }

        addEventListener('load', e => {
            layout();
            let resizeDebounce;
            window.addEventListener('resize', () => {
                clearTimeout(resizeDebounce);
                resizeDebounce = setTimeout(layout, 100);
            }, false)
        }, false);
    }
})();
