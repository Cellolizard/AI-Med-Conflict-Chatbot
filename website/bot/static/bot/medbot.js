$( document ).ready(function() {
    sessionStorage.clear();
    $("#copyrightYear").text(new Date().getFullYear());
    $('[data-toggle="popover"]').popover();
});
$('[data-toggle="popover"]').popover({
  gpuAcceleration: !(window.devicePixelRatio < 1.5 && /Win/.test(navigator.platform))
})
