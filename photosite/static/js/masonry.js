(() => {
    const grids = [...document.querySelectorAll('.masonry')];
    if (grids.length && getComputedStyle(grids[0]).gridTemplateRows !== 'masonry') {
        const mappedGrids = grids.map(grid => ({
            _el: grid,
            gap: parseFloat(getComputedStyle(grid).rowGap),
            items: [...grid.children]
                .filter(c => c.nodeType === 1)
                .map(e => e.tagName === "PICTURE" ? e.querySelector("img") || e : e),
        }));
        function layout() {
            mappedGrids.forEach(grid => {
                const columnCount = getComputedStyle(grid._el).gridTemplateColumns.split(' ').length;
                grid.items.forEach(c => c.style.removeProperty('margin-top'));
                if (columnCount > 1) {
                    requestAnimationFrame(() => {
                        grid.items.slice(columnCount).forEach((c, i) => {
                            const prev_fin = grid.items[i].getBoundingClientRect().bottom;
                            const curr_ini = c.getBoundingClientRect().top;
                            c.style.marginTop = `${prev_fin + grid.gap - curr_ini}px`;
                        });
                    });
                }
            });
        }
        addEventListener('load', e => {
            layout();
            let resizeDebounce;
            window.addEventListener('resize', () => {
                clearTimeout(resizeDebounce);
                resizeDebounce = setTimeout(layout, 100);
            }, false);
        }, false);
    }
})();
