// Geometry of the delivered page; no test door is installed in the product.
(async () => {
    const frame = document.getElementById('bench');
    const report = {pages: 0, measurements: 0, widths: [375, 1280], themes: ['light', 'dark']};
    const wait = ms => new Promise(r => setTimeout(r, ms));
    function measure(label) {
        const d = frame.contentDocument;
        const readings = ['html', 'body', '#main', '#bar', '#verdict-head', '#chips'].map(s => {
            const e = d.querySelector(s);
            if (!e || !e.clientWidth) throw Error(label + ': missing visible ' + s);
            return {element: s, width: e.clientWidth, scroll: e.scrollWidth};
        });
        const wide = readings.filter(r => r.scroll > r.width);
        if (wide.length) throw Error(label + ': ' + JSON.stringify(wide));
        for (const chip of d.querySelectorAll('.chip')) {
            if (chip.scrollWidth > chip.clientWidth) throw Error(label + ': clipped answer ' + chip.textContent);
        }
        report.measurements++;
        return readings;
    }
    try {
        for (const page of pages) {
            frame.style.width = '375px';
            await new Promise((resolve, reject) => {
                frame.onload = resolve; frame.onerror = () => reject(Error('cannot load ' + page));
                frame.src = page;
            });
            const d = frame.contentDocument;
            let ready = false;
            for (let n = 0; n < 100; n++) {
                if (d.querySelector('#filelist .file.on') && d.querySelector('#chips .chip')) { ready = true; break; }
                await wait(50);
            }
            if (!ready) throw Error(page + ': bench did not finish opening');
            for (const width of report.widths) {
                frame.style.width = width + 'px';
                frame.contentWindow.dispatchEvent(new Event('resize'));
                for (const theme of report.themes) {
                    d.documentElement.setAttribute('data-theme', theme);
                    await wait(50);
                    if (frame.contentWindow.innerWidth !== width) throw Error('wrong viewport');
                    if (d.documentElement.getAttribute('data-theme') !== theme) throw Error(page + ': theme changed before measurement');
                    measure(page + ' ' + width + ' ' + theme);
                }
            }
            // Bare, Table, Full and Drawing share the same frame. Real view
            // buttons exercise its scrolling surfaces without forbidding them.
            if (page === '/playground/basics/') {
                frame.style.width = '375px';
                for (const button of d.querySelectorAll('#view-seg button')) {
                    if (button.hidden || button.disabled || frame.contentWindow.getComputedStyle(button).display === 'none') continue;
                    button.click(); await wait(100);
                    measure(page + ' 375 ' + button.textContent.trim());
                }
                // Restore the old no-wrap chip, on the same finished page.
                // It must escape its group; hiding the whole document's overflow
                // cannot fool the per-group measurements above.
                const style = d.createElement('style');
                style.textContent = '.chip{max-width:none;white-space:nowrap}';
                d.head.appendChild(style);
                let error = '';
                try { measure('old chip'); } catch (e) { error = e.message; }
                style.remove();
                if (!error) throw Error('old no-wrap answer was accepted');
                report.negative = {detected: true, error};
                measure(page + ' restored');
            }
            report.pages++;
        }
    } catch (e) { report.error = e.stack || String(e); }
    document.getElementById('width-report').textContent = JSON.stringify(report);
})();
