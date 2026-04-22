function confirmAction(message) {
    return window.confirm(message);
}

document.addEventListener('DOMContentLoaded', function () {
    var flashes = document.querySelectorAll('.flash');
    flashes.forEach(function (el) {
        setTimeout(function () {
            el.style.transition = 'opacity .4s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 400);
        }, 6000);
    });
});
